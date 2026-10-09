#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
 [自研工具] sync_projects.py
 用途：从 GitHub 拉取账号下全部公开仓库的最新指标，回写 data/projects.js 的仓库区，
       使个人主页的项目信息随仓库更新而自动保持同步
 适用场景：静态个人主页 / 作品集站点的项目数据同步（零第三方依赖，只用标准库）
 仓库链接：https://github.com/Garvin666/Garvin-s
============================================================================

用法
----
    python scripts/sync_projects.py              # 更新已收录仓库的自动字段
    python scripts/sync_projects.py --dry-run    # 只显示将要发生的变更，不写文件
    python scripts/sync_projects.py --add-new    # 同时收录尚未出现在页面上的新仓库
    python scripts/sync_projects.py --prune      # 移除 GitHub 上已不存在的条目
    python scripts/sync_projects.py --check      # 只校验数据完整性（CI 可用），不改动

凭据
----
    按 --token → 环境变量 GITHUB_TOKEN → GH_TOKEN → `gh auth token` 顺序自动解析。
    脚本不会打印、记录或写入任何凭据；匿名访问亦可运行（受 60 次/小时限流）。

设计要点
--------
    · 只重写 data/projects.js 中 @sync:begin 与 @sync:end 之间的仓库区，
      文件头注释、其余板块与格式完全不受影响。
    · 每个条目的 "auto" 区块为自动写入；zh / highlight / tags / featured
      等手工字段在同步时原样保留。
    · 抓不到数据时静默保留本地值，绝不把已有内容清空。
"""

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

# --------------------------------------------------------------------- 常量
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DATA_FILE = os.path.join(ROOT, 'data', 'projects.js')

BEGIN_ANCHOR = '@sync:begin'
END_ANCHOR = '@sync:end'
ITEM_INDENT = 6                                   # 仓库条目在文件中的基础缩进
ITEM_KEY_ORDER = ['name', 'url', 'featured', 'zh', 'highlight', 'tags', 'auto']
AUTO_KEY_ORDER = ['description', 'language', 'stars', 'forks', 'pushedAt', 'archived']
SYNCED_FIELDS = ['stars', 'pushedAt', 'language', 'description', 'archived']
TIMEOUT = 25


# ----------------------------------------------------------------- 基础工具
def log(tag, msg):
    print('[{0}] {1}'.format(tag, msg))


def js_str(value):
    """序列化为 JSON 字符串字面量（保证中文不转义）。"""
    return json.dumps('' if value is None else str(value), ensure_ascii=False)


def js_scalar(value):
    if value is None:
        return 'null'
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, (int, float)):
        return str(value)
    return js_str(value)


def js_value(value, indent):
    """序列化单个值：短标量数组内联，对象多行。"""
    pad = ' ' * indent
    if isinstance(value, list):
        return '[' + ', '.join(js_scalar(v) for v in value) + ']'
    if isinstance(value, dict):
        if not value:
            return '{}'
        lines = ['{']
        for k, v in value.items():
            lines.append(pad + '  ' + js_str(k) + ': ' + js_scalar(v) + ',')
        lines[-1] = lines[-1].rstrip(',')
        lines.append(pad + '}')
        return '\n'.join(lines)
    return js_scalar(value)


def dump_item(item, indent=ITEM_INDENT):
    """把一条仓库记录序列化为与数据文件同风格的文本块。"""
    pad = ' ' * indent
    keys = [k for k in ITEM_KEY_ORDER if k in item]
    keys += [k for k in item if k not in keys]
    lines = [pad + '{']
    for i, k in enumerate(keys):
        lines.append(pad + '  ' + js_str(k) + ': ' + js_value(item[k], indent + 2) + ',')
    lines[-1] = lines[-1].rstrip(',')
    lines.append(pad + '}')
    return '\n'.join(lines)


def strip_js_comments(text):
    """字符串感知地移除 JS 注释，使其余下部分成为合法 JSON。

    必须逐字符扫描，不能用正则了事：本文件含有大量 URL（https://api.github.com、
    https://github.com/...），朴素的 `//` 正则会把这些 URL 从中间截断，清洗后
    JSON 直接解析失败。区块注释同理——也不能删掉字符串里出现的 /*。

    策略：只在字符串之外识别注释；遇到 /* */ 用等量换行占位（保持行号可对），
    遇到 // 丢弃至行尾。转义字符（\\"）正确处理。
    """
    out, i, n = [], 0, len(text)
    in_str = False
    while i < n:
        ch = text[i]
        if in_str:
            out.append(ch)
            if ch == '\\' and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if ch == '"':
                in_str = False
            i += 1
            continue
        # JSON 字符串只可能是双引号；不跟踪单引号，避免把文案里的撇号误判为字符串起始
        if ch == '"':
            in_str = True
            out.append(ch)
            i += 1
            continue
        if ch == '/' and i + 1 < n and text[i + 1] == '*':
            j = text.find('*/', i + 2)
            seg = text[i:j + 2] if j >= 0 else text[i:]
            out.append('\n' * seg.count('\n'))
            i = (j + 2) if j >= 0 else n
            continue
        if ch == '/' and i + 1 < n and text[i + 1] == '/':
            j = text.find('\n', i)
            i = n if j < 0 else j
            continue
        out.append(ch)
        i += 1
    return ''.join(out)


def parse_site_data(text):
    """解析文件中的 window.SITE_DATA 对象（其为合法 JSON 字面量）。"""
    cleaned = strip_js_comments(text)
    idx = cleaned.find('window.SITE_DATA')
    if idx < 0:
        raise ValueError('未找到 window.SITE_DATA')
    start = cleaned.find('{', idx)
    if start < 0:
        raise ValueError('window.SITE_DATA 后未找到对象起始符')
    depth, in_str, escaped = 0, False, False
    for i in range(start, len(cleaned)):
        ch = cleaned[i]
        if in_str:
            if escaped:
                escaped = False
            elif ch == '\\':
                escaped = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return json.loads(cleaned[start:i + 1])
    raise ValueError('未找到 window.SITE_DATA 对象的结束位置')


def find_region(text):
    """返回 (区域起始下标, 区域结束下标)，区域为两个锚点之间。"""
    b = text.find(BEGIN_ANCHOR)
    e = text.find(END_ANCHOR)
    if b < 0 or e < 0 or e < b:
        raise ValueError('未找到 @sync:begin / @sync:end 锚点，无法安全同步')
    line_start = text.rfind('\n', 0, b) + 1
    end_line_start = text.rfind('\n', 0, e) + 1
    return line_start, end_line_start


def parse_region(text):
    """解析仓库区内的现有条目列表。"""
    b, e = find_region(text)
    body = strip_js_comments(text[b:e]).strip()
    body = body.strip()
    if body.endswith(','):
        body = body[:-1]
    if not body:
        return []
    return json.loads('[' + body + ']')


# ------------------------------------------------------------------- 凭据
def resolve_token(explicit=None):
    if explicit:
        return explicit
    for env in ('GITHUB_TOKEN', 'GH_TOKEN'):
        v = os.environ.get(env)
        if v:
            return v.strip()
    try:
        out = subprocess.run(['gh', 'auth', 'token'], capture_output=True,
                             text=True, timeout=6)
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except Exception:
        pass
    return None


# ------------------------------------------------------------------- 取数
def fetch_repos(user, api_base, token):
    repos, page = [], 1
    while True:
        url = '{0}/users/{1}/repos?per_page=100&sort=pushed&page={2}'.format(api_base, user, page)
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'garvin-sync-projects')
        req.add_header('Accept', 'application/vnd.github+json')
        if token:
            req.add_header('Authorization', 'Bearer ' + token)
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                batch = json.loads(resp.read().decode('utf-8'))
        except urllib.error.HTTPError as ex:
            if ex.code in (403, 429):
                raise SystemExit('[!!] GitHub 返回 {0}：可能触发限流。请稍后重试，'
                                 '或设置 GITHUB_TOKEN 提高限额。'.format(ex.code))
            raise SystemExit('[!!] GitHub 请求失败：HTTP {0}'.format(ex.code))
        except urllib.error.URLError as ex:
            raise SystemExit('[!!] 网络不可达：{0}'.format(ex.reason))
        if not isinstance(batch, list) or not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return [r for r in repos if not r.get('fork')]


def to_auto(repo):
    return {
        'description': repo.get('description') or '',
        'language': repo.get('language') or '',
        'stars': int(repo.get('stargazers_count') or 0),
        'forks': int(repo.get('forks_count') or 0),
        'pushedAt': str(repo.get('pushed_at') or '')[:10],
        'archived': bool(repo.get('archived') or False),
    }


def diff_auto(old, new):
    changes = []
    if not isinstance(old, dict):
        return [('*', '(新建)', '已同步')]
    for k in SYNCED_FIELDS:
        if k not in new:
            continue
        a, b = old.get(k), new.get(k)
        if k == 'description':
            if b and a != b:
                changes.append((k, '(原描述)', b))
            continue
        if a != b:
            changes.append((k, a, b))
    return changes


# ------------------------------------------------------------------- 主流程
def main():
    ap = argparse.ArgumentParser(
        description='同步 GitHub 仓库信息到 data/projects.js',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--file', default=DEFAULT_DATA_FILE, help='数据文件路径')
    ap.add_argument('--token', default=None, help='GitHub 令牌（缺省读环境变量）')
    ap.add_argument('--user', default=None, help='覆盖 GitHub 用户名')
    ap.add_argument('--dry-run', '-n', action='store_true', help='只显示变更，不写文件')
    ap.add_argument('--add-new', action='store_true', help='收录未出现在页面上的新仓库')
    ap.add_argument('--prune', action='store_true', help='移除远端已不存在的条目')
    ap.add_argument('--check', action='store_true', help='只校验数据完整性，不改动')
    args = ap.parse_args()

    path = os.path.abspath(args.file)
    if not os.path.isfile(path):
        raise SystemExit('[!!] 数据文件不存在：{0}'.format(path))

    with open(path, 'r', encoding='utf-8', newline='') as fh:
        text = fh.read()
    # 行尾风格按「多数行」判定，而不是「只要出现一个 \r\n 就算 CRLF」：
    # 混合行尾的文件一旦被一律转成单一风格，反而会放大不一致。
    _crlf_n = text.count('\r\n')
    _lf_only = text.count('\n') - _crlf_n
    crlf = _crlf_n > _lf_only

    data = parse_site_data(text)
    items = parse_region(text)

    # ---------------------------------------------------------- 校验模式
    if args.check:
        problems = []
        for it in items:
            if not it.get('name'):
                problems.append('存在缺少 name 的条目')
            if not it.get('url'):
                problems.append('{0}: 缺少 url'.format(it.get('name', '?')))
            if not it.get('auto'):
                problems.append('{0}: 缺少 auto 区块'.format(it.get('name', '?')))
        if problems:
            for p in problems:
                log('!!', p)
            raise SystemExit(1)
        log('OK', '数据完整性校验通过：{0} 个仓库条目'.format(len(items)))
        return 0

    # ---------------------------------------------------------- 确定配置
    cfg = data.get('sync') or {}
    user = args.user or cfg.get('user')
    if not user:
        raise SystemExit('[!!] 未在数据文件的 sync.user 中配置 GitHub 用户名')
    api_base = cfg.get('apiBase') or 'https://api.github.com'

    token = resolve_token(args.token)
    log('INFO', '数据文件：{0}'.format(path))
    log('INFO', '账号：{0} | 凭据：{1}'.format(
        user, '已提供（长度 {0}）'.format(len(token)) if token else '无（匿名限流 60 次/小时）'))

    remote = fetch_repos(user, api_base, token)
    by_name = {r['name']: r for r in remote}
    log('INFO', '远端公开仓库：{0} 个'.format(len(by_name)))

    # ---------------------------------------------------------- 更新已有条目
    changes_total, touched, missing = 0, 0, []
    for it in items:
        name = it.get('name')
        repo = by_name.get(name)
        if not repo:
            missing.append(name)
            continue
        new_auto = to_auto(repo)
        old_auto = it.get('auto') if isinstance(it.get('auto'), dict) else {}
        # 远端未填写描述时，保留本地补充的说明，避免把已有内容清空
        if not new_auto.get('description') and old_auto.get('description'):
            new_auto['description'] = old_auto['description']
        ch = diff_auto(old_auto, new_auto)
        if ch:
            touched += 1
            changes_total += len(ch)
            log('UPD', '{0}'.format(name))
            for field, old_v, new_v in ch:
                log('   ', '  {0}: {1} -> {2}'.format(field, old_v, new_v))
        it['auto'] = new_auto

    # ---------------------------------------------------------- 新增 / 清理
    known = {it.get('name') for it in items}
    newcomers = [n for n in by_name if n not in known]
    if newcomers:
        if args.add_new:
            for n in sorted(newcomers):
                repo = by_name[n]
                items.append({
                    'name': n,
                    'url': repo.get('html_url') or 'https://github.com/{0}/{1}'.format(user, n),
                    'featured': False,
                    'zh': repo.get('description') or '（待补充中文说明）',
                    'highlight': '',
                    'tags': [repo.get('language')] if repo.get('language') else [],
                    'auto': to_auto(repo),
                })
                log('NEW', '已收录 {0}（暂用 GitHub 原文描述，建议改写成中文说明）'.format(n))
            changes_total += len(newcomers)
        else:
            log('NOTE', '发现 {0} 个未收录仓库：{1}'.format(len(newcomers), '、'.join(sorted(newcomers))))
            log('NOTE', '如需收录请加 --add-new 参数重新运行')

    if missing:
        if args.prune:
            items = [it for it in items if it.get('name') not in missing]
            log('DEL', '已移除远端不存在的条目：{0}'.format('、'.join(missing)))
            changes_total += len(missing)
        else:
            log('NOTE', '以下条目在远端已不存在（本次保留）：{0}'.format('、'.join(missing)))
            log('NOTE', '如需移除请加 --prune 参数重新运行')

    # ---------------------------------------------------------- 结果判定
    if not changes_total:
        log('OK', '已是最新，无需改动。')
        return 0

    if args.dry_run:
        log('DRY', '试运行模式：共 {0} 处变更未写入。去掉 --dry-run 即应用。'.format(changes_total))
        return 0

    # ---------------------------------------------------------- 回写文件
    new_region = '      /* ' + BEGIN_ANCHOR + ' —— 本区域由 scripts/sync_projects.py 维护：\n'
    new_region += ('         条目的 auto 区块为自动写入（会被覆盖），'
                   '其余手工字段（zh / highlight / tags / featured）永久保留。\n')
    new_region += '         请勿删除本锚点。 */\n'
    new_region += ',\n'.join(dump_item(it) for it in items)
    new_region += '\n'

    b, e = find_region(text)
    updated = text[:b] + new_region + text[e:]

    now = datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
    updated, n = re.subn(r'("lastSync"\s*:\s*")[^"]*(")',
                         lambda m: m.group(1) + now + m.group(2), updated, count=1)
    if n == 0:
        log('WARN', '未找到 meta.lastSync 字段，已跳过时间戳更新')

    if crlf:
        updated = updated.replace('\r\n', '\n').replace('\n', '\r\n')

    with open(path, 'w', encoding='utf-8', newline='') as fh:
        fh.write(updated)

    log('OK', '已写入 {0}（{1} 个条目，{2} 处变更，时间戳 {3}）'.format(path, len(items), changes_total, now))
    log('OK', '建议随后运行：python -m http.server 预览确认，再提交推送。')
    return 0


if __name__ == '__main__':
    sys.exit(main())

/* ============================================================================
 *  个人主页 · 全站唯一数据源（Single Source of Truth）
 * ----------------------------------------------------------------------------
 *  [自研工具] projects.js
 *  用途：集中承载主页全部可变内容，使页面无需改动 HTML 即可随仓库更新
 *  适用场景：静态个人主页 / 作品集站点的数据与展示分离
 *  仓库链接：https://github.com/Garvin666/Garvin-s
 * ----------------------------------------------------------------------------
 *  维护方式（三选一，任选其一即可）：
 *    1. 跑同步脚本 —— python scripts/sync_projects.py
 *       自动从 GitHub 拉取全部公开仓库的最新指标（星数 / 更新时间 / 语言 / 描述），
 *       ★ 只写入每个条目下的 "auto" 区块，其余手工字段绝不覆盖。
 *    2. 直接手改本文件 —— 增删项目、改文案，页面即时生效，无需构建。
 *    3. 新增站内 demo —— 把页面放进 demos/<名字>/ 并在 "demos" 数组追加一项。
 *
 *  字段分区约定（务必遵守，脚本依赖它保证不误伤手工内容）：
 *    "auto"  —— 由 sync_projects.py 自动写入，手工改动会在下次同步时被覆盖
 *    其余键  —— 手工维护，同步脚本永不触碰
 * ========================================================================== */

window.SITE_DATA = {

  /* ------------------------------------------------------------------ 元信息 */
  "meta": {
    "lastSync": "2026-09-25 09:29",
    "source": "github:Garvin666",
    "schemaVersion": 1,
    "note": "auto 区块由 scripts/sync_projects.py 自动维护；其余字段为手工内容。"
  },

  /* -------------------------------------------------------------- 站点与个人 */
  "site": {
    "name": "Garvin",
    "pageTitle": "Garvin · 数学 × 代码",
    "logo": "Garvin",
    "badge": "数学 · 代码 · 创造",
    "heroTitle": "你好，我是 Garvin",
    "heroHighlight": "Garvin",
    "tagline": "数学专业在读，习惯把复杂问题拆成可推演的步骤。<br>喜欢从数据到界面，把想法完整地做成能跑起来的东西。",
    "nav": [
      { "label": "关于", "href": "#about" },
      { "label": "技能", "href": "#skills" },
      { "label": "开源项目", "href": "#projects" },
      { "label": "作品", "href": "#demos" },
      { "label": "进行中", "href": "#private" },
      { "label": "联系", "href": "#contact" }
    ],
    "about": {
      "sub": "数学思维 + 工程执行力",
      /* avatar：相对路径指向一张本地图片（如 "assets/me.jpg"）。
         留空则回退到页面内置的 SVG 抽象头像 —— 换不换、换成什么由站主决定，
         这里不预置任何会让人误以为是真人的占位图。 */
      "avatar": "",
      /* now：首屏「近期在做」。留空数组 → 整块不渲染（而不是渲染一个空壳）。
         下列三条**逐条取自本文件里已经公开的同一份事实**（进行中项目与仓库描述），
         没有引入任何新表述；想换文案直接改这里，想整块隐藏就把数组清空。 */
      "now": [
        "量化分析平台 · 从数据到因子与策略研究的完整链路",
        "ai-workflow · 多阶段工作方法论与配套工具链",
        "底座模型调优 · 小样本风控，冻结底座 + 可训练 Adapter"
      ],
      /* timeline：经历 / 教育时间线。留空数组 → 整块不渲染。
         这是个人数据（学校、起止年份），**不做任何估算**，需要时按下面形状自行填写：
         [ { "when": "2024.09 – 2028.06", "what": "华南理工大学 · 数学类（强基计划）" } ] */
      "timeline": [],
      "paragraphs": [
        "我是 <strong>Garvin</strong>，数学专业在读。数学教给我最有用的一件事是——<br>任何复杂的问题都可以被拆解成可推演、可验证的步骤。这套方法我一直在代码里复用。",
        "目前的主要方向是 <strong>AI 应用开发</strong> 与 <strong>全栈工程</strong>：<br>从数据侧的分析与建模，到后端服务与前端交互，习惯把一个想法完整地做到能跑起来。",
        "同时在维护若干开源工具与个人项目，覆盖量化分析、工程自动化与学习系统。<br>数学背景让我在数据展示与工具型产品上有自己的判断。"
      ]
    },
    "contacts": [
      { "label": "Garvin666", "href": "https://github.com/Garvin666", "icon": "github" },
      { "label": "2671751728@qq.com", "href": "mailto:2671751728@qq.com", "icon": "mail" },
      { "label": "小红书", "href": "https://www.xiaohongshu.com/user/profile/26246095258", "icon": "book" }
    ],
    "contactForm": {
      /* 联系表单的投递方式。留空 = 组装一封真实邮件交给本机邮件客户端
         （零凭据、零第三方、不产生加载期外部请求）；填了 = POST 到该地址
         （Formspree / Web3Forms 这类服务都能直接吃表单编码）。
         收件地址**不在这里配** —— 它从上面 contacts 里的 mailto 记录取，
         同一个邮箱写两处迟早会漂移成两个值。 */
      "endpoint": "",
      "subject": "来自个人主页的留言"
    },
    "footer": "Built from scratch with ❤️"
  },

  /* -------------------------------------------------------------------- 技能 */
  "skills": {
    "sub": "按方向分组，不做熟练度评级",
    /* icon 取值为 index.html 内联 sprite 的名字（<use href="#i-xxx"> 去掉前缀 i-）；
       留空则该组不画图标，只显示标签。 */
    "groups": [
      { "label": "语言", "icon": "code", "items": ["Python", "JavaScript", "TypeScript", "SQL"] },
      { "label": "前端", "icon": "palette", "items": ["React", "Next.js", "Vite", "HTML / CSS"] },
      { "label": "后端与数据", "icon": "layers", "items": ["FastAPI", "Node.js", "Qlib", "DuckDB"] },
      { "label": "工具与数学基础", "icon": "sqrt", "items": ["Git", "LaTeX", "数学建模", "数据分析"] }
    ]
  },

  /* ------------------------------------------------- 开源仓库（脚本自动同步区） */
  "repos": {
    "title": "开源项目",
    "sub": "全部来自 GitHub 仓库 · 数据由同步脚本自动更新",
    "items": [
      /* @sync:begin —— 本区域由 scripts/sync_projects.py 维护：
         条目的 auto 区块为自动写入（会被覆盖），其余手工字段（zh / highlight / tags / featured）永久保留。
         请勿删除本锚点。 */
      {
        "name": "ai-workflow-skill",
        "url": "https://github.com/Garvin666/ai-workflow-skill",
        "featured": true,
        "zh": "一套标准化多阶段工作方法论的可复用实现：从入口分型、任务分层到计划先行与熔断门禁，并配套阶段感知的模型路由来控制推理成本。",
        "highlight": "含机器可校验的计划对账与门禁脚本",
        "tags": ["工作流编排", "方法论", "Python"],
        "auto": {
          "description": "ai-workflow skill: 阶段感知模型路由(--tier/--ledger) + 多阶段标准化工作流方法论",
          "language": "Python",
          "stars": 1,
          "forks": 0,
          "pushedAt": "2026-09-24",
          "archived": false
        }
      },
      {
        "name": "ai-workflow-tools",
        "url": "https://github.com/Garvin666/ai-workflow-tools",
        "featured": true,
        "zh": "工作流方法论中自研工具的公开留痕仓库，用于源码同步与版本一致性校验。",
        "highlight": "工具链与其方法论同源、版本可核对",
        "tags": ["工具链", "Python"],
        "auto": {
          "description": "ai-workflow 自研工具与技能的公开留痕仓库（源码同步 + 版本一致）",
          "language": "Python",
          "stars": 1,
          "forks": 0,
          "pushedAt": "2026-09-24",
          "archived": false
        }
      },
      {
        "name": "code-review-workbench",
        "url": "https://github.com/Garvin666/code-review-workbench",
        "featured": false,
        "zh": "代码审查工作台：把设计稿还原为可交互的 HTML 演示，并搭建配套的审查数据管道。",
        "highlight": "设计稿 → 可交互演示 → 数据管道的完整链路",
        "tags": ["HTML", "代码审查"],
        "auto": {
          "description": "代码审查工作台 · 设计稿还原 HTML 演示与审查数据管道 (review_pipeline)",
          "language": "HTML",
          "stars": 0,
          "forks": 0,
          "pushedAt": "2026-09-05",
          "archived": false
        }
      },
      {
        "name": "doc-impl-parity-audit",
        "url": "https://github.com/Garvin666/doc-impl-parity-audit",
        "featured": false,
        "zh": "文档与实现一致性审计工具：零第三方依赖，对中文文档友好，用于检出文档说明与代码行为之间的漂移。",
        "highlight": "零依赖，克隆即用",
        "tags": ["Python", "文档一致性"],
        "auto": {
          "description": "Document vs implementation parity audit (zero-dependency, Chinese-friendly)",
          "language": "Python",
          "stars": 0,
          "forks": 0,
          "pushedAt": "2026-09-15",
          "archived": false
        }
      },
      {
        "name": "Garvin-s",
        "url": "https://github.com/Garvin666/Garvin-s",
        "featured": false,
        "zh": "本站源码——数据结构驱动的个人主页。项目信息集中在一份数据文件中，可随仓库更新低成本维护。",
        "highlight": "数据与展示分离，改数据即改页面",
        "tags": ["HTML", "个人站点"],
        "auto": {
          "description": "个人作品集与主页站点（本页源码）",
          "language": "HTML",
          "stars": 0,
          "forks": 0,
          "pushedAt": "2026-07-23",
          "archived": false
        }
      }
      /* @sync:end */
    ]
  },

  /* ------------------------------------------------------------ 站内作品 Demo */
  "demos": {
    "title": "作品 Demo",
    "sub": "站内可直接打开的单页作品",
    "note": "href 写成显式的 index.html：GitHub Pages 与本地 file:// 两种打开方式下都能直接进入页面。",
    "items": [
      {
        "name": "Demo 01 · 餐厅站",
        "href": "demos/restaurant/index.html",
        "icon": "utensils",
        "preview": "restaurant",
        "tech": "HTML / CSS · 浅色暖调",
        "desc": "简洁菜单展示、营业信息与预约入口——为本地小商家设计的单页网站模板。",
        "status": "已上线",
        "statusType": "done"
      },
      {
        "name": "Demo 02 · 工作室站",
        "href": "demos/studio/index.html",
        "icon": "palette",
        "preview": "studio",
        "tech": "交互 · 响应式",
        "desc": "设计师 / 摄影师作品集模板：作品网格、方向筛选与详情弹层，缩略图由 CSS 渐变自绘，单文件零外部依赖。",
        "status": "已上线",
        "statusType": "done"
      },
      {
        "name": "数学工具站",
        "href": "demos/mathtools/index.html",
        "icon": "sqrt",
        "preview": "math",
        "tech": "Canvas · 数值计算",
        "desc": "函数绘图、矩阵运算、线性方程组与微积分四件套，自研表达式解析器，纯本地计算、零外部依赖。",
        "status": "已上线",
        "statusType": "done"
      }
    ]
  },

  /* -------------------------------------------------------- 进行中（未开源） */
  "privateProjects": {
    "title": "进行中的项目",
    "sub": "以下项目在本地开发中，暂未开源，因此不提供代码链接",
    "groups": [
      {
        "label": "量化与数据",
        "icon": "chart",
        "items": [
          {
            "name": "量化分析平台",
            "desc": "面向 A 股的量化分析与交易研究平台，覆盖数据获取、因子与策略研究的完整链路。",
            "stack": ["FastAPI", "Qlib", "React", "Vite"],
            "status": "运行中"
          },
          {
            "name": "数据分析前端",
            "desc": "量化与数据分析场景的可视化前端，配套单元测试保障交互与计算逻辑。",
            "stack": ["React", "Vite", "Vitest"],
            "status": "开发中"
          }
        ]
      },
      {
        "label": "AI 学习与教育",
        "icon": "graduation",
        "items": [
          {
            "name": "学习小助手",
            "desc": "面向数学专业的 AI 学习助教 Web 应用，含学习工作台、AI 辅导、刷题训练、报告生成与数字图书馆。",
            "stack": ["Next.js", "AI 应用"],
            "status": "开发中"
          },
          {
            "name": "AI 与计算机科学学习库",
            "desc": "基于 Obsidian 组织的 48 周学习任务体系，覆盖 AI 应用开发与大模型方向。",
            "stack": ["Obsidian", "知识体系"],
            "status": "持续更新"
          }
        ]
      },
      {
        "label": "工程与工具",
        "icon": "wrench",
        "items": [
          {
            "name": "求职助手",
            "desc": "求职双端平台，含求职端与企业端，并配套 V2 监控工作台跟踪运转状态。",
            "stack": ["FastAPI", "双端平台"],
            "status": "开发中"
          },
          {
            "name": "Agent 第二大脑",
            "desc": "面向智能体的三层共享记忆系统（高频 / 摘要 / 归档），供不同开发助手共用同一套长期记忆与读写纪律。",
            "stack": ["记忆架构", "Agent"],
            "status": "开发中"
          },
          {
            "name": "DSH 开发环境与插件",
            "desc": "日常开发环境的配置维护与插件体系，用于统一工具链与工作流。",
            "stack": ["工具链", "插件"],
            "status": "维护中"
          },
          {
            "name": "守护中枢",
            "desc": "文件完整性与站点状态监控服务，持续跟踪关键产物的变动与线上可达性。",
            "stack": ["监控", "服务"],
            "status": "运行中"
          }
        ]
      },
      {
        "label": "数学建模与模型研发",
        "icon": "flask",
        "items": [
          {
            "name": "数学建模项目集",
            "desc": "建模工作区中沉淀的多类赛题与模型实现，涵盖机器学习模型的训练与优化。",
            "stack": ["数学建模", "ML"],
            "status": "持续迭代"
          },
          {
            "name": "底座模型调优",
            "desc": "小样本风控场景下的模型升级调优，采用冻结底座 + 可训练 Adapter 的范式，兼顾效果与显存成本。",
            "stack": ["Adapter", "小样本"],
            "status": "研发中"
          }
        ]
      }
    ]
  },

  /* ------------------------------------------------------------ 运行时同步配置 */
  "sync": {
    "autoRefresh": true,
    "apiBase": "https://api.github.com",
    "user": "Garvin666",
    "refreshFields": ["stars", "pushedAt", "language", "description", "archived"]
  },

  /* -------------------------------------------------------------- UI 与交互配置
   * 页面表现层的开关与参数。想关掉某个效果，把对应项改成 false 即可，无需改 HTML。
   * 注意：无论这里怎么配，系统「减少动态效果」偏好（prefers-reduced-motion）始终优先。 */
  "ui": {
    "theme": "dark",
    "effects": {
      "aurora": true,          // 背景极光色团
      "grain": true,           // 颗粒质感叠加
      "mesh": true,            // 极淡网格背景
      "scrollProgress": true,  // 顶部滚动进度线
      "stagger": true,         // 卡片分段错开入场
      "spotlight": true,       // 卡片内鼠标光晕跟随
      "magnetic": true,        // 按钮磁性偏移
      "tilt": true,            // 卡片 3D 微倾
      "countUp": true,         // 数字滚动计数
      "viewTransitions": true  // 区块跳转视图过渡
    },
    "commandPalette": true,    // ⌘K / Ctrl+K 命令面板
    "repoFilter": true,        // 开源项目按语言筛选
    "repoSort": true,          // 开源项目排序（精选优先 / 最近更新 / Star）
    "repoLangBar": true,       // 开源项目语言构成条（章节头下方按占比的细色条）
    "contactCopy": true        // 联系方式的「复制」按钮（只对可复制的值出现）
  },

  /* ------------------------------------------------ Hero 数据条（数值自动派生）
   * source 指向数据源中的集合，数值由页面实时计算 —— 加仓库/加 demo 后自动跟随，
   * 无需手动改这里的数字。 */
  "heroStats": [
    { "label": "公开仓库", "source": "repos" },
    { "label": "站内作品", "source": "demos" },
    { "label": "进行中", "source": "private" }
  ]
};

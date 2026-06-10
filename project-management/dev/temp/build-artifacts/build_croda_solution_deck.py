from pathlib import Path

ROOT = Path("/Users/fangziying/Documents/trae_projects/claudecodeinstall/newsletter 字典")
TEMPLATE = Path("/Users/fangziying/.codex/skills/guizang-ppt-skill/assets/template-swiss.html")
OUT = ROOT / "outputs/禾大Croda/方案介绍PPT/style-b/index.html"

slides = r'''
<section class="slide accent" data-layout="S01" data-animate="hero">
  <div class="canvas-card">
    <canvas class="ascii-bg" aria-hidden="true"></canvas>
    <div class="chrome-min">
      <div class="l">Croda Beauty · Intelligence Workflow</div>
      <div class="r">Style B · 01 / 15</div>
    </div>
    <div style="flex:1;display:grid;grid-template-rows:auto 1fr auto;gap:2.6vh">
      <div data-anim="kicker" class="t-meta" style="color:rgba(255,255,255,.78);letter-spacing:.22em">SOLUTION DECK · 2026</div>
      <h1 data-anim="title" style="align-self:start;font-family:var(--sans),var(--sans-zh);font-weight:200;font-size:min(8.8vw,15.4vh);line-height:.96;letter-spacing:-.025em;color:#fff">
        月度情报<br/>报告应用方案
      </h1>
      <div data-anim="bottom" style="display:grid;grid-template-rows:auto auto;gap:1.6vh;border-top:1px solid rgba(255,255,255,.22);padding-top:2vh">
        <div class="lead" style="max-width:46ch;color:rgba(255,255,255,.86)">把行业信息转化为可行动的业务洞察</div>
        <div style="display:flex;justify-content:space-between;align-items:end">
          <div class="t-meta" style="color:rgba(255,255,255,.6)">Croda Beauty</div>
          <div class="t-meta" style="color:rgba(255,255,255,.6)">方案介绍</div>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="slide" data-layout="S12" data-animate="manifesto">
  <div class="canvas-card">
    <div class="chrome-min">
      <div class="l">Solution Goal</div>
      <div class="r">02 / 15</div>
    </div>
    <div data-anim="line" style="display:flex;flex-direction:column;gap:1.5vh">
      <div class="t-meta">方案目标</div>
      <h2 class="h-xl-zh" style="font-size:min(5.6vw,9.8vh);max-width:12em">从已验证的报告体验，走向系统化的月度情报工作流。</h2>
    </div>
    <div data-anim="up" style="margin-top:auto;display:grid;grid-template-columns:repeat(3,1fr);gap:1.4vw;border-top:1px solid var(--grey-2);padding-top:2.4vh">
      <div class="mini-cell"><div class="mini-num">01</div><div class="mini-title">更稳定地汇总<br/>每月行业信息</div></div>
      <div class="mini-cell accent"><div class="mini-num">02</div><div class="mini-title">更准确地识别<br/>新闻背后的业务信号</div></div>
      <div class="mini-cell"><div class="mini-num">03</div><div class="mini-title">更持续地沉淀<br/>Business Insight 与数据资产</div></div>
    </div>
  </div>
</section>

<section class="slide" data-layout="S19" data-animate="four-cards">
  <div class="canvas-card">
    <div class="chrome-min tight">
      <div class="l">Scenario Alignment</div>
      <div class="r">03 / 15</div>
    </div>
    <div data-anim="line" style="display:flex;flex-direction:column;gap:1.3vh;border-top:2px solid var(--accent);padding-top:2vh">
      <div class="t-meta">场景需求对齐</div>
      <h2 class="h-xl-zh" style="font-size:min(4.9vw,8.6vh)">关注的不是单篇新闻本身，而是新闻背后的业务含义。</h2>
    </div>
    <div data-anim="up" class="four-grid">
      <div class="four-card"><div class="four-n">01</div><h3>公司动作</h3><p>哪些公司正在推出新原料。</p></div>
      <div class="four-card"><div class="four-n">02</div><h3>品牌信号</h3><p>哪些品牌正在强化新的功效卖点。</p></div>
      <div class="four-card accent"><div class="four-n">03</div><h3>趋势形成</h3><p>哪些成分、技术和法规正在升温。</p></div>
      <div class="four-card"><div class="four-n">04</div><h3>业务关联</h3><p>哪些变化可能影响产品推广、研发方向和客户开发。</p></div>
    </div>
    <div data-anim="up" class="bottom-line">发生了什么 · 为什么重要 · 和业务有什么关系 · 下一步可以关注什么</div>
  </div>
</section>

<section class="slide" data-layout="S08" data-animate="duo-mirror">
  <div class="canvas-card">
    <div class="chrome-min">
      <div class="l">Prototype To Application</div>
      <div class="r">04 / 15</div>
    </div>
    <div data-anim="line" style="display:flex;flex-direction:column;gap:1.3vh">
      <div class="t-meta">从 prototype 到一期应用</div>
      <h2 class="h-xl-zh" style="font-size:min(5.2vw,9.2vh)">从体验对齐，走向价值沉淀。</h2>
    </div>
    <div data-anim="up" class="duo-compare" style="margin-top:5vh">
      <div class="col">
        <div class="col-tag"><span class="num">A</span> Prototype</div>
        <div class="col-ttl">看清报告<br/>应该如何被使用</div>
        <div class="col-desc">已验证阅读、筛选、展开、追溯原文和导出的最终体验。</div>
        <ul class="col-list"><li>对齐月报形态</li><li>对齐交互体验</li><li>对齐客户阅读习惯</li></ul>
      </div>
      <div class="vrule"></div>
      <div class="col accent">
        <div class="col-tag"><span class="num">B</span> Application</div>
        <div class="col-ttl">沉淀每篇新闻<br/>的商业价值</div>
        <div class="col-desc">通过事件、价值链、成分技术、功效宣称和公司维度组合，形成 Business Insight。</div>
        <ul class="col-list"><li>补齐数据结构与流程</li><li>沉淀多维标签资产</li><li>支持持续月度交付</li></ul>
      </div>
    </div>
  </div>
</section>

<section class="slide" data-layout="S16" data-animate="grid-reveal">
  <div class="canvas-card">
    <div class="chrome-min tight">
      <div class="l">Delivery Scope</div>
      <div class="r">05 / 15</div>
    </div>
    <div data-anim="line" style="display:flex;flex-direction:column;gap:1.3vh">
      <div class="t-meta">一期交付范围</div>
      <h2 class="h-xl-zh" style="font-size:min(5vw,8.8vh)">交付一套可运行的月度报告生产流程。</h2>
    </div>
    <div data-anim="up" class="sub-grid-3-2" style="margin-top:3.2vh">
      <div class="sub-card"><div class="nb-corner">01</div><div class="ttl">媒体源与关注名单配置</div><div class="desc">明确每月看哪些来源、公司和客户品牌。</div></div>
      <div class="sub-card"><div class="nb-corner">02</div><div class="ttl">月度文章整理与清洗</div><div class="desc">把原始信息整理成可分析的文章清单。</div></div>
      <div class="sub-card accent"><div class="nb-corner">03</div><div class="ttl">文章语义识别与标签输出</div><div class="desc">识别事件、技术、功效、价值链和相关公司。</div></div>
      <div class="sub-card"><div class="nb-corner">04</div><div class="ttl">报告内容结构化生成</div><div class="desc">将标签与文章组织为月报内容草案。</div></div>
      <div class="sub-card"><div class="nb-corner">05</div><div class="ttl">HTML 月报展示模板</div><div class="desc">形成可阅读、可筛选、可导出的交互式报告。</div></div>
      <div class="sub-card ink"><div class="nb-corner">06</div><div class="ttl">人工复核与质量确认机制</div><div class="desc">保留业务判断，支持持续优化。</div></div>
    </div>
  </div>
</section>

<section class="slide" data-layout="S05" data-animate="stack-build">
  <div class="canvas-card">
    <div class="chrome-min">
      <div class="l">Capability Architecture</div>
      <div class="r">06 / 15</div>
    </div>
    <div data-anim="line" style="display:flex;flex-direction:column;gap:1.3vh">
      <div class="t-meta">应用能力架构</div>
      <h2 class="h-xl-zh" style="font-size:min(5vw,8.8vh)">三层能力，让内容、口径与洞察持续复用。</h2>
    </div>
    <div data-anim="up" class="stack-row">
      <div class="stack-block b-grey"><div class="layer-nb">LAYER 01</div><div class="layer-ttl">数据层</div><div class="layer-desc">整理来源、文章、链接、时间、正文和原始记录。</div><div class="layer-tag">Source · Article · Content</div></div>
      <div class="stack-block b-accent"><div class="layer-nb">LAYER 02</div><div class="layer-ttl">标签层</div><div class="layer-desc">识别事件类型、价值链位置、成分技术、功效宣称和相关公司。</div><div class="layer-tag">Tag · Entity · Signal</div></div>
      <div class="stack-block b-ink"><div class="layer-nb">LAYER 03</div><div class="layer-ttl">报告层</div><div class="layer-desc">把结构化结果转化为月度报告内容，并渲染为 HTML 页面。</div><div class="layer-tag">Insight · Report · HTML</div></div>
    </div>
  </div>
</section>

<section class="slide" data-layout="S17" data-animate="system-diagram">
  <div class="canvas-card">
    <div class="chrome-min tight">
      <div class="l">Tagging To Report Flow</div>
      <div class="r">07 / 15</div>
    </div>
    <div data-anim="line" style="display:grid;grid-template-columns:7fr 5fr;gap:3vw;align-items:end">
      <div>
        <div class="t-meta">数据打标与报告生成流程</div>
        <h2 class="h-xl-zh" style="font-size:min(4.8vw,8.4vh);margin-top:1.2vh">从来源到月报，每一步都有明确产出。</h2>
      </div>
      <p class="t-body" style="color:var(--text-secondary)">流程既服务当月报告，也为后续数据资产沉淀保留结构。</p>
    </div>
    <div data-anim="up" class="flow-grid">
      <div class="flow-node source">RSS / 公众号 / 官网 / 人工补充</div>
      <div class="flow-arrow">→</div>
      <div class="flow-node">来源配置与关注名单匹配</div>
      <div class="flow-arrow">→</div>
      <div class="flow-node">文章抓取与基础字段整理</div>
      <div class="flow-node">当月干净文章清单</div>
      <div class="flow-arrow">→</div>
      <div class="flow-node accent">智能打标 Agent</div>
      <div class="flow-arrow">→</div>
      <div class="flow-node">文章标签与引用依据</div>
      <div class="flow-node">近月报告上下文</div>
      <div class="flow-arrow">→</div>
      <div class="flow-node accent">报告内容 Agent</div>
      <div class="flow-arrow">→</div>
      <div class="flow-node">结构化月报内容</div>
      <div class="flow-node">HTML 渲染模板</div>
      <div class="flow-arrow">→</div>
      <div class="flow-node ink">月度市场监测报告</div>
      <div class="flow-arrow">→</div>
      <div class="flow-node">业务审阅与下月优化</div>
    </div>
  </div>
</section>

<section class="slide" data-layout="S08" data-animate="duo-mirror">
  <div class="canvas-card">
    <div class="chrome-min">
      <div class="l">Deliverables And Quality Control</div>
      <div class="r">08 / 15</div>
    </div>
    <div data-anim="line" style="display:flex;flex-direction:column;gap:1.3vh">
      <div class="t-meta">核心交付物与质量控制</div>
      <h2 class="h-xl-zh" style="font-size:min(5vw,8.8vh)">区分客户可见成果与内部过程控制。</h2>
    </div>
    <div data-anim="up" class="duo-compare" style="margin-top:5vh">
      <div class="col accent">
        <div class="col-tag"><span class="num">01</span> Client Facing</div>
        <div class="col-ttl">客户侧核心交付物</div>
        <ul class="col-list"><li>月度 HTML 报告</li><li>结构化报告内容</li><li>标签字段字典</li><li>媒体源与关注名单配置</li><li>首期报告样例与调整建议</li></ul>
      </div>
      <div class="vrule"></div>
      <div class="col">
        <div class="col-tag"><span class="num">02</span> Internal Control</div>
        <div class="col-ttl">内部质量控制文件</div>
        <ul class="col-list"><li>原始抓取记录</li><li>运行日志</li><li>异常记录</li><li>复核记录</li><li>用于复查、定位和持续优化</li></ul>
      </div>
    </div>
  </div>
</section>

<section class="slide" data-layout="S13" data-animate="three-forces">
  <div class="canvas-card">
    <div class="chrome-min tight">
      <div class="l">Collaboration Model</div>
      <div class="r">09 / 15</div>
    </div>
    <div data-anim="line" style="display:grid;grid-template-columns:5fr 7fr;gap:2vw;flex:1;align-items:stretch">
      <div class="card-ink" style="padding:4vh 2.4vw;display:flex;flex-direction:column;justify-content:space-between">
        <div class="t-meta" style="color:rgba(255,255,255,.62)">团队协作中的应用位置</div>
        <h2 style="font-family:var(--sans),var(--sans-zh);font-size:min(5.6vw,9.8vh);line-height:1;letter-spacing:-.03em;font-weight:200;color:#fff">情报<br/>助理</h2>
        <p class="t-body" style="color:rgba(255,255,255,.82)">应用提升效率，业务团队保留判断权。</p>
      </div>
      <div data-anim="up" style="display:grid;grid-template-columns:repeat(3,1fr);gap:1.4vw">
        <div class="sub-card"><div class="nb-corner">A</div><div class="ttl">先整理</div><div class="desc">整理文章、补齐字段、识别标签。</div></div>
        <div class="sub-card accent"><div class="nb-corner">B</div><div class="ttl">再生成</div><div class="desc">记录引用依据，生成报告内容草案。</div></div>
        <div class="sub-card"><div class="nb-corner">C</div><div class="ttl">再确认</div><div class="desc">业务团队判断重要性、语境和建议是否适合进入报告。</div></div>
      </div>
    </div>
  </div>
</section>

<section class="slide" data-layout="S11" data-animate="timeline-walk">
  <div class="canvas-card">
    <div class="chrome-min">
      <div class="l">Monthly User Journey</div>
      <div class="r">10 / 15</div>
    </div>
    <div data-anim="line" style="display:flex;flex-direction:column;gap:1.3vh">
      <div class="t-meta">用户完成一次月报的路径</div>
      <h2 class="h-xl-zh" style="font-size:min(5vw,8.8vh)">从确认范围，到内部讨论。</h2>
    </div>
    <div data-anim="up" class="timeline-h">
      <div class="tl-row">
        <div class="th-node up"><div class="dot"></div><div class="label"><div class="yr">01</div><div class="name">确认周期与名单</div><div class="desc">月初确定本月关注范围</div></div></div>
        <div class="th-node down"><div class="dot"></div><div class="label"><div class="yr">02</div><div class="name">整理文章清单</div><div class="desc">形成可分析输入</div></div></div>
        <div class="th-node up accent"><div class="dot"></div><div class="label"><div class="yr">03</div><div class="name">识别标签</div><div class="desc">公司、事件、成分、技术、功效</div></div></div>
        <div class="th-node down"><div class="dot"></div><div class="label"><div class="yr">04</div><div class="name">审阅报告草案</div><div class="desc">确认洞察和行动建议</div></div></div>
        <div class="th-node up"><div class="dot"></div><div class="label"><div class="yr">05</div><div class="name">交付月报</div><div class="desc">阅读、筛选、导出、讨论</div></div></div>
      </div>
    </div>
  </div>
</section>

<section class="slide" data-layout="S18" data-animate="grid-reveal">
  <div class="canvas-card">
    <div class="chrome-min tight">
      <div class="l">Adaptive Workflow</div>
      <div class="r">11 / 15</div>
    </div>
    <div data-anim="line" style="display:flex;flex-direction:column;gap:1.3vh">
      <div class="t-meta">一套可以适应变化的工作流</div>
      <h2 class="h-xl-zh" style="font-size:min(5.2vw,9.2vh)">报告长期运行后，变化会持续发生。</h2>
    </div>
    <div data-anim="up" class="change-grid">
      <div>来源会变化</div><div>文章数量会变化</div><div>关注名单会变化</div><div>热门成分和功效会变化</div><div>报告重点也会变化</div>
    </div>
    <div data-anim="up" class="asset-strip">
      <span>来源资产</span><span>文章资产</span><span>标签资产</span><span>洞察资产</span><span>业务判断经验</span>
    </div>
  </div>
</section>

<section class="slide" data-layout="S08" data-animate="duo-mirror">
  <div class="canvas-card">
    <div class="chrome-min">
      <div class="l">Boundary And Review</div>
      <div class="r">12 / 15</div>
    </div>
    <div data-anim="line" style="display:flex;flex-direction:column;gap:1.3vh">
      <div class="t-meta">应用边界与人工确认</div>
      <h2 class="h-xl-zh" style="font-size:min(5vw,8.8vh)">减少重复整理，保留关键判断。</h2>
    </div>
    <div data-anim="up" class="duo-compare" style="margin-top:5vh">
      <div class="col">
        <div class="col-tag"><span class="num">AUTO</span> Application</div>
        <div class="col-ttl">系统提供材料、初步判断和结构化结果。</div>
        <ul class="col-list"><li>来源整理</li><li>文章结构化</li><li>标签识别</li><li>报告草案生成</li></ul>
      </div>
      <div class="vrule"></div>
      <div class="col accent">
        <div class="col-tag"><span class="num">REVIEW</span> Business Team</div>
        <div class="col-ttl">重要业务判断由团队最终确认。</div>
        <ul class="col-list"><li>来源无法访问或正文缺失</li><li>业务关系不明确</li><li>临时新增监测对象</li><li>栏目或表达重点需要调整</li><li>内容进入管理层汇报或对外使用</li></ul>
      </div>
    </div>
  </div>
</section>

<section class="slide" data-layout="S16" data-animate="grid-reveal">
  <div class="canvas-card">
    <div class="chrome-min tight">
      <div class="l">Future Applications</div>
      <div class="r">13 / 15</div>
    </div>
    <div data-anim="line" style="display:flex;flex-direction:column;gap:1.3vh">
      <div class="t-meta">后续应用展望</div>
      <h2 class="h-xl-zh" style="font-size:min(5vw,8.8vh)">从月报应用，延伸为业务 insight 数据资产。</h2>
    </div>
    <div data-anim="up" class="sub-grid-3-2 future-grid" style="margin-top:2.6vh">
      <div class="sub-card accent"><div class="nb-corner">01</div><div class="ttl">行业 Insight 数据库</div><div class="desc">沉淀文章、标签、公司动态、成分技术和月度洞察。</div></div>
      <div class="sub-card"><div class="nb-corner">02</div><div class="ttl">竞品与客户画像库</div><div class="desc">持续积累公司动作、技术路线、产品方向和市场信号。</div></div>
      <div class="sub-card"><div class="nb-corner">03</div><div class="ttl">成分与技术知识库</div><div class="desc">把重点技术主题沉淀为长期观察对象。</div></div>
      <div class="sub-card"><div class="nb-corner">04</div><div class="ttl">业务问答助手</div><div class="desc">支持团队直接询问竞品动作、成分升温原因和潜在合作机会。</div></div>
      <div class="sub-card ink"><div class="nb-corner">05</div><div class="ttl">长期趋势分析</div><div class="desc">从单月报告延伸到跨月、跨季度、跨年度洞察。</div></div>
      <div class="sub-card"><div class="nb-corner">06</div><div class="ttl">数据库化运营</div><div class="desc">将月度 JSON 工件接入后续 SQLite / 数据平台能力。</div></div>
    </div>
  </div>
</section>

<section class="slide" data-layout="S19" data-animate="four-cards">
  <div class="canvas-card">
    <div class="chrome-min tight">
      <div class="l">Client Alignment</div>
      <div class="r">14 / 15</div>
    </div>
    <div data-anim="line" style="display:flex;flex-direction:column;gap:1.3vh;border-top:2px solid var(--accent);padding-top:2vh">
      <div class="t-meta">本轮需要确认的内容</div>
      <h2 class="h-xl-zh" style="font-size:min(5vw,8.8vh)">对齐需求、标签与工作流。</h2>
    </div>
    <div data-anim="up" class="confirm-grid">
      <div class="confirm-card accent"><div class="confirm-num">01</div><h3>需求场景对齐</h3><p>五个核心报告板块是否覆盖当前业务需求。</p></div>
      <div class="confirm-card"><div class="confirm-num">02</div><h3>标签内容与报告标准</h3><p>分类和标签定义是否准确；报告产出标准是否与业务场景保持一致。</p></div>
      <div class="confirm-card ink"><div class="confirm-num">03</div><h3>工作流贴合度</h3><p>当前流程是否符合团队实际月报工作方式；哪些环节适合系统处理，哪些环节需要团队确认。</p></div>
    </div>
  </div>
</section>

<section class="slide split" data-layout="S10" data-animate="split-statement">
  <div class="canvas-card">
    <div class="split-half">
      <div class="half b-accent" style="padding:5.6vh 3.6vw 4.4vh;justify-content:space-between;position:relative;overflow:hidden">
        <canvas class="ascii-bg" aria-hidden="true"></canvas>
        <div class="chrome-min" style="margin-bottom:0;position:relative;z-index:1">
          <div class="l">15 / 15</div>
          <div class="r">Closing</div>
        </div>
        <div data-anim="manifesto" style="position:relative;z-index:1">
          <div class="t-meta" style="color:rgba(255,255,255,.78);letter-spacing:.22em;margin-bottom:1.8vh">FINAL NOTE</div>
          <h2 style="font-family:var(--sans),var(--sans-zh);font-size:min(7vw,12.4vh);line-height:.96;letter-spacing:-.025em;font-weight:200;color:#fff">从报告体验<br/>到洞察资产</h2>
        </div>
        <div class="t-meta" style="color:rgba(255,255,255,.62);border-top:1px solid rgba(255,255,255,.22);padding-top:2vh;position:relative;z-index:1">Croda Beauty · Intelligence Workflow</div>
      </div>
      <div class="half" style="padding:5.6vh 3.6vw 4.4vh;justify-content:center">
        <div data-anim="rules" style="display:flex;flex-direction:column;gap:2.6vh">
          <div class="t-meta">Closing</div>
          <h3 style="font-family:var(--sans),var(--sans-zh);font-weight:300;font-size:min(4vw,7vh);line-height:1.1;letter-spacing:-.02em;color:var(--text-primary)">让每月报告不只是信息汇总，<br/>而是持续服务业务判断的数据资产。</h3>
          <div class="rule accent" style="width:42%"></div>
          <p class="t-body" style="max-width:34ch;color:var(--text-secondary)">谢谢。</p>
        </div>
      </div>
    </div>
  </div>
</section>
'''

extra_css = r'''
  .mini-cell{border-top:1px solid var(--grey-2);padding:2vh 1.4vw 0;min-height:20vh}
  .mini-cell.accent{background:var(--accent);color:var(--accent-on);border-top-color:var(--accent);padding:2vh 1.4vw}
  .mini-num{font-family:var(--mono);font-size:14px;letter-spacing:.18em;color:var(--text-helper);margin-bottom:2.2vh}
  .mini-cell.accent .mini-num{color:rgba(255,255,255,.72)}
  .mini-title{font-family:var(--sans),var(--sans-zh);font-size:max(20px,2vw);line-height:1.2;font-weight:300;letter-spacing:-.02em}
  .four-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1.2vw;margin-top:4vh;flex:1}
  .four-card{background:var(--grey-1);padding:2.6vh 1.5vw;display:flex;flex-direction:column;gap:1.4vh}
  .four-card.accent{background:var(--accent);color:var(--accent-on)}
  .four-n{font-family:var(--mono);font-size:14px;letter-spacing:.18em;color:var(--text-helper)}
  .four-card.accent .four-n{color:rgba(255,255,255,.72)}
  .four-card h3{font-family:var(--sans),var(--sans-zh);font-size:max(20px,1.8vw);font-weight:400;line-height:1.2;letter-spacing:-.015em;margin-top:auto}
  .four-card p{font-family:var(--sans),var(--sans-zh);font-size:max(16px,.96vw);line-height:1.55;color:var(--text-secondary)}
  .four-card.accent p{color:rgba(255,255,255,.86)}
  .bottom-line{font-family:var(--mono);font-size:14px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);border-top:1px solid var(--grey-2);padding-top:1.5vh;margin-top:2vh}
  .flow-grid{display:grid;grid-template-columns:1.15fr auto 1fr auto 1.15fr;gap:1.1vh .8vw;margin-top:3.2vh;align-items:stretch}
  .flow-node{background:var(--grey-1);padding:1.8vh 1vw;font-family:var(--sans),var(--sans-zh);font-size:max(16px,.94vw);font-weight:500;line-height:1.35;display:flex;align-items:center;min-height:8vh}
  .flow-node.source{border-top:2px solid var(--ink)}
  .flow-node.accent{background:var(--accent);color:var(--accent-on)}
  .flow-node.ink{background:var(--ink);color:var(--paper)}
  .flow-arrow{font-family:var(--sans);font-weight:200;font-size:2.6vw;color:var(--accent);display:flex;align-items:center;justify-content:center}
  .change-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:1px;background:var(--grey-2);margin-top:5vh}
  .change-grid div{background:var(--paper);min-height:22vh;padding:2.4vh 1.2vw;display:flex;align-items:end;font-family:var(--sans),var(--sans-zh);font-size:max(18px,1.55vw);font-weight:300;line-height:1.2;letter-spacing:-.015em}
  .change-grid div:nth-child(3){background:var(--accent);color:var(--accent-on)}
  .asset-strip{margin-top:auto;display:grid;grid-template-columns:repeat(5,1fr);gap:0;border-top:2px solid var(--ink)}
  .asset-strip span{font-family:var(--mono);font-size:14px;letter-spacing:.12em;text-transform:uppercase;padding:1.8vh 1vw;border-left:1px solid var(--grey-2);color:var(--text-helper)}
  .asset-strip span:first-child{border-left:0}
  .confirm-grid{display:grid;grid-template-columns:1fr 1.3fr 1.15fr;gap:1.4vw;margin-top:5vh;flex:1}
  .confirm-card{background:var(--grey-1);padding:3vh 1.8vw;display:flex;flex-direction:column;justify-content:space-between}
  .confirm-card.accent{background:var(--accent);color:var(--accent-on)}
  .confirm-card.ink{background:var(--ink);color:var(--paper)}
  .confirm-num{font-family:var(--sans);font-weight:200;font-size:min(5vw,8.8vh);line-height:1;letter-spacing:-.04em}
  .confirm-card h3{font-family:var(--sans),var(--sans-zh);font-weight:400;font-size:max(22px,2.1vw);line-height:1.15;letter-spacing:-.02em}
  .confirm-card p{font-family:var(--sans),var(--sans-zh);font-size:max(16px,1vw);line-height:1.55;color:var(--text-secondary)}
  .confirm-card.accent p,.confirm-card.ink p{color:rgba(255,255,255,.84)}
  .future-grid{height:54vh;flex:0 0 54vh;gap:1.1vh 1.2vw}
  .future-grid .sub-card{padding:2vh 1.45vw 1.8vh}
  .future-grid .sub-card .ttl{font-size:max(17px,1.38vw)}
  .future-grid .sub-card .desc{font-size:max(16px,.88vw);line-height:1.45}
'''

html = TEMPLATE.read_text(encoding="utf-8")
html = html.replace("<title>[必填] 替换为 PPT 标题 · Deck Title</title>", "<title>禾大 Croda Beauty 月度情报报告应用方案</title>")
html = html.replace("</style>", extra_css + "\n</style>", 1)
start = html.index("<!-- ============================================================\n     SLIDES 插入区")
end = html.index("\n</div>\n\n<div id=\"nav\"></div>", start)
html = html[:start] + slides + html[end:]
html = html.replace("[必填]", "")
OUT.write_text(html, encoding="utf-8")
print(OUT)

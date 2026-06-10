from pathlib import Path


PPT = Path("/Users/fangziying/Documents/trae_projects/claudecodeinstall/croda-monthly-intel-ppt/index-v2.html")


def replace_between(text: str, start: str, end: str, replacement: str) -> str:
    s = text.index(start)
    e = text.index(end, s)
    return text[:s] + replacement.strip() + "\n\n" + text[e:]


def upsert_css(text: str, insert: str) -> str:
    marker = "  /* ===== V2 targeted client refinements ===== */"
    if marker in text:
        s = text.index(marker)
        e = text.index("</style>", s)
        return text[:s] + insert.rstrip() + "\n\n" + text[e:]
    marker = "</style>"
    i = text.index(marker)
    return text[:i] + insert.rstrip() + "\n\n" + text[i:]


css = r"""
  /* ===== V2 targeted client refinements ===== */
  .scenario-right-v2{height:100%;display:flex;flex-direction:column;gap:1.45vh}
  .scenario-question-grid-v2{flex:1;display:grid;grid-template-columns:1fr 1fr;gap:1vh 1vw;min-height:0}
  .scenario-q-v2{background:var(--paper);border-top:2px solid var(--ink);padding:1.75vh 1.15vw;display:flex;flex-direction:column;justify-content:space-between;gap:1.2vh}
  .scenario-q-v2.accent{background:var(--accent);border-top-color:var(--accent);color:var(--accent-on)}
  .scenario-q-v2 .num{font-family:var(--mono);font-size:max(10px,.68vw);letter-spacing:.18em;color:var(--text-helper)}
  .scenario-q-v2.accent .num{color:rgba(255,255,255,.72)}
  .scenario-q-v2 .question{font-family:var(--sans),var(--sans-zh);font-size:max(16px,1.24vw);line-height:1.26;font-weight:550;letter-spacing:0;color:inherit}
  .scenario-flow-v2{display:grid;grid-template-columns:1fr auto 1fr auto 1fr;gap:.8vw;align-items:center;border-top:1px solid var(--grey-2);padding-top:1.35vh}
  .scenario-flow-v2 .step{background:var(--paper);padding:1.15vh .95vw;font-family:var(--sans),var(--sans-zh);font-size:max(14px,.88vw);font-weight:650;line-height:1.35;text-align:center}
  .scenario-flow-v2 .step.accent{background:var(--accent);color:var(--accent-on)}
  .scenario-flow-v2 .arrow{font-family:var(--sans);font-size:min(2vw,3.6vh);font-weight:200;color:var(--accent);text-align:center}

  .proto-grid-v2{flex:1;min-height:0;display:grid;grid-template-columns:1fr 1fr;gap:1.6vw;margin-top:3vh}
  .proto-panel-v2{background:var(--grey-1);border-top:4px solid var(--ink);padding:2.8vh 2vw;display:flex;flex-direction:column;justify-content:space-between;gap:2.2vh}
  .proto-panel-v2.accent{background:var(--accent);border-top-color:var(--accent);color:var(--accent-on)}
  .proto-panel-v2 .label{font-family:var(--mono);font-size:max(10px,.72vw);letter-spacing:.16em;text-transform:uppercase;color:var(--text-helper)}
  .proto-panel-v2.accent .label{color:rgba(255,255,255,.72)}
  .proto-panel-v2 .title{font-family:var(--sans),var(--sans-zh);font-size:max(26px,2.1vw);font-weight:260;line-height:1.08;letter-spacing:-.015em}
  .proto-panel-v2 .desc{font-size:max(14px,.98vw);line-height:1.55;font-weight:300;color:var(--text)}
  .proto-panel-v2.accent .desc{color:rgba(255,255,255,.88)}
  .proto-list-v2{list-style:none;display:grid;grid-template-columns:1fr 1fr;gap:.9vh .9vw;margin-top:1vh}
  .proto-list-v2 li{border-top:1px solid var(--grey-2);padding-top:.9vh;font-size:max(13px,.86vw);line-height:1.35;font-weight:520}
  .proto-panel-v2.accent .proto-list-v2 li{border-top-color:rgba(255,255,255,.24)}

  .deliverable-table-v2{flex:1;min-height:0;display:grid;grid-template-columns:1fr 1fr;gap:1.8vw;margin-top:2.4vh;align-items:stretch}
  .deliverable-col-v2{display:grid;height:100%;border-top:3px solid rgba(255,255,255,.65)}
  .deliverable-client-v2{grid-template-rows:auto repeat(5,minmax(0,1fr))}
  .deliverable-qa-v2{grid-template-rows:auto repeat(4,minmax(0,1fr))}
  .deliverable-col-v2.accent{border-top-color:var(--accent-bright)}
  .deliverable-head-v2{display:flex;align-items:baseline;justify-content:space-between;gap:1vw;border-bottom:1px solid rgba(255,255,255,.2);padding:1.65vh 0}
  .deliverable-head-v2 .title{font-family:var(--sans),var(--sans-zh);font-size:max(22px,1.7vw);font-weight:260;line-height:1.1;color:#fff}
  .deliverable-head-v2 .meta{font-family:var(--mono);font-size:max(10px,.68vw);letter-spacing:.16em;color:rgba(255,255,255,.48)}
  .deliverable-row-v2{display:grid;grid-template-columns:9.5em 1fr;gap:1.1vw;padding:.5vh 0;border-bottom:1px solid rgba(255,255,255,.14);align-items:center}
  .deliverable-row-v2 .item{font-size:max(13px,.9vw);line-height:1.35;font-weight:650;color:#fff}
  .deliverable-row-v2 .use{font-size:max(12px,.82vw);line-height:1.5;font-weight:300;color:rgba(255,255,255,.68)}

  .resp-grid-v2{flex:1;min-height:0;display:grid;grid-template-columns:1fr 1fr;gap:1.7vw;margin-top:3vh}
  .resp-panel-v2{background:var(--grey-1);border-top:4px solid var(--ink);padding:2.6vh 2vw;display:flex;flex-direction:column;gap:1.8vh}
  .resp-panel-v2.accent{background:var(--accent);border-top-color:var(--accent);color:var(--accent-on)}
  .resp-panel-v2 .title{font-family:var(--sans),var(--sans-zh);font-size:max(24px,1.9vw);font-weight:260;line-height:1.1;letter-spacing:-.012em}
  .resp-list-v2{list-style:none;display:flex;flex-direction:column;gap:1vh}
  .resp-list-v2 li{display:grid;grid-template-columns:auto 1fr;gap:.9vw;align-items:baseline;font-size:max(14px,.94vw);line-height:1.45;font-weight:430}
  .resp-list-v2 li::before{content:"";width:.58em;height:1px;background:currentColor;opacity:.5;transform:translateY(-.25em)}
  .resp-summary-v2{margin-top:1.6vh;background:var(--ink);color:var(--paper);padding:1.4vh 1.5vw;display:flex;align-items:center;justify-content:space-between;gap:2vw}
  .resp-summary-v2 .main{font-family:var(--sans),var(--sans-zh);font-size:max(18px,1.35vw);font-weight:260;line-height:1.2}
  .resp-summary-v2 .sub{font-size:max(12px,.82vw);line-height:1.45;color:rgba(255,255,255,.66);text-align:right}

  .final-blue-v2,.final-blue-v2 .canvas-card{background:var(--accent);color:var(--accent-on)}
  .final-blue-v2 .canvas-card{position:relative;overflow:hidden}
  .final-slogan-v2{position:relative;z-index:1;flex:1;display:flex;flex-direction:column;justify-content:center;gap:2.2vh}
  .final-slogan-v2 h2{font-family:var(--sans),var(--sans-zh);font-weight:200;font-size:min(6.2vw,11vh);line-height:1.05;letter-spacing:-.025em;color:#fff;max-width:14em}
  .final-bottom-v2{position:relative;z-index:1;display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:rgba(255,255,255,.28);border-top:1px solid rgba(255,255,255,.32)}
  .final-mini-v2{background:rgba(0,47,167,.18);padding:1.65vh 1.3vw;color:#fff;display:flex;align-items:baseline;gap:.9vw}
  .final-mini-v2 .num{font-family:var(--mono);font-size:max(10px,.72vw);letter-spacing:.16em;color:rgba(255,255,255,.62)}
  .final-mini-v2 .txt{font-family:var(--sans),var(--sans-zh);font-size:max(16px,1.05vw);font-weight:520;line-height:1.25}
"""

p3 = r"""
<!-- ============ P3 · 场景需求对齐 · S03 Split Statement ============ -->
<section class="slide split" data-layout="S03" data-animate="statement">
  <div class="canvas-card">
    <div class="split-half">
      <div class="half b-ink" style="padding:5.6vh 3.4vw 4.4vh;justify-content:space-between">
        <div class="chrome-min" style="margin-bottom:0"><div class="l">SCENARIO · 场景需求</div><div class="r">03 / 15</div></div>
        <h2 style="font-family:var(--sans),var(--sans-zh);font-weight:200;font-size:min(3.4vw,6.4vh);line-height:1.16;letter-spacing:-.02em;color:#fff">我们关注的不是单篇新闻本身，<br/>而是新闻背后的<span style="font-style:italic;font-weight:300">业务含义</span>。</h2>
        <div class="t-meta" style="color:rgba(255,255,255,.55)">WHAT IT MEANS FOR THE BUSINESS</div>
      </div>
      <div class="half b-grey" style="padding:5.6vh 3.4vw 4.4vh;justify-content:space-between">
        <div class="scenario-right-v2">
          <div class="t-cat accent">我们关注什么</div>
          <div class="scenario-question-grid-v2">
            <div class="scenario-q-v2"><div class="num">Q01</div><div class="question">哪些公司正在推出新原料？</div></div>
            <div class="scenario-q-v2 accent"><div class="num">Q02</div><div class="question">哪些品牌正在强化新的功效卖点？</div></div>
            <div class="scenario-q-v2"><div class="num">Q03</div><div class="question">哪些成分、技术和法规正在形成趋势？</div></div>
            <div class="scenario-q-v2"><div class="num">Q04</div><div class="question">哪些变化可能影响推广、研发与客户开发？</div></div>
          </div>
          <div class="scenario-flow-v2">
            <div class="step">发生了什么</div>
            <div class="arrow">→</div>
            <div class="step accent">为什么重要</div>
            <div class="arrow">→</div>
            <div class="step">下一步关注什么</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>
"""

p4 = r"""
<!-- ============ P4 · 从 prototype 到一期 · S08 Duo Compare ============ -->
<section class="slide light" data-layout="S08" data-animate="duo-mirror">
  <div class="canvas-card">
    <div class="chrome-min"><div class="l">FROM PROTOTYPE TO V1 · 从原型到一期</div><div class="r">04 / 15</div></div>
    <div data-anim="line" style="display:flex;flex-direction:column;gap:1.2vh">
      <div class="t-cat accent">演进路径</div>
      <h2 style="font-family:var(--sans),var(--sans-zh);font-weight:200;font-size:min(4vw,6.8vh);line-height:1.04;letter-spacing:-.025em">已验证体验，补齐持续产出能力。</h2>
      <div class="lead" style="font-weight:300;max-width:72ch;opacity:.82">原型已经帮助我们看清报告应该如何被阅读和使用；一期应用在此基础上，把 Business Insight、标签体系与月度生产流程连接起来，让每篇新闻的商业意义可以被稳定识别和沉淀。</div>
    </div>
    <div class="proto-grid-v2" data-anim="up">
      <div class="proto-panel-v2">
        <div>
          <div class="label">PROTOTYPE · 已验证体验</div>
          <div class="title" style="margin-top:1.4vh">报告应该如何被使用</div>
          <div class="desc" style="margin-top:1.4vh">现有 HTML demo 已经很好地呈现了最终阅读体验：如何浏览、筛选、展开、追溯原文和导出。</div>
        </div>
        <ul class="proto-list-v2">
          <li>报告阅读体验</li><li>筛选与展开</li><li>原文追溯</li><li>一键导出</li>
        </ul>
      </div>
      <div class="proto-panel-v2 accent">
        <div>
          <div class="label">V1 · 补齐持续产出能力</div>
          <div class="title" style="margin-top:1.4vh">报告如何每月稳定生成</div>
          <div class="desc" style="margin-top:1.4vh">围绕月度场景补齐数据结构、标签口径与生产流程，让 Business Insight 与数据持续匹配，形成可复用的业务判断资产。</div>
        </div>
        <ul class="proto-list-v2">
          <li>月度数据结构</li><li>多层标签体系</li><li>商业价值识别</li><li>可持续产出流程</li>
        </ul>
      </div>
    </div>
  </div>
</section>
"""

p8 = r"""
<!-- ============ P8 · 核心交付物与质量控制 · S08 Duo Compare (dark) ============ -->
<section class="slide dark" data-layout="S08" data-animate="duo-mirror">
  <div class="canvas-card">
    <div class="chrome-min"><div class="l">DELIVERABLES & QA · 交付物与质量控制</div><div class="r">08 / 15</div></div>
    <div data-anim="line" style="display:flex;flex-direction:column;gap:1.2vh">
      <div class="t-cat accent">交付与质控</div>
      <h2 style="font-family:var(--sans),var(--sans-zh);font-weight:200;font-size:min(3.8vw,6.4vh);line-height:1.04;letter-spacing:-.025em">交付给客户的是报告体验，支撑报告的是一套质量机制。</h2>
    </div>
    <div class="deliverable-table-v2" data-anim="up">
      <div class="deliverable-col-v2 deliverable-client-v2 accent">
        <div class="deliverable-head-v2"><div class="title">客户交付物</div><div class="meta">5 ITEMS</div></div>
        <div class="deliverable-row-v2"><div class="item">月度 HTML 报告</div><div class="use">用于客户团队阅读、筛选、展开、讨论与导出。</div></div>
        <div class="deliverable-row-v2"><div class="item">结构化报告内容</div><div class="use">承载五大报告板块及每月核心洞察。</div></div>
        <div class="deliverable-row-v2"><div class="item">标签字段字典</div><div class="use">统一分类、标签定义与后续复用口径。</div></div>
        <div class="deliverable-row-v2"><div class="item">媒体源与关注名单配置</div><div class="use">明确监测范围，支持每月持续更新。</div></div>
        <div class="deliverable-row-v2"><div class="item">首期报告样例与调整建议</div><div class="use">帮助双方确认表达方式与业务重点。</div></div>
      </div>
      <div class="deliverable-col-v2 deliverable-qa-v2">
        <div class="deliverable-head-v2"><div class="title">内部质控</div><div class="meta">4 CONTROLS</div></div>
        <div class="deliverable-row-v2"><div class="item">原始抓取记录</div><div class="use">保留文章来源、时间与链接，便于复查。</div></div>
        <div class="deliverable-row-v2"><div class="item">运行过程记录</div><div class="use">跟踪每月处理过程，支持问题定位。</div></div>
        <div class="deliverable-row-v2"><div class="item">异常与补充记录</div><div class="use">标记正文缺失、来源异常或需人工补充的内容。</div></div>
        <div class="deliverable-row-v2"><div class="item">复核记录</div><div class="use">沉淀人工判断，持续优化标签与报告口径。</div></div>
      </div>
    </div>
  </div>
</section>
"""

p9 = r"""
<!-- ============ P9 · 团队协作中的应用位置 · S12 Responsibility Split ============ -->
<section class="slide light" data-layout="S12" data-animate="manifesto">
  <div class="canvas-card">
    <div class="chrome-min"><div class="l">TEAM COLLABORATION · 协作中的位置</div><div class="r">09 / 15</div></div>
    <div data-anim="line" style="display:flex;flex-direction:column;gap:1.2vh">
      <div class="t-cat accent">应用的角色</div>
      <h2 style="font-family:var(--sans),var(--sans-zh);font-weight:200;font-size:min(3.9vw,6.7vh);line-height:1.04;letter-spacing:-.025em">应用负责稳定生产，团队保留关键判断。</h2>
      <div class="lead" style="font-weight:300;max-width:68ch;opacity:.82">这套工作流把重复、结构化、可复用的环节交给应用处理，把真正需要业务语境的判断留给团队确认。</div>
    </div>
    <div class="resp-grid-v2" data-anim="up">
      <div class="resp-panel-v2 accent">
        <div class="title">应用负责什么</div>
        <ul class="resp-list-v2">
          <li>整理当月文章，形成干净的分析清单</li>
          <li>补齐来源、时间、公司、链接等基础字段</li>
          <li>识别事件、成分、功效、价值链位置等标签</li>
          <li>生成结构化报告草案和 HTML 阅读页面</li>
          <li>沉淀可复用的数据与标签口径</li>
        </ul>
      </div>
      <div class="resp-panel-v2">
        <div class="title">团队负责什么</div>
        <ul class="resp-list-v2">
          <li>判断哪些动态真正重要</li>
          <li>确认哪些洞察更贴近业务语境</li>
          <li>把报告重点对齐到当月业务关注</li>
          <li>决定哪些建议进入正式报告</li>
          <li>反馈标签与表达口径，推动下月优化</li>
        </ul>
      </div>
    </div>
    <div class="resp-summary-v2" data-anim="up">
      <div class="main">应用提升效率，业务团队保留判断权。</div>
      <div class="sub">让月报既能稳定产出，也能保持业务判断的温度与准确性。</div>
    </div>
  </div>
</section>
"""

p15 = r"""
<!-- ============ P15 · 结束页 · S09 Final Slogan · IKB full screen ============ -->
<section class="slide accent final-blue-v2" data-layout="S09" data-animate="manifesto">
  <div class="canvas-card">
    <canvas class="ascii-bg" aria-hidden="true"></canvas>
    <div class="chrome-min" style="position:relative;z-index:1"><div class="l">CLOSING</div><div class="r">15 / 15</div></div>
    <div class="final-slogan-v2" data-anim="line">
      <div class="t-meta" style="color:rgba(255,255,255,.74);letter-spacing:.22em">FINAL NOTE</div>
      <h2>把已验证的报告体验，<br/>升级为可沉淀洞察的工作流。</h2>
      <div style="width:28vw;height:1px;background:rgba(255,255,255,.45)"></div>
    </div>
    <div class="final-bottom-v2" data-anim="up">
      <div class="final-mini-v2"><span class="num">01</span><span class="txt">可持续产出</span></div>
      <div class="final-mini-v2"><span class="num">02</span><span class="txt">可沉淀价值</span></div>
      <div class="final-mini-v2"><span class="num">03</span><span class="txt">成为数据资产</span></div>
    </div>
  </div>
</section>
"""


html = PPT.read_text(encoding="utf-8")
html = upsert_css(html, css)
html = replace_between(html, "<!-- ============ P3", "<!-- ============ P4", p3)
html = replace_between(html, "<!-- ============ P4", "<!-- ============ P5", p4)
html = replace_between(html, "<!-- ============ P8", "<!-- ============ P9", p8)
html = replace_between(html, "<!-- ============ P9", "<!-- ============ P10", p9)
p15_start = "<!-- ============ 示例:最后一页" if "<!-- ============ 示例:最后一页" in html else "<!-- ============ P15"
html = replace_between(html, p15_start, "\n</div>\n\n<div id=\"nav\"></div>", p15 + "\n</div>\n\n<div id=\"nav\"></div>")

html = html.replace("""<!-- ============================================================
     SLIDES 插入区
     - 将下方示例 section 复制 / 替换为你的实际页面
     - 每页保留 class=\"slide\";使用 data-layout 标注模板
     ============================================================ -->

""", "")
if "<!-- ============================================================\n     SLIDES 插入区 ·" in html:
    s = html.index("<!-- ============================================================\n     SLIDES 插入区 ·")
    e = html.index("<!-- ============ P1", s)
    html = html[:s] + html[e:]

PPT.write_text(html, encoding="utf-8")
print(PPT)

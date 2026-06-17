#!/usr/bin/env python3
"""Config-driven renderer for the Croda Beauty monthly intelligence report demo.

Reads ``report_content.json`` and writes TWO self-contained HTML files:

  report-internal.html  内部调整版 — draft for the internal team to review and
                          request rewrites/deletes before publishing.
  report-final.html      最终展示版 — clean final report shown after adjustment.

The HTML owns only layout, interaction, brand visuals and link display; every
piece of business content comes from the JSON config (data / HTML separation).

Usage:
    python3 render_report.py            # report_content.json -> both html files
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "report_content.json"

TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Croda Beauty 市场监测月报</title>
<style>
:root{
  --primary:#16584C;--primary-dark:#0E3D34;--primary-mid:#1F6F5C;--leaf:#3E9A78;--sage:#8FBCA8;
  --gradient:linear-gradient(135deg,#0E3D34 0%,#1F6F5C 58%,#2E8B6F 100%);
  --bg:#F2F6F3;--card:#FFFFFF;--text:#1C2925;--text-secondary:#5B6C64;--muted:#8A998F;
  --border:#E1E8E3;--chip-bg:#EAF2EC;--shadow:0 1px 2px rgba(16,61,52,.05),0 6px 18px rgba(16,61,52,.06);
  --story-fg:#2C6E8F;--story-bg:#E6F0F5;--ingredient-fg:#2C7D58;--ingredient-bg:#E3F1E9;
  --claim-fg:#7250A6;--claim-bg:#EEE8F6;--application-fg:#AD6B22;--application-bg:#F6EEDD;
  --regulation-fg:#B04A45;--regulation-bg:#F6E6E5;--default-fg:#5B6C64;--default-bg:#EDF1EE;
  --amber-fg:#9a6b16;--amber-bg:#fde7cf;--amber-bd:#d8a23a;
}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:120px}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;
  background:var(--bg);color:var(--text);line-height:1.65;font-size:15px}
body.mode-internal{padding-bottom:64px}
a{color:var(--primary-mid);text-decoration:none}
a:hover{text-decoration:underline}

/* Mode banner */
.mode-banner{padding:7px 40px;font-size:.82em;text-align:center;font-weight:600;color:#fff}
.mode-internal .mode-banner{background:var(--amber-fg)}
.mode-final .mode-banner{display:none}

/* Header */
.report-header{background:var(--gradient);color:#fff;padding:42px 40px 36px;position:relative;overflow:hidden}
.report-header::before{content:'';position:absolute;top:-55%;right:-12%;width:560px;height:560px;
  background:radial-gradient(circle,rgba(255,255,255,.10) 0%,transparent 70%);border-radius:50%}
.report-header::after{content:'';position:absolute;bottom:-60%;left:-8%;width:420px;height:420px;
  background:radial-gradient(circle,rgba(143,188,168,.16) 0%,transparent 70%);border-radius:50%}
.header-inner{max-width:1180px;margin:0 auto;position:relative;z-index:1}
.header-top{display:flex;justify-content:space-between;align-items:flex-start;gap:20px;flex-wrap:wrap}
.report-header h1{font-size:2em;font-weight:700;letter-spacing:.5px;margin-bottom:6px}
.report-header .subtitle{font-size:1.05em;opacity:.9;margin-bottom:18px}
.report-header .meta{display:flex;gap:24px;flex-wrap:wrap;font-size:.86em;opacity:.9}
.report-header .meta span{display:flex;align-items:center;gap:6px}
.brand-badge{display:inline-flex;align-items:center;gap:8px;background:rgba(255,255,255,.14);
  border:1px solid rgba(255,255,255,.25);padding:6px 14px;border-radius:999px;font-size:.82em}
.lang-toggle{display:flex;background:rgba(255,255,255,.16);border-radius:999px;padding:3px;border:1px solid rgba(255,255,255,.25)}
.lang-toggle button{background:none;border:none;color:#fff;padding:5px 14px;border-radius:999px;cursor:pointer;font-size:.84em;opacity:.8}
.lang-toggle button.active{background:#fff;color:var(--primary-dark);opacity:1;font-weight:600}

/* Toolbar */
.toolbar{background:var(--card);border-bottom:1px solid var(--border);padding:10px 40px;position:sticky;top:0;z-index:200;
  display:flex;align-items:center;gap:14px;flex-wrap:wrap;box-shadow:0 2px 10px rgba(16,61,52,.05)}
.search-box{flex:1;min-width:220px;max-width:380px;padding:9px 14px;border:1px solid var(--border);border-radius:9px;
  font-size:.9em;outline:none;transition:border-color .2s,box-shadow .2s}
.search-box:focus{border-color:var(--leaf);box-shadow:0 0 0 3px rgba(62,154,120,.15)}
.toc-strip{display:flex;gap:6px;flex-wrap:wrap}
.toc-chip{padding:5px 12px;border:1px solid var(--border);border-radius:999px;background:#fff;font-size:.8em;
  color:var(--text-secondary);cursor:pointer;transition:all .18s;white-space:nowrap}
.toc-chip:hover{background:var(--chip-bg);border-color:var(--sage);color:var(--primary)}
.tool-spacer{flex:1}
.tool-btn{padding:8px 16px;border:1px solid var(--border);background:#fff;border-radius:9px;cursor:pointer;font-size:.86em;
  color:var(--text);transition:all .2s;display:inline-flex;align-items:center;gap:6px}
.tool-btn:hover{border-color:var(--leaf);color:var(--primary)}
.tool-btn.primary{background:var(--gradient);color:#fff;border:none}
.tool-btn.primary:hover{transform:translateY(-1px);box-shadow:0 4px 14px rgba(16,61,52,.28);color:#fff}

/* Tag cascade filter */
.filter-wrap{position:relative}
.filter-trigger{padding:8px 16px;border:1px solid var(--border);background:#fff;border-radius:9px;cursor:pointer;font-size:.86em;
  display:inline-flex;align-items:center;gap:6px;color:var(--text)}
.filter-trigger:hover,.filter-wrap.open .filter-trigger{border-color:var(--leaf);color:var(--primary)}
.filter-trigger .cnt{background:var(--leaf);color:#fff;border-radius:999px;font-size:.72em;padding:1px 7px;display:none}
.filter-trigger.has-active .cnt{display:inline-block}
.cascade{position:absolute;top:calc(100% + 8px);right:0;left:auto;display:none;background:#fff;border:1px solid var(--border);
  border-radius:12px;box-shadow:0 10px 34px rgba(16,61,52,.16);z-index:300;width:min(560px,calc(100vw - 36px))}
.filter-wrap.open .cascade,.filter-wrap:hover .cascade{display:flex}
.cascade-cats{width:200px;border-right:1px solid var(--border);padding:8px;flex-shrink:0}
.cascade-cat{padding:9px 12px;border-radius:8px;cursor:pointer;font-size:.88em;display:flex;align-items:center;
  justify-content:space-between;gap:8px;color:var(--text)}
.cascade-cat:hover,.cascade-cat.active{background:var(--chip-bg);color:var(--primary);font-weight:600}
.cascade-cat .dot{width:9px;height:9px;border-radius:3px;flex-shrink:0}
.cascade-cat .arrow{color:var(--muted);font-size:.8em}
.cascade-wrap2{display:flex;flex-direction:column;flex:1;min-width:0}
.cascade-fields{flex:1;padding:12px;max-height:340px;overflow:auto;display:flex;flex-wrap:wrap;gap:8px;align-content:flex-start}
.cascade-field{padding:6px 12px;border-radius:999px;font-size:.82em;cursor:pointer;border:1px solid transparent;user-select:none}
.cascade-field.on{box-shadow:inset 0 0 0 2px currentColor}
.cascade-foot{padding:8px 12px;border-top:1px solid var(--border);display:flex;justify-content:flex-end;align-items:center;font-size:.8em}
.af-clear{font-size:.8em;color:var(--text-secondary);cursor:pointer;text-decoration:underline}
.active-filters{display:flex;gap:8px;flex-wrap:wrap;padding:0 40px;margin-top:14px}
.active-filters:empty{display:none}
.af-chip{display:inline-flex;align-items:center;gap:6px;padding:4px 10px;border-radius:999px;font-size:.8em;cursor:pointer}
.af-chip .x{font-weight:700}

/* Container */
.container{max-width:1180px;margin:0 auto;padding:28px 40px 70px}

/* KPI — count auto-adapts to JSON via auto-fit grid */
.kpi-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:14px;margin-bottom:26px}
.kpi-card{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:18px 16px;position:relative;
  box-shadow:var(--shadow);transition:transform .18s,box-shadow .18s}
.kpi-card:hover{transform:translateY(-2px)}
.kpi-card.clickable{cursor:pointer}
.kpi-card.clickable:hover{box-shadow:0 8px 22px rgba(16,61,52,.12);border-color:var(--sage)}
.kpi-card.has-suggestion{border-color:var(--amber-bd);box-shadow:0 0 0 2px rgba(216,162,58,.35)}
.kpi-card::before{content:'';position:absolute;left:0;top:14px;bottom:14px;width:3px;border-radius:3px;background:var(--leaf)}
.kpi-top{position:absolute;top:9px;right:9px;display:flex;gap:6px;align-items:center}
.kpi-top .status-pill{margin-left:0}
.kpi-value{font-size:1.9em;font-weight:700;color:var(--primary);letter-spacing:-.5px}
.kpi-label{font-size:.8em;color:var(--text-secondary);margin-top:4px;line-height:1.4}
.kpi-jump{margin-top:9px;font-size:.72em;color:var(--primary-mid);font-weight:600}
.kpi-edit{border:1px solid var(--border);background:#fff;cursor:pointer;color:var(--text-secondary);font-size:.74em;
  padding:2px 7px;border-radius:7px;line-height:1.4}
.kpi-edit:hover{background:var(--chip-bg);color:var(--primary);border-color:var(--sage)}
.kpi-edit.active{background:var(--amber-bg);color:var(--amber-fg);border-color:var(--amber-bd)}

/* Section */
.section{margin-bottom:30px;scroll-margin-top:120px}
.section-header{display:flex;align-items:center;gap:14px;cursor:pointer;user-select:none;padding:15px 20px;background:var(--card);
  border-radius:13px;border:1px solid var(--border);box-shadow:var(--shadow);transition:box-shadow .2s}
.section-header:hover{box-shadow:0 6px 20px rgba(16,61,52,.10)}
.section-header .s-icon{width:42px;height:42px;border-radius:11px;display:flex;align-items:center;justify-content:center;
  font-size:1.25em;background:var(--gradient);color:#fff;flex-shrink:0}
.section-header h2{flex:1;font-size:1.2em;font-weight:650}
.section-header .s-sub{font-size:.78em;color:var(--text-secondary);font-weight:400;margin-top:2px;display:block}
.section-count{background:var(--chip-bg);color:var(--primary);border-radius:999px;padding:3px 11px;font-size:.78em;font-weight:600}
.toggle-icon{transition:transform .3s;color:var(--muted);font-size:.85em}
.section.collapsed .toggle-icon{transform:rotate(-90deg)}
.section-body{padding:18px 2px 2px}
.section.collapsed .section-body{display:none}
.group-label{font-size:.92em;font-weight:650;color:var(--primary-mid);margin:14px 0 12px;display:flex;align-items:center;gap:8px}
.group-label::before{content:'';width:4px;height:14px;background:var(--leaf);border-radius:2px}

/* Cards */
.card-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:14px}
.intel-card{background:var(--card);border:1px solid var(--border);border-radius:13px;padding:15px 17px;position:relative;
  box-shadow:var(--shadow);transition:transform .16s,box-shadow .16s}
.intel-card:hover{transform:translateY(-2px);box-shadow:0 8px 22px rgba(16,61,52,.10);border-color:var(--sage)}
.intel-card.has-suggestion{border-color:var(--amber-bd);box-shadow:0 0 0 2px rgba(216,162,58,.35)}
@keyframes flashhl{0%{box-shadow:0 0 0 3px rgba(62,154,120,.65)}100%{box-shadow:0 0 0 3px rgba(62,154,120,0)}}
.flash-hl{animation:flashhl 1.8s ease-out}
.card-meta{display:flex;align-items:center;gap:7px;flex-wrap:wrap;margin-bottom:9px}
.idx-badge{width:22px;height:22px;border-radius:7px;background:var(--primary);color:#fff;font-size:.74em;font-weight:700;
  display:flex;align-items:center;justify-content:center;flex-shrink:0}
.date-chip{font-size:.74em;color:var(--muted)}
.section-chip{font-size:.73em;padding:2px 9px;border-radius:999px;background:var(--chip-bg);color:var(--primary);font-weight:600;cursor:help}
.company-chip{font-size:.76em;padding:2px 9px;border-radius:6px;background:#eef2ef;color:var(--text);font-weight:600}
.region-chip{font-size:.73em;color:var(--text-secondary);border:1px solid var(--border);padding:1px 8px;border-radius:6px}
.status-pill{font-size:.7em;padding:2px 9px;border-radius:999px;margin-left:auto;font-weight:600}
.status-tobemod{background:var(--amber-bg);color:var(--amber-fg)}
.intel-card h3{font-size:.98em;font-weight:650;line-height:1.45;margin-bottom:7px}
.intel-card .summary{font-size:.85em;color:var(--text-secondary);margin-bottom:11px}
.tag-row{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px}
.tag{font-size:.74em;padding:2px 9px;border-radius:999px;cursor:help;font-weight:500;white-space:nowrap}
.tag-story{color:var(--story-fg);background:var(--story-bg)}
.tag-ingredient{color:var(--ingredient-fg);background:var(--ingredient-bg)}
.tag-claim{color:var(--claim-fg);background:var(--claim-bg)}
.tag-application{color:var(--application-fg);background:var(--application-bg)}
.tag-regulation{color:var(--regulation-fg);background:var(--regulation-bg)}
.tag-default{color:var(--default-fg);background:var(--default-bg)}
.card-foot{display:flex;align-items:center;gap:10px;flex-wrap:wrap;border-top:1px dashed var(--border);padding-top:9px;font-size:.78em}
.src-link{color:var(--primary-mid);display:inline-flex;align-items:baseline;gap:4px}
.edit-hot{margin-left:auto;border:1px solid var(--border);background:#fff;cursor:pointer;color:var(--text-secondary);
  font-size:.82em;padding:3px 10px;border-radius:8px;display:inline-flex;align-items:center;gap:4px;white-space:nowrap}
.edit-hot:hover{background:var(--chip-bg);color:var(--primary);border-color:var(--sage)}
.edit-hot.active{background:var(--amber-bg);color:var(--amber-fg);border-color:var(--amber-bd)}

/* Inline collapsible deep analysis on the card */
.deep{margin-bottom:11px;border:1px solid var(--border);border-radius:10px;overflow:hidden}
.deep-toggle{width:100%;text-align:left;background:#f3f7f4;border:none;padding:9px 12px;cursor:pointer;font-size:.82em;
  font-weight:650;color:var(--primary);display:flex;align-items:center;gap:7px}
.deep-toggle:hover{background:var(--chip-bg)}
.deep-toggle .chev{transition:transform .25s;font-size:.78em;color:var(--primary-mid)}
.deep.open .deep-toggle .chev{transform:rotate(90deg)}
.deep-body{padding:12px 13px;border-top:1px solid var(--border);background:#fbfdfc}
.deep:not(.open) .deep-body{display:none}
.ai-disclaimer{display:inline-flex;align-items:center;gap:5px;font-size:.7em;color:var(--amber-fg);background:var(--amber-bg);
  padding:2px 9px;border-radius:999px;margin-bottom:10px}
.an-block{margin-bottom:11px}
.an-block:last-child{margin-bottom:0}
.an-label{display:block;font-weight:700;color:var(--primary);font-size:.8em;margin-bottom:3px}
.an-text{font-size:.85em;line-height:1.66;color:var(--text)}

/* Appendix */
.src-group{margin-bottom:18px}
.src-group h4{font-size:.92em;color:var(--primary-mid);margin-bottom:9px}
.src-item{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:11px 15px;margin-bottom:8px;
  display:flex;gap:12px;align-items:flex-start;flex-wrap:wrap}
.src-item .s-title{font-weight:600;font-size:.9em;flex:1;min-width:200px}
.src-item .s-meta{font-size:.78em;color:var(--text-secondary);display:flex;gap:10px;flex-wrap:wrap;align-items:center}
.src-item .s-secs{display:flex;gap:5px;flex-wrap:wrap}
.src-item .s-sec{font-size:.72em;background:var(--chip-bg);color:var(--primary);padding:1px 8px;border-radius:999px;cursor:help}

/* Footer */
.report-footer{background:var(--primary-dark);color:rgba(255,255,255,.78);padding:26px 40px;text-align:center;font-size:.82em}
.report-footer strong{color:#fff}

/* Submit bar (internal only) — pinned to the bottom of the screen */
.submit-panel{position:fixed;left:0;right:0;bottom:0;z-index:250;background:#fff;border-top:1px solid var(--border);
  box-shadow:0 -4px 18px rgba(16,61,52,.12);padding:11px 40px;display:flex;align-items:center;gap:16px}
.submit-panel .sg-count{margin-right:auto;font-size:.9em;color:var(--text-secondary)}
.submit-panel .sg-count b{color:var(--amber-fg)}

/* Tooltip */
#tooltip{position:fixed;z-index:1200;max-width:300px;background:#1C2925;color:#fff;padding:10px 13px;border-radius:9px;
  font-size:.8em;line-height:1.5;box-shadow:0 8px 26px rgba(0,0,0,.28);display:none;pointer-events:none}
#tooltip .tt-title{font-weight:700;margin-bottom:3px;color:var(--sage)}

/* Modal */
.modal-overlay{position:fixed;inset:0;background:rgba(14,61,52,.45);backdrop-filter:blur(2px);display:none;z-index:900;
  align-items:center;justify-content:center;padding:20px}
.modal-overlay.open{display:flex}
.modal{background:#fff;border-radius:16px;max-width:580px;width:100%;max-height:84vh;overflow:auto;box-shadow:0 20px 60px rgba(0,0,0,.3)}
.modal-head{background:var(--gradient);color:#fff;padding:18px 56px 18px 22px;position:sticky;top:0;z-index:2}
.modal-head .m-sec{font-size:.78em;opacity:.85}
.modal-head h3{font-size:1.12em;margin-top:5px;line-height:1.4}
.modal-close{position:absolute;top:14px;right:14px;background:rgba(255,255,255,.28);border:1px solid rgba(255,255,255,.5);
  color:#fff;width:32px;height:32px;border-radius:50%;cursor:pointer;font-size:1.05em;line-height:1;display:flex;align-items:center;justify-content:center}
.modal-close:hover{background:rgba(255,255,255,.45)}
.modal-body{padding:22px 24px}
.modal-body .m-row{margin-bottom:16px}
.modal-body .m-k{font-size:.76em;text-transform:uppercase;letter-spacing:.5px;color:var(--muted);margin-bottom:5px}
.modal-body .m-detail{font-size:.92em;line-height:1.7}
.modal-src{background:var(--bg);border-radius:10px;padding:12px 14px;font-size:.86em}
.m-analysis .an-block{margin-bottom:12px}
.m-analysis .an-block:last-child{margin-bottom:0}
.m-analysis .an-label{display:block;font-weight:700;color:var(--primary);font-size:.82em;margin-bottom:3px}
.m-analysis .an-text{font-size:.9em;line-height:1.7;color:var(--text)}
.sg-list{list-style:none}
.sg-list li{border:1px solid var(--border);border-radius:10px;padding:11px 13px;margin-bottom:9px}
.sg-list .sg-t{font-weight:650;font-size:.9em;margin-bottom:4px}
.sg-list .sg-c{font-size:.86em;color:var(--text-secondary);margin-bottom:6px}
.sg-scope{display:inline-block;font-size:.72em;background:var(--chip-bg);color:var(--primary);padding:1px 9px;border-radius:999px}
.sg-scope.sg-kpi{background:var(--application-bg);color:var(--application-fg);margin-right:6px}
.done-box{text-align:center;padding:6px 0 2px}
.done-ico{font-size:2.2em;margin-bottom:6px}
.done-file{display:inline-block;background:var(--bg);border:1px solid var(--border);border-radius:8px;
  padding:6px 12px;font-size:.84em;margin:10px 0;font-family:ui-monospace,Menlo,monospace}
.done-steps{text-align:left;background:var(--bg);border-radius:10px;padding:14px 16px;font-size:.86em;line-height:1.8;margin-top:8px}

/* Inline rewrite panel in modal (internal) + floating popover (cards/KPIs) */
.m-sg textarea,.edit-pop textarea{width:100%;min-height:78px;border:1px solid var(--border);border-radius:9px;padding:9px 11px;
  font-size:.88em;font-family:inherit;resize:vertical;outline:none}
.m-sg textarea:focus,.edit-pop textarea:focus{border-color:var(--leaf);box-shadow:0 0 0 3px rgba(62,154,120,.15)}
.prefill-row{display:flex;flex-wrap:wrap;gap:14px;margin-bottom:8px}
.prefill{font-size:.78em;color:var(--primary-mid);cursor:pointer;text-decoration:underline;display:inline-block}
.ep-scope{display:flex;gap:12px;flex-wrap:wrap;margin-top:9px;font-size:.8em}
.ep-scope label{display:inline-flex;align-items:center;gap:4px;cursor:pointer;color:var(--text-secondary)}
.ep-row{display:flex;gap:8px;margin-top:10px}
.ep-row button{flex:1;border-radius:8px;padding:9px;cursor:pointer;font-size:.85em;border:1px solid var(--border);background:#fff;color:var(--text)}
.ep-row button.ep-save{background:var(--gradient);color:#fff;border:none;font-weight:600}
.ep-row button.ep-del{background:#fff;color:#b04a45;border-color:#e6c9c7}
.ep-note{font-size:.72em;color:var(--muted);margin-top:8px}
.edit-pop{position:fixed;z-index:1100;background:#fff;border:1px solid var(--border);border-radius:12px;
  box-shadow:0 12px 34px rgba(16,61,52,.2);padding:14px;display:none;width:320px;max-width:calc(100vw - 24px)}
.edit-pop .ep-title{font-size:.86em;font-weight:650;margin-bottom:3px}
.edit-pop .ep-sub{font-size:.78em;color:var(--text-secondary);margin-bottom:8px}

.no-results{text-align:center;padding:50px;color:var(--muted);display:none}

@media (max-width:768px){
  .mode-banner,.report-header,.toolbar,.container,.report-footer,.active-filters,.submit-panel{padding-left:18px;padding-right:18px}
  .report-header h1{font-size:1.5em}
  .header-top{flex-direction:column}
  .card-grid{grid-template-columns:1fr}
  .cascade{width:calc(100vw - 36px);flex-direction:column}
  .cascade-cats{width:auto;border-right:none;border-bottom:1px solid var(--border);display:flex;flex-wrap:wrap}
  .toc-strip{display:none}
}
@media print{
  .no-print{display:none !important}
  body{background:#fff}
  body.mode-internal{padding-bottom:0}
  .section.collapsed .section-body{display:block !important}
  .section,.intel-card,.src-item{break-inside:avoid}
  .report-header{padding:24px}
  #tooltip,.modal-overlay,.edit-pop,.submit-panel,.mode-banner{display:none !important}
  .edit-hot,.kpi-edit{display:none !important}
}
</style>
</head>
<body class="mode-__MODE__">
<div id="app"></div>
<div id="tooltip"></div>
<div class="modal-overlay" id="modal-overlay"><div class="modal" id="modal"></div></div>
<div class="edit-pop" id="edit-pop"></div>

<script id="report-data" type="application/json">__REPORT_DATA__</script>
<script>
const MODE='__MODE__';                 // 'internal' | 'final'
function boot(DATA){ try{ render(DATA); }catch(e){ document.getElementById('app').innerHTML='<p style="padding:40px">Render error: '+e.message+'</p>'; console.error(e);} }
(function(){
  const embedded=JSON.parse(document.getElementById('report-data').textContent);
  fetch('report_content.json').then(r=>r.ok?r.json():Promise.reject()).then(boot).catch(()=>boot(embedded));
})();

let DATA, lang='zh';
let glossaryById={}, sourceById={}, sectionById={}, categoryById={}, tagCategoryByTag={}, sgMeta={};
const activeFilters=new Set();
const suggestions={};   // key -> {text, scope:'both'|'zh'|'en'}  (internal mode; key = item_id or kpi_id)

function t(o){ if(o==null) return ''; if(typeof o==='string') return o; return o[lang]||o.zh||o.en||''; }
function esc(s){ return String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }
function cssEsc(s){ return (window.CSS&&CSS.escape)?CSS.escape(s):String(s).replace(/[^\w-]/g,'\\$&'); }
function tagLabel(tag){ const g=glossaryById[tag]; return g?t(g.display):tag; }
function tagClass(tag){ const c=tagCategoryByTag[tag]; return c?c.color_class:'tag-default'; }
function sectionName(id){ const s=sectionById[id]; return s?t(s.title):id; }
function L(zh,en){ return lang==='zh'?zh:en; }

function render(d){
  DATA=d; lang=d.language_default||'zh';
  glossaryById={}; (d.glossary||[]).forEach(g=>glossaryById[g.term_id]=g);
  sourceById={}; (d.source_links||[]).forEach(s=>sourceById[s.source_ref_id]=s);
  sectionById={}; (d.sections||[]).forEach(s=>sectionById[s.section_id]=s);
  categoryById={}; tagCategoryByTag={};
  (d.tag_taxonomy||[]).forEach(c=>{categoryById[c.category_id]=c; (c.tags||[]).forEach(tg=>tagCategoryByTag[tg]=c);});
  sgMeta={};
  (d.kpis||[]).forEach(k=>sgMeta[k.kpi_id]={type:'kpi',title:k.label});
  (d.sections||[]).forEach(s=>(s.items||[]).forEach(i=>sgMeta[i.item_id]={type:'item',title:i.title,sectionId:s.section_id}));
  draw();
}

function draw(){
  const d=DATA;
  document.documentElement.lang = lang==='zh'?'zh-CN':'en';
  document.getElementById('app').innerHTML =
    (MODE==='internal'?'<div class="mode-banner">'+L('内部调整版 · 供团队审阅与提交重写建议，提交后由报告 Agent 重新编写','Internal review version · for team review and rewrite requests; resubmitted to the report Agent')+'</div>':'')+
    headerHTML(d) + toolbarHTML(d) +
    '<div class="active-filters" id="active-filters"></div>' +
    '<main class="container">' +
      kpiHTML(d) +
      (d.sections||[]).map(sectionHTML).join('') +
      appendixHTML(d) +
      '<div class="no-results" id="no-results">'+L('没有匹配的内容，请调整搜索或筛选条件。','No matching content. Adjust your search or filters.')+'</div>' +
    '</main>' + footerHTML(d) +
    (MODE==='internal'?submitPanelHTML():'');
  bindEvents();
  renderActiveFilters();
  applyVisibility();
  if(MODE==='internal') reapplySuggestions();
}

function headerHTML(d){
  return '<header class="report-header"><div class="header-inner">'+
    '<div class="header-top"><div>'+
      '<h1>'+esc(t(d.title))+'</h1>'+
      '<div class="subtitle">'+esc(t({zh:d.period.display_zh,en:d.period.display_en}))+' · '+L('内部情报参考','Internal intelligence')+'</div>'+
      '<div class="meta">'+
        '<span>📅 '+esc(d.period.start||'')+' – '+esc(d.period.end||'')+'</span>'+
        '<span>🏢 '+esc(d.client||'Croda Beauty')+'</span>'+
        '<span>🔖 '+L('每月自动生成 · 双语','Auto-generated monthly · Bilingual')+'</span>'+
      '</div></div>'+
    '<div style="display:flex;flex-direction:column;gap:12px;align-items:flex-end">'+
      '<div class="brand-badge">🌿 Croda Beauty</div>'+
      '<div class="lang-toggle no-print">'+
        '<button data-lang="zh" class="'+(lang==='zh'?'active':'')+'">中文</button>'+
        '<button data-lang="en" class="'+(lang==='en'?'active':'')+'">English</button>'+
      '</div></div></div></div></header>';
}

function toolbarHTML(d){
  const toc=(d.sections||[]).map(s=>'<span class="toc-chip" data-jump="sec-'+s.section_id+'" data-term="'+s.section_id+'">'+esc(t(s.title))+'</span>').join('')+
    '<span class="toc-chip" data-jump="sec-appendix">'+L('原文链接','Sources')+'</span>';
  const cats=(d.tag_taxonomy||[]).map((c,i)=>{
    const color='var(--'+c.color_class.replace('tag-','')+'-fg)';
    return '<div class="cascade-cat'+(i===0?' active':'')+'" data-cat="'+c.category_id+'">'+
      '<span><span class="dot" style="background:'+color+'"></span> '+esc(t(c.display))+'</span><span class="arrow">▸</span></div>';
  }).join('');
  return '<nav class="toolbar no-print">'+
    '<input type="text" class="search-box" id="search" placeholder="'+L('🔍 搜索公司 / 成分 / 功效 / 栏目 / 来源 / 标签','🔍 Search company / ingredient / claim / section / source / tag')+'">'+
    '<div class="toc-strip">'+toc+'</div>'+
    '<div class="tool-spacer"></div>'+
    '<div class="filter-wrap" id="filter-wrap"><button class="filter-trigger" id="filter-trigger">🏷️ '+L('标签筛选','Tag filter')+' <span class="cnt" id="filter-cnt">0</span></button>'+
      '<div class="cascade"><div class="cascade-cats">'+cats+'</div>'+
      '<div class="cascade-wrap2"><div class="cascade-fields" id="cascade-fields"></div>'+
      '<div class="cascade-foot"><span class="af-clear" id="cascade-clear">'+L('清除','Clear')+'</span></div></div></div></div>'+
    '<button class="tool-btn" id="print-btn">🖨️ '+L('导出 PDF','Export PDF')+'</button></nav>';
}

function kpiTarget(k){ for(const sid of (k.source_ref_ids||[])){ const s=sourceById[sid]; if(s&&s.item_ids&&s.item_ids.length) return s.item_ids[0]; } return null; }
function kpiHTML(d){
  return '<div class="kpi-row">'+(d.kpis||[]).map(k=>{
    const tgt=kpiTarget(k);
    const edit=MODE==='internal'?'<button class="kpi-edit edit-hot no-print" title="'+L('建议修改该指标','Suggest a change to this KPI')+'">✏️</button>':'';
    return '<div class="kpi-card'+(tgt?' clickable':'')+'" data-sgkey="'+esc(k.kpi_id)+'"'+(tgt?' data-jump-item="'+esc(tgt)+'"':'')+'>'+
      (edit?'<div class="kpi-top">'+edit+'</div>':'')+
      '<div class="kpi-value">'+esc(k.value)+'</div>'+
      '<div class="kpi-label">'+esc(t(k.label))+'</div>'+
      (tgt?'<div class="kpi-jump">'+L('↘ 查看来源新闻','↘ View source story')+'</div>':'')+
      '</div>';
  }).join('')+'</div>';
}

const SEC_ICON={market_flash:'⚡',competitor_watch:'🎯',ingredient_innovation:'🧪',ka_watch:'👑',market_event:'📅',regulation_policy:'⚖️'};
function groupLabel(g,sid){
  const k=(g||'').toLowerCase();
  if(k==='mnc') return {zh:'🌍 跨国客户品牌 (MNC)',en:'🌍 MNC customer brands'};
  if(k==='international') return {zh:'🌐 国际原料商',en:'🌐 International suppliers'};
  if(k==='domestic') return sid==='ka_watch'?{zh:'🇨🇳 国内客户品牌',en:'🇨🇳 Domestic customer brands'}:{zh:'🇨🇳 国内原料商',en:'🇨🇳 Domestic suppliers'};
  return {zh:g,en:g};
}

function sectionHTML(s){
  const items=s.items||[];
  const grouped=items.some(i=>i.group);
  let body;
  if(grouped){
    const order=[...new Set(items.map(i=>i.group))];
    body=order.map(g=>{
      const gl=groupLabel(g,s.section_id);
      const cards=items.filter(i=>i.group===g).map((i,idx)=>cardHTML(i,s,idx)).join('');
      return '<div class="group"><div class="group-label">'+esc(t(gl))+'</div><div class="card-grid">'+cards+'</div></div>';
    }).join('');
  } else {
    body='<div class="card-grid">'+items.map((i,idx)=>cardHTML(i,s,idx)).join('')+'</div>';
  }
  return '<section class="section" id="sec-'+s.section_id+'" data-section="'+s.section_id+'">'+
    '<div class="section-header"><div class="s-icon">'+(SEC_ICON[s.section_id]||'📄')+'</div>'+
    '<h2 data-term="'+s.section_id+'">'+esc(t(s.title))+'<span class="s-sub">'+esc(t(s.summary))+'</span></h2>'+
    '<span class="section-count" data-count-for="'+s.section_id+'">'+items.length+'</span>'+
    '<span class="toggle-icon">▼</span></div>'+
    '<div class="section-body">'+body+'</div></section>';
}

function cardHTML(item,sec,idx){
  const tags=(item.tags||[]).filter(tg=>tagCategoryByTag[tg]);   // only V4 dictionary fields
  const tagRow=tags.map(tg=>'<span class="tag '+tagClass(tg)+'" data-term="'+esc(tg)+'">'+esc(tagLabel(tg))+'</span>').join('');
  const meta=[];
  if(sec.section_id==='market_flash') meta.push('<span class="idx-badge">'+(idx+1)+'</span>');
  if(item.date) meta.push('<span class="date-chip">'+esc(item.date)+'</span>');
  meta.push('<span class="section-chip" data-term="'+sec.section_id+'">'+esc(sectionName(sec.section_id))+'</span>');
  if(item.company) meta.push('<span class="company-chip">'+esc(item.company_display?t(item.company_display):item.company)+'</span>');
  if(item.region) meta.push('<span class="region-chip">'+esc(t(item.region))+'</span>');
  const srcFoot=(item.source_ref_ids||[]).map(id=>srcLink(id)).join(' ');
  const edit = MODE==='internal' ? '<button class="edit-hot no-print">✏️ '+L('建议重写','Request rewrite')+'</button>' : '';
  const foot=(srcFoot||edit)?'<div class="card-foot">'+(srcFoot?'<span>🔗 '+srcFoot+'</span>':'')+edit+'</div>':'';
  return '<div class="intel-card" id="item-'+esc(item.item_id)+'" data-item="'+esc(item.item_id)+'" data-sgkey="'+esc(item.item_id)+'" data-tags=\''+esc(JSON.stringify(item.tags||[]))+'\' data-search="'+esc(buildSearch(item,sec))+'">'+
    '<div class="card-meta">'+meta.join('')+'</div>'+
    '<h3>'+esc(t(item.title))+'</h3>'+
    '<div class="summary">'+esc(t(item.summary))+'</div>'+
    (tagRow?'<div class="tag-row">'+tagRow+'</div>':'')+
    deepHTML(item,sec)+
    foot+'</div>';
}

const DEEP_LABEL={market_flash:{zh:'深度解读',en:'In-depth analysis'},
  competitor_watch:{zh:'竞品深度解读',en:'Competitor deep-dive'},
  ingredient_innovation:{zh:'技术深度解读',en:'Technical deep-dive'},
  ka_watch:{zh:'客户深度解读',en:'Customer deep-dive'},
  market_event:{zh:'活动价值分析',en:'Event value analysis'},
  regulation_policy:{zh:'法规深度解读',en:'Regulatory deep-dive'}};
function analysisBlocks(item){
  if(item.analysis&&item.analysis.length)
    return item.analysis.map(a=>'<div class="an-block"><span class="an-label">'+esc(t(a.label))+'</span><div class="an-text">'+esc(t(a.text))+'</div></div>').join('');
  return item.detail?'<div class="an-text">'+esc(t(item.detail))+'</div>':'';
}
function deepHTML(item,sec){
  const blocks=analysisBlocks(item); if(!blocks) return '';
  const lab=DEEP_LABEL[sec.section_id]||{zh:'深度解读',en:'In-depth analysis'};
  return '<div class="deep"><button class="deep-toggle"><span class="chev">▶</span>🔎 '+esc(t(lab))+'</button>'+
    '<div class="deep-body"><span class="ai-disclaimer">🤖 '+L('AI 生成 · 仅供参考','AI-generated · for reference only')+'</span>'+blocks+'</div></div>';
}

function buildSearch(item,sec){
  const parts=[];
  ['title','summary','detail','category','region'].forEach(k=>{ if(item[k]){parts.push(item[k].zh||'',item[k].en||'');} });
  (item.analysis||[]).forEach(a=>parts.push(a.text&&a.text.zh||'',a.text&&a.text.en||''));
  if(item.company) parts.push(item.company);
  if(item.company_display) parts.push(item.company_display.zh||'',item.company_display.en||'');
  (item.tags||[]).forEach(tg=>{parts.push(tg); const g=glossaryById[tg]; if(g) parts.push(g.display.zh||'',g.display.en||'');});
  parts.push(t(sec.title),sec.title.zh,sec.title.en,sec.section_id);
  (item.source_ref_ids||[]).forEach(id=>{const s=sourceById[id]; if(s){ if(s.source_name) parts.push(s.source_name.zh||s.source_name,s.source_name.en||''); parts.push(s.title.zh||'',s.title.en||'');}});
  return parts.join(' ').toLowerCase();
}

/* #1 — show the real article / news title (source_name moves to the hover title) */
function srcLink(id){
  const s=sourceById[id]; if(!s) return '';
  return '<a class="src-link" href="'+esc(s.url)+'" target="_blank" rel="noopener" title="'+esc(t(s.source_name))+'">'+esc(t(s.title))+' ↗</a>';
}

function appendixHTML(d){
  const groups={};
  (d.source_links||[]).forEach(s=>{ (groups[s.source_type]=groups[s.source_type]||[]).push(s); });
  const TYPE={regulatory:{zh:'⚖️ 法规与官方',en:'⚖️ Regulatory & official'},industry_media:{zh:'📰 行业媒体',en:'📰 Industry media'},
    company:{zh:'🏢 企业来源',en:'🏢 Company sources'},database:{zh:'📊 数据库与机构',en:'📊 Databases & institutions'},
    market_data:{zh:'📊 市场数据',en:'📊 Market data'},event:{zh:'📅 活动来源',en:'📅 Event sources'},brand:{zh:'🏷️ 品牌来源',en:'🏷️ Brand sources'}};
  const body=Object.keys(groups).map(tp=>{
    const head=TYPE[tp]?t(TYPE[tp]):tp;
    const rows=groups[tp].map(s=>{
      const secs=(s.section_ids||[]).map(id=>'<span class="s-sec" data-term="'+id+'">'+esc(sectionName(id))+'</span>').join('');
      return '<div class="src-item" id="src-'+esc(s.source_ref_id)+'"><div class="s-title"><a href="'+esc(s.url)+'" target="_blank" rel="noopener">'+esc(t(s.title))+' ↗</a></div>'+
        '<div class="s-meta"><span>'+esc(t(s.source_name))+'</span><span class="s-secs">'+secs+'</span></div></div>';
    }).join('');
    return '<div class="src-group"><h4>'+esc(head)+'</h4>'+rows+'</div>';
  }).join('');
  return '<section class="section appendix" id="sec-appendix"><div class="section-header"><div class="s-icon">🔗</div>'+
    '<h2>'+L('数据来源与原文链接汇总','Sources & Links')+'<span class="s-sub">'+L('所有引用来源、原文链接、来源类型与对应栏目','All cited sources, original links, source types, and mapped sections')+'</span></h2>'+
    '<span class="section-count">'+(d.source_links||[]).length+'</span><span class="toggle-icon">▼</span></div>'+
    '<div class="section-body">'+body+'</div></section>';
}

function footerHTML(d){
  return '<footer class="report-footer"><strong>Croda Beauty '+L('市场监测月报','Market Intelligence Monthly')+'</strong> · '+esc(t({zh:d.period.display_zh,en:d.period.display_en}))+
    '<br>'+L('配置驱动渲染 Demo · 数值与内容为演示数据 · 仅供内部参考','Config-driven demo · figures and content are illustrative · internal use only')+'</footer>';
}

function submitPanelHTML(){
  return '<div class="submit-panel no-print" id="submit-panel"><span class="sg-count" id="sg-count"></span>'+
    '<button class="tool-btn primary" id="submit-all">📤 '+L('一键提交给报告 Agent','Submit all to report Agent')+'</button></div>';
}

/* ---------- interactions ---------- */
function bindEvents(){
  document.querySelectorAll('.lang-toggle button').forEach(b=>b.onclick=()=>{ if(b.dataset.lang!==lang){lang=b.dataset.lang; draw();} });
  document.querySelectorAll('.section-header').forEach(h=>h.onclick=()=>h.parentElement.classList.toggle('collapsed'));
  document.querySelectorAll('[data-jump]').forEach(el=>el.addEventListener('click',e=>{
    e.stopPropagation(); const tgt=document.getElementById(el.dataset.jump);
    if(tgt){ tgt.classList.remove('collapsed'); tgt.scrollIntoView({behavior:'smooth',block:'start'}); }
  }));
  const sb=document.getElementById('search'); if(sb) sb.oninput=()=>applyVisibility();
  document.getElementById('print-btn').onclick=()=>window.print();
  setupCascade();
  document.querySelectorAll('.deep-toggle').forEach(b=>b.onclick=()=>b.closest('.deep').classList.toggle('open'));
  document.querySelectorAll('.kpi-card.clickable').forEach(c=>c.addEventListener('click',e=>{
    if(e.target.closest('.edit-hot')) return; jumpToItem(c.dataset.jumpItem);
  }));
  document.querySelectorAll('.edit-hot').forEach(b=>b.addEventListener('click',e=>{e.stopPropagation();
    const host=b.closest('[data-sgkey]'); if(host) openSuggestionBox(host.dataset.sgkey,b);}));
  const sa=document.getElementById('submit-all'); if(sa) sa.onclick=submitAll;
  setupTooltips();
  const ov=document.getElementById('modal-overlay'); ov.onclick=e=>{ if(e.target===ov) closeModal(); };
  document.addEventListener('keydown',e=>{ if(e.key==='Escape'){closeModal();hideTooltip();hideEditPop();} });
  document.addEventListener('click',e=>{ if(!e.target.closest('#edit-pop')&&!e.target.closest('.edit-hot')) hideEditPop(); });
}

function jumpToItem(itemId){
  closeModal();
  const card=document.getElementById('item-'+itemId); if(!card) return;
  const sec=card.closest('.section'); if(sec) sec.classList.remove('collapsed');
  card.scrollIntoView({behavior:'smooth',block:'center'});
  card.classList.remove('flash-hl'); void card.offsetWidth; card.classList.add('flash-hl');
  setTimeout(()=>card.classList.remove('flash-hl'),1900);
}

function setupCascade(){
  const wrap=document.getElementById('filter-wrap'), trigger=document.getElementById('filter-trigger');
  trigger.onclick=()=>wrap.classList.toggle('open');
  document.addEventListener('click',e=>{ if(!e.target.closest('#filter-wrap')) wrap.classList.remove('open'); });
  function showCat(cid){
    document.querySelectorAll('.cascade-cat').forEach(c=>c.classList.toggle('active',c.dataset.cat===cid));
    const cat=categoryById[cid]; const fg='var(--'+cat.color_class.replace('tag-','')+'-fg)', bg='var(--'+cat.color_class.replace('tag-','')+'-bg)';
    document.getElementById('cascade-fields').innerHTML=cat.tags.map(tg=>{
      const key=cid+'::'+tg, on=activeFilters.has(key);
      return '<span class="cascade-field '+(on?'on':'')+'" data-key="'+key+'" data-term="'+esc(tg)+'" style="color:'+fg+';background:'+bg+'">'+esc(tagLabel(tg))+'</span>';
    }).join('');
    document.querySelectorAll('.cascade-field').forEach(f=>{ f.onclick=()=>{ toggleFilter(f.dataset.key); f.classList.toggle('on'); }; attachTip(f); });
  }
  document.querySelectorAll('.cascade-cat').forEach(c=>{ c.addEventListener('mouseenter',()=>showCat(c.dataset.cat)); c.addEventListener('click',()=>showCat(c.dataset.cat)); });
  document.getElementById('cascade-clear').onclick=()=>{ activeFilters.clear(); showCat(document.querySelector('.cascade-cat.active').dataset.cat); renderActiveFilters(); applyVisibility(); };
  showCat((DATA.tag_taxonomy[0]||{}).category_id);
}
function toggleFilter(key){ activeFilters.has(key)?activeFilters.delete(key):activeFilters.add(key); renderActiveFilters(); applyVisibility(); }
function renderActiveFilters(){
  const box=document.getElementById('active-filters'); if(!box) return;
  const arr=[...activeFilters];
  document.getElementById('filter-cnt').textContent=arr.length;
  document.getElementById('filter-trigger').classList.toggle('has-active',arr.length>0);
  box.innerHTML=arr.map(key=>{ const tg=key.split('::')[1]; const cat=tagCategoryByTag[tg];
    const fg='var(--'+cat.color_class.replace('tag-','')+'-fg)', bg='var(--'+cat.color_class.replace('tag-','')+'-bg)';
    return '<span class="af-chip" data-key="'+key+'" style="color:'+fg+';background:'+bg+'">'+esc(tagLabel(tg))+' <span class="x">✕</span></span>';
  }).join('') + (arr.length?'<span class="af-clear" id="af-clear-all">'+L('全部清除','Clear all')+'</span>':'');
  box.querySelectorAll('.af-chip').forEach(c=>c.onclick=()=>{ activeFilters.delete(c.dataset.key); renderActiveFilters(); applyVisibility();
    const af=document.querySelector('.cascade-field[data-key="'+c.dataset.key+'"]'); if(af) af.classList.remove('on'); });
  const clr=document.getElementById('af-clear-all'); if(clr) clr.onclick=()=>{ activeFilters.clear(); renderActiveFilters(); applyVisibility(); document.querySelectorAll('.cascade-field.on').forEach(f=>f.classList.remove('on')); };
}

function applyVisibility(){
  const ql=((document.getElementById('search')||{}).value||'').trim().toLowerCase();
  const byCat={}; activeFilters.forEach(k=>{ const[c,tg]=k.split('::'); (byCat[c]=byCat[c]||[]).push(tg); });
  const cats=Object.keys(byCat);
  let anyVisible=false;
  document.querySelectorAll('.intel-card').forEach(card=>{
    const tags=JSON.parse(card.dataset.tags||'[]');
    const okSearch=!ql||card.dataset.search.indexOf(ql)>=0;
    const okFilter=cats.every(c=>byCat[c].some(tg=>tags.includes(tg)));
    const show=okSearch&&okFilter; card.style.display=show?'':'none'; if(show) anyVisible=true;
  });
  document.querySelectorAll('.group').forEach(g=>{ g.style.display=[...g.querySelectorAll('.intel-card')].some(c=>c.style.display!=='none')?'':'none'; });
  document.querySelectorAll('.section[data-section]').forEach(sec=>{
    const cards=[...sec.querySelectorAll('.intel-card')], vis=cards.filter(c=>c.style.display!=='none').length;
    sec.style.display=vis?'':'none';
    const badge=sec.querySelector('[data-count-for]'); if(badge) badge.textContent=(ql||cats.length)?vis+'/'+cards.length:cards.length;
  });
  document.getElementById('no-results').style.display=anyVisible?'none':'block';
}

/* tooltips */
function tipShow(el){
  const tip=document.getElementById('tooltip'); const g=glossaryById[el.dataset.term]; if(!g) return;
  tip.innerHTML='<div class="tt-title">'+esc(t(g.display))+'</div>'+esc(t(g.definition)); tip.style.display='block';
  const r=el.getBoundingClientRect(), tw=tip.offsetWidth, th=tip.offsetHeight;
  let x=Math.max(8,Math.min(r.left+r.width/2-tw/2,innerWidth-tw-8)); let y=r.top-th-8; if(y<8) y=r.bottom+8;
  tip.style.left=x+'px'; tip.style.top=y+'px';
}
function attachTip(el){
  if(!el||el._tip||!glossaryById[el.dataset.term]) return; el._tip=1;
  el.addEventListener('mouseenter',()=>tipShow(el)); el.addEventListener('mouseleave',hideTooltip);
  el.addEventListener('focus',()=>tipShow(el)); el.addEventListener('blur',hideTooltip);
  if(!el.matches('h2')) el.tabIndex=0;
  el.addEventListener('click',e=>{ if(window.matchMedia('(hover:none)').matches){ e.stopPropagation(); document.getElementById('tooltip').style.display==='block'?hideTooltip():tipShow(el);} });
}
function setupTooltips(){ document.querySelectorAll('[data-term]').forEach(attachTip); }
function hideTooltip(){ document.getElementById('tooltip').style.display='none'; }

/* detail modal */
let itemIndex=null;
function findItem(id){ if(!itemIndex){ itemIndex={}; DATA.sections.forEach(s=>s.items.forEach(i=>itemIndex[i.item_id]={item:i,sec:s})); } return itemIndex[id]; }
function closeModal(){ document.getElementById('modal-overlay').classList.remove('open'); hideTooltip(); }

/* ---------- internal: rewrite suggestions (items + KPIs, with EN/ZH scope) ---------- */
function scopeRadios(name,sel){
  const o=[['both',L('同步中英文','Sync ZH+EN')],['zh',L('仅中文','ZH only')],['en',L('仅英文','EN only')]];
  return '<div class="ep-scope">'+o.map(v=>'<label><input type="radio" name="'+name+'" value="'+v[0]+'"'+(v[0]===(sel||'both')?' checked':'')+'> '+v[1]+'</label>').join('')+'</div>';
}
function reapplySuggestions(){ Object.keys(suggestions).forEach(k=>markSug(k,true)); updateSubmitCount(); }
function markSug(key,on){
  document.querySelectorAll('[data-sgkey="'+cssEsc(key)+'"]').forEach(el=>{
    el.classList.toggle('has-suggestion',on);
    const btn=el.querySelector('.edit-hot');
    if(btn){ btn.classList.toggle('active',on);
      if(!btn.classList.contains('kpi-edit')) btn.innerHTML=on?'✏️ '+L('已填写建议','Suggestion added'):'✏️ '+L('建议重写','Request rewrite'); }
    const holder=el.querySelector('.card-meta')||el.querySelector('.kpi-top');
    let pill=el.querySelector('.status-pill');
    if(on){ if(!pill&&holder) holder.insertAdjacentHTML('beforeend','<span class="status-pill status-tobemod">'+L('待修改','To revise')+'</span>'); }
    else if(pill) pill.remove();
  });
}
function setSug(key,text,scope){
  const v=(text||'').trim();
  if(v){ suggestions[key]={text:v,scope:scope||'both'}; markSug(key,true); }
  else { delete suggestions[key]; markSug(key,false); }
  updateSubmitCount();
}
function hideEditPop(){ document.getElementById('edit-pop').style.display='none'; }
function analysisText(item){
  if(item.analysis&&item.analysis.length) return item.analysis.map(a=>t(a.label)+(lang==='zh'?'：':': ')+t(a.text)).join('\n');
  return item.detail?t(item.detail):'';
}
function openSuggestionBox(key,anchor){
  const pop=document.getElementById('edit-pop'); const ex=suggestions[key]||{text:'',scope:'both'};
  const meta=sgMeta[key]||{title:{zh:key,en:key}};
  const item=meta.type==='item'?(findItem(key)||{}).item:null;
  const hasAn=item&&((item.analysis&&item.analysis.length)||item.detail);
  const prefill=item?'<div class="prefill-row"><span class="prefill" data-pf="summary">'+L('↪ 基于新闻摘要','↪ From summary')+'</span>'+
    (hasAn?'<span class="prefill" data-pf="analysis">'+L('↪ 基于深度解读','↪ From analysis')+'</span>':'')+'</div>':'';
  pop.innerHTML='<div class="ep-title">'+L('建议重写 / 删除','Request rewrite / delete')+'</div>'+
    '<div class="ep-sub">'+(meta.type==='kpi'?L('指标卡：','KPI: '):'')+esc(t(meta.title))+'</div>'+
    prefill+
    '<textarea id="ep-text" placeholder="'+L('请输入调整需求或意见，例如：补充对 Croda 的供应机会；或：建议删除本条。','Describe the change, e.g. add the Croda supply angle; or: please delete this item.')+'">'+esc(ex.text)+'</textarea>'+
    scopeRadios('ep-scope',ex.scope)+
    '<div class="ep-row"><button class="ep-save" id="ep-save">'+L('提交建议','Save')+'</button>'+
      (ex.text?'<button class="ep-del" id="ep-del">'+L('删除建议','Remove')+'</button>':'')+'</div>'+
    '<div class="ep-note">'+L('删除建议即视同确认本条。提交后由报告 Agent 重写。','Removing a suggestion confirms the item. Submitted items are rewritten by the report Agent.')+'</div>';
  pop.style.display='block';
  const r=anchor.getBoundingClientRect();
  pop.style.left=Math.max(8,Math.min(r.left,innerWidth-pop.offsetWidth-8))+'px';
  pop.style.top=(r.bottom+6+pop.offsetHeight>innerHeight?Math.max(8,r.top-pop.offsetHeight-6):r.bottom+6)+'px';
  const ta=document.getElementById('ep-text'); ta.focus();
  pop.querySelectorAll('.prefill').forEach(p=>p.onclick=()=>{ ta.value=(p.dataset.pf==='analysis')?analysisText(item):t(item.summary); });
  document.getElementById('ep-save').onclick=()=>{ setSug(key,ta.value,(pop.querySelector('input[name=ep-scope]:checked')||{}).value); hideEditPop(); };
  const del=document.getElementById('ep-del'); if(del) del.onclick=()=>{ setSug(key,'',''); hideEditPop(); };
}
function updateSubmitCount(){
  const el=document.getElementById('sg-count'); if(!el) return; const n=Object.keys(suggestions).length;
  el.innerHTML=n?L('已标记 <b>'+n+'</b> 条修改建议','<b>'+n+'</b> rewrite suggestion(s) marked'):L('暂无修改建议，默认不改动即视为确认','No suggestions — unmarked items are treated as confirmed');
}
function scopeLabel(s){ return s==='zh'?L('仅中文','ZH only'):s==='en'?L('仅英文','EN only'):L('中英同步','ZH+EN'); }
function submitAll(){
  const keys=Object.keys(suggestions);
  const list=keys.length?'<ul class="sg-list">'+keys.map(k=>{ const m=sgMeta[k]||{title:{zh:k,en:k}}; const sg=suggestions[k];
    const kpiTag=m.type==='kpi'?'<span class="sg-scope sg-kpi">'+L('指标卡','KPI')+'</span>':'';
    return '<li><div class="sg-t">'+kpiTag+esc(t(m.title))+'</div><div class="sg-c">'+esc(sg.text)+'</div><span class="sg-scope">'+scopeLabel(sg.scope)+'</span></li>';
  }).join('')+'</ul>':'<p style="color:var(--text-secondary)">'+L('当前没有任何修改建议。所有卡片默认视为确认。','No rewrite suggestions. All cards are confirmed by default.')+'</p>';
  document.getElementById('modal').innerHTML='<div class="modal-head"><button class="modal-close" id="m-close">✕</button>'+
    '<div class="m-sec">'+L('提交给报告 Agent','Submit to report Agent')+'</div><h3>'+L(keys.length+' 条修改建议',keys.length+' rewrite suggestion(s)')+'</h3></div>'+
    '<div class="modal-body">'+
    (keys.length?'<div class="ep-note" style="margin-bottom:12px">'+L('每条建议右侧标注了应用范围（中英同步 / 仅中文 / 仅英文）。如需调整，请关闭后在卡片上重新编辑。','Each suggestion is tagged with its scope (ZH+EN / ZH only / EN only). To change it, close and re-edit on the card.')+'</div>':'')+
    list+
    (keys.length?'<button class="tool-btn primary" id="confirm-submit" style="width:100%;margin-top:6px">'+L('确认提交','Confirm submit')+'</button>':'')+
    '</div>';
  document.getElementById('modal-overlay').classList.add('open');
  document.getElementById('m-close').onclick=closeModal;
  const cs=document.getElementById('confirm-submit'); if(cs) cs.onclick=()=>submitDone(keys);
}
function submitDone(keys){
  const month=DATA.month||'';
  const stamp=new Date().toISOString().slice(0,10).replace(/-/g,'');
  const fname='修改建议_'+month+'_'+stamp+'.html';
  document.getElementById('modal').innerHTML='<div class="modal-head"><button class="modal-close" id="m-close">✕</button>'+
    '<div class="m-sec">'+L('提交修改建议','Submit rewrite suggestions')+'</div><h3>'+L('已生成本期修改建议文件','Rewrite-suggestion file generated')+'</h3></div>'+
    '<div class="modal-body"><div class="done-box"><div class="done-ico">📄✅</div>'+
    '<div>'+L('已生成包含 '+keys.length+' 条修改建议的文件（Demo 阶段不实际下载）：','A file with '+keys.length+' suggestion(s) has been generated (not actually downloaded in demo):')+'</div>'+
    '<div class="done-file">'+esc(fname)+'</div></div>'+
    '<div class="done-steps"><b>'+L('下一步操作','Next steps')+'</b><br>'+
      L('1. 保存这份修改建议文件。<br>2. 将文件放入本期报告目录 report/'+month+'/ 下的「修改意见」文件夹。<br>3. 报告 Agent 会自动读取该文件，按你标记的建议（含中英同步范围）重写相关卡片，并返回新一版报告。',
        '1. Save this suggestion file.<br>2. Drop it into the "rewrite-suggestions" folder under report/'+month+'/ for this issue.<br>3. The report Agent will read it and rewrite the flagged cards (respecting each ZH/EN scope), then return a new version.')+
    '</div>'+
    '<button class="tool-btn primary" id="done-ok" style="width:100%;margin-top:14px">'+L('知道了','Got it')+'</button></div>';
  document.getElementById('m-close').onclick=closeModal;
  document.getElementById('done-ok').onclick=closeModal;
}
</script>
</body>
</html>
"""


def build(data, mode, out):
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = TEMPLATE.replace("__REPORT_DATA__", payload).replace("__MODE__", mode)
    out.write_text(html, encoding="utf-8")
    print(f"  {out.name}  ({len(html)//1024} KB)  mode={mode}")


def main():
    data = json.loads(SRC.read_text(encoding="utf-8"))
    print(f"Rendering from {SRC.name}: sections={len(data.get('sections',[]))} kpis={len(data.get('kpis',[]))} "
          f"glossary={len(data.get('glossary',[]))} sources={len(data.get('source_links',[]))} "
          f"tag_categories={len(data.get('tag_taxonomy',[]))}")
    build(data, "internal", HERE / "report-internal.html")
    build(data, "final", HERE / "report-final.html")


if __name__ == "__main__":
    main()

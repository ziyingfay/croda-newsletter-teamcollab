#!/usr/bin/env python3
"""脚本打标层（模块 B · script-tagger）· MVP 开发版

输入起点 = 已抽好正文的 all-articles(1).json（不依赖 spider，不做 HTML→正文清洗）。
本版按需求做了三处省略（见脚本层设计文档「调整后的方案」）：
  - 跳过 source_profiles 派生：mpId/author 原样透传为来源身份（source_raw）。
  - published_at 置空：该输入的 publishTime 不可靠（全落同月、逐秒递增=抓取排序），
    按文档原则"宁可置空也不冒充"，仅透传 fetched_at。
  - 跳过真实清洗：contentText 已是抽好的正文，直接用（空/超短文按 extraction 降级或剔除）。

打标核心（配置驱动，词表全外置）：
  spans / company(+normalized) / ingredient_mentions / is_event+event_type / fact_hints
配置：
  watchlist_entities_seed.json  → company 抽取与归一
  ingredient_alias_seed.json    → ingredient_mentions
  event_keywords_seed.json      → is_event/event_type

产物：待打标.json（rss_clean + 脚本字段）+ run_log.json

> 等后续抓到更可靠的 JSON（带真实 publishTime / source 信息）：只需改 load_articles 适配段，
> 并打开 source_profiles / published_at 解析，打标核心逻辑不变。

Run from repo root:
    python3 product/script-tagger/script_tagger.py
    python3 product/script-tagger/script_tagger.py --src <input.json> --limit 30
"""
from __future__ import annotations
import argparse, hashlib, json, re
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SRC = ROOT / "project-management/reference/examples/all-articles(1).json"
PARAM = ROOT / "product/parameter-file"
WATCHLIST_CFG = PARAM / "watchlist/watchlist_entities_seed.json"
INGREDIENT_CFG = PARAM / "ingredient-alias/ingredient_alias_seed.json"
EVENT_CFG = PARAM / "event-keywords/event_keywords_seed.json"
OUT_DIR = ROOT / "product/output/result/tagging"

SENT_SPLIT_RE = re.compile(r"[^。！？；!?;\n]+[。！？；!?;\n]?")
ASCII_ALIAS_RE = re.compile(r"^[\x00-\x7f]+$")
CONTENT_TRIM = 4000  # 抽取扫描窗口（避免超长文逐句开销；spans 仍按完整 trim 切）

# ---------- 文本匹配 ----------

def _compile_alias(alias: str) -> re.Pattern:
    """ASCII 别名加词边界、大小写不敏感；CJK 别名用子串。"""
    if ASCII_ALIAS_RE.match(alias):
        return re.compile(r"(?<![A-Za-z0-9])" + re.escape(alias) + r"(?![A-Za-z0-9])", re.IGNORECASE)
    return re.compile(re.escape(alias))


def match_aliases(text: str, alias_patterns: list[tuple[re.Pattern, Any]]) -> list[Any]:
    """返回命中的 payload（去重保序）。"""
    out, seen = [], set()
    for pat, payload in alias_patterns:
        if pat.search(text):
            key = json.dumps(payload, ensure_ascii=False, sort_keys=True) if isinstance(payload, dict) else payload
            if key not in seen:
                seen.add(key)
                out.append(payload)
    return out


# ---------- 配置加载 ----------

def load_watchlist() -> list[tuple[re.Pattern, dict]]:
    cfg = json.loads(WATCHLIST_CFG.read_text(encoding="utf-8"))
    pats = []
    for e in cfg["entities"]:
        payload = {"display_name": e["display_name"], "entity_role": e["entity_role"]}
        for a in e["aliases"]:
            pats.append((_compile_alias(a), payload))
    return pats


def load_ingredients() -> list[tuple[re.Pattern, dict]]:
    cfg = json.loads(INGREDIENT_CFG.read_text(encoding="utf-8"))
    pats = []
    for it in cfg["ingredients"]:
        payload = {"key": it["key"], "display": it["display"]}
        for a in it["aliases"]:
            pats.append((_compile_alias(a), payload))
    return pats


def load_events() -> list[tuple[str, list[re.Pattern]]]:
    cfg = json.loads(EVENT_CFG.read_text(encoding="utf-8"))
    return [(et["event_type"], [_compile_alias(k) for k in et["keywords"]]) for et in cfg["event_types"]]


# ---------- 字段实现 ----------

def stable_article_id(url: str, fallback: str) -> str:
    """sha1(规范化 url)；缺 url 用 fallback。规范化=去 query/fragment。"""
    if url:
        s = urlsplit(url)
        canonical = urlunsplit((s.scheme, s.netloc, s.path, "", ""))
        return "sha1:" + hashlib.sha1(canonical.encode()).hexdigest()
    return "sha1:" + hashlib.sha1(fallback.encode()).hexdigest()


def split_spans(title: str, content: str) -> list[dict]:
    spans = []
    if title.strip():
        spans.append({"id": "s0", "text": title.strip()})
    idx = 1
    for m in SENT_SPLIT_RE.finditer(content or ""):
        seg = m.group(0).strip()
        if len(seg) < 2:
            continue
        spans.append({"id": f"s{idx}", "text": seg})
        idx += 1
    return spans


def detect_event(text: str, event_rules) -> tuple[bool, str | None]:
    for etype, pats in event_rules:
        if any(p.search(text) for p in pats):
            return True, etype
    return False, None


def extraction_status(text_len: int, quality: int | None) -> str:
    """两态：success / partial（契约要求）。空文不入库（由调用方剔除）。"""
    if quality is not None and quality >= 70 and text_len >= 300:
        return "success"
    return "partial"


# ---------- 主流程 ----------

def load_articles(src: Path) -> list[dict]:
    """适配 all-articles(1).json：{generatedAt,totalArticles,articles:[...]}。
    换输入格式时改这里即可。"""
    data = json.loads(src.read_text(encoding="utf-8"))
    return data["articles"]


def main() -> int:
    ap = argparse.ArgumentParser(description="script-tagger MVP (module B)")
    ap.add_argument("--src", default=str(DEFAULT_SRC))
    ap.add_argument("--limit", type=int, default=0, help="只处理前 N 篇（调试用，0=全部）")
    ap.add_argument("--out-dir", default=str(OUT_DIR))
    args = ap.parse_args()

    src = Path(args.src)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    watch_pats = load_watchlist()
    ingr_pats = load_ingredients()
    event_rules = load_events()

    articles = load_articles(src)
    if args.limit:
        articles = articles[: args.limit]

    tagged: list[dict] = []
    log = {
        "src": str(src),
        "input_count": len(articles),
        "output_count": 0,
        "dropped_empty": 0,
        "source_profiles": "SKIPPED (mpId/author passthrough only)",
        "published_at": "SET NULL (input publishTime unreliable)",
        "extraction_dist": Counter(),
        "is_event_count": 0,
        "event_type_dist": Counter(),
        "with_company": 0,
        "with_ingredient": 0,
        "empty_dropped_ids": [],
    }
    seen_ids: set[str] = set()
    dup = 0

    for a in articles:
        title = (a.get("title") or "").strip()
        text = (a.get("contentText") or "").strip()
        url = a.get("url") or ""

        if not text:
            log["dropped_empty"] += 1
            log["empty_dropped_ids"].append(a.get("id"))
            continue

        aid = stable_article_id(url, fallback=f"{a.get('mpId','')}|{title}")
        if aid in seen_ids:
            dup += 1
            continue
        seen_ids.add(aid)

        scan = title + "\n" + text[:CONTENT_TRIM]
        quality = (a.get("meta") or {}).get("qualityScore")
        status = extraction_status(len(text), quality)

        companies = match_aliases(scan, watch_pats)
        company_names = sorted({c["display_name"] for c in companies})
        ingredients = match_aliases(scan, ingr_pats)
        ingr_display = sorted({i["display"] for i in ingredients})
        ingr_keys = sorted({i["key"] for i in ingredients})
        # is_event 只看标题：正文常夹带活动广告/页脚（PCHi 报名等），全文匹配会大量误判。
        # 活动文（预告/回顾/邀请）几乎都在标题点明主题。
        is_event, event_type = detect_event(title, event_rules)

        record = {
            # --- 基础字段（rss_clean 子集，本输入可得部分）---
            "article_id": aid,
            "source_article_id": a.get("id"),
            "url": url,
            "title": title,
            "content": text,
            "content_length": len(text),
            "extraction_status": status,
            "published_at": None,
            "published_at_note": "input publishTime unreliable; left null per spec",
            "fetched_at": a.get("fetchedAt"),
            "source_raw": {"mp_id": a.get("mpId"), "author": a.get("author")},
            "source_profile_matched": False,
            # --- 脚本打标字段（V4 下放项）---
            "spans": split_spans(title, text[:CONTENT_TRIM]),
            "company": company_names,
            "company_normalized": company_names,
            "company_detail": companies,
            "ingredient_mentions": ingr_display,
            "ingredient_keys": ingr_keys,
            "is_event": is_event,
            "event_type": event_type,
            "fact_hints": {
                "company": company_names,
                "ingredient_technology": ingr_display,
                "event": event_type,
            },
        }
        tagged.append(record)

        log["extraction_dist"][status] += 1
        if is_event:
            log["is_event_count"] += 1
            log["event_type_dist"][event_type] += 1
        if company_names:
            log["with_company"] += 1
        if ingr_display:
            log["with_ingredient"] += 1

    log["output_count"] = len(tagged)
    log["dup_skipped"] = dup
    log["extraction_dist"] = dict(log["extraction_dist"])
    log["event_type_dist"] = dict(log["event_type_dist"])

    (out_dir / "待打标.json").write_text(json.dumps(tagged, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "run_log.json").write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"输入 {log['input_count']} 篇 → 输出 {log['output_count']} 篇"
          f"（空文剔除 {log['dropped_empty']}，重复 {dup}）")
    print(f"  extraction: {log['extraction_dist']}")
    print(f"  命中 company: {log['with_company']}  命中 ingredient: {log['with_ingredient']}")
    print(f"  is_event: {log['is_event_count']}  类型分布: {log['event_type_dist']}")
    print(f"  → {out_dir/'待打标.json'}")
    print(f"  → {out_dir/'run_log.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

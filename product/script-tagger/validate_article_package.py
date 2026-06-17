#!/usr/bin/env python3
"""Validate 待打标.json（脚本打标层模块 B 的产物 = rss_clean + 脚本字段）.

对齐脚本层文档 3.4：校验脚本字段 + spans 结构 + 与契约一致，是 script_tagger 的下游闸。
与 validate_watchlist.py（校验配置，上游）配成本链路的校验闭环。

校验项（ERROR=阻断，WARN=提示）：
  [ERROR] 顶层非数组 / 记录非对象
  [ERROR] 缺必填字段 / 类型错误
  [ERROR] article_id 缺失/重复
  [ERROR] extraction_status 不在 {success, partial}
  [ERROR] content_length != len(content)
  [ERROR] spans 结构错：非 {id,text} / s0 缺失 / s0!=title / id 不连续(s0..sN)
  [ERROR] company / company_normalized / ingredient_mentions / ingredient_keys 非字符串数组
  [ERROR] is_event 非布尔 / event_type 与 is_event 不自洽（True 必有 type，False 必为 null）
  [ERROR] company_detail 里的 display_name 未出现在 company
  [WARN ] published_at 非 null 且非 ISO（本输入约定置空）
  [WARN ] source_raw 缺 mp_id/author
  [WARN ] 整篇 spans 为空（无标题且无正文）

Usage:
    python3 validate_article_package.py                      # 默认 output/result/tagging/待打标.json
    python3 validate_article_package.py path/to/待打标.json
    python3 validate_article_package.py --strict             # WARN 也判失败
退出码：0 通过；1 有 ERROR（或 --strict 下有 WARN）；2 读取失败。
"""
from __future__ import annotations
import argparse, json, re, sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PKG = ROOT / "product/output/result/tagging/待打标.json"

REQUIRED = {"article_id", "url", "title", "content", "content_length", "extraction_status",
            "published_at", "fetched_at", "source_raw", "spans",
            "company", "company_normalized", "company_detail",
            "ingredient_mentions", "ingredient_keys", "is_event", "event_type"}
EXTRACTION_ENUM = {"success", "partial"}
STR_ARRAY_FIELDS = ["company", "company_normalized", "ingredient_mentions", "ingredient_keys"]
ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}")
SPAN_ID_RE = re.compile(r"^s\d+$")


def is_str_list(v: Any) -> bool:
    return isinstance(v, list) and all(isinstance(x, str) for x in v)


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate 待打标.json article package.")
    ap.add_argument("path", nargs="?", default=str(DEFAULT_PKG))
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    p = Path(args.path)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"[FATAL] 文件不存在: {p}")
        return 2
    except json.JSONDecodeError as e:
        print(f"[FATAL] JSON 解析失败: {e}")
        return 2

    errors: list[str] = []
    warns: list[str] = []

    if not isinstance(data, list):
        print("[FATAL] 顶层应为数组（记录列表）")
        return 2

    seen_ids: dict[str, int] = {}
    extraction_dist: Counter = Counter()
    event_dist: Counter = Counter()
    n_company = n_ingr = n_event = 0

    for i, r in enumerate(data):
        tag = f"[{i}]"
        if not isinstance(r, dict):
            errors.append(f"{tag} 记录非对象")
            continue

        missing = REQUIRED - r.keys()
        if missing:
            errors.append(f"{tag} 缺字段: {sorted(missing)}")

        aid = r.get("article_id")
        if not isinstance(aid, str) or not aid:
            errors.append(f"{tag} article_id 非法: {aid!r}")
        elif aid in seen_ids:
            errors.append(f"article_id 重复: {aid!r}（{tag} 与 [{seen_ids[aid]}]）")
        else:
            seen_ids[aid] = i

        status = r.get("extraction_status")
        if status not in EXTRACTION_ENUM:
            errors.append(f"{tag} extraction_status 不在 {EXTRACTION_ENUM}: {status!r}")
        else:
            extraction_dist[status] += 1

        content = r.get("content")
        clen = r.get("content_length")
        if isinstance(content, str) and isinstance(clen, int) and len(content) != clen:
            errors.append(f"{tag} content_length({clen}) != len(content)({len(content)})")

        # spans
        spans = r.get("spans")
        title = r.get("title") or ""
        if not isinstance(spans, list):
            errors.append(f"{tag} spans 非数组")
        elif not spans:
            warns.append(f"{tag} spans 为空")
        else:
            ok_struct = all(isinstance(s, dict) and set(s.keys()) >= {"id", "text"} for s in spans)
            if not ok_struct:
                errors.append(f"{tag} spans 元素结构错（需 {{id,text}}）")
            else:
                ids = [s["id"] for s in spans]
                if ids[0] != "s0":
                    errors.append(f"{tag} spans 首元素 id 应为 s0，实为 {ids[0]!r}")
                elif spans[0]["text"].strip() != title.strip():
                    errors.append(f"{tag} s0 文本与 title 不一致")
                if ids != [f"s{j}" for j in range(len(ids))]:
                    errors.append(f"{tag} spans id 不连续: {ids[:5]}...")

        # 字符串数组字段
        for f in STR_ARRAY_FIELDS:
            if f in r and not is_str_list(r[f]):
                errors.append(f"{tag} {f} 应为字符串数组: {r.get(f)!r}")

        # company_normalized 与 company 一致性（本脚本两者相同）
        if is_str_list(r.get("company")) and is_str_list(r.get("company_normalized")):
            if sorted(r["company"]) != sorted(r["company_normalized"]):
                warns.append(f"{tag} company 与 company_normalized 不一致")
            if r["company"]:
                n_company += 1

        if is_str_list(r.get("ingredient_mentions")) and r["ingredient_mentions"]:
            n_ingr += 1

        # company_detail 的 display_name 必须出现在 company
        cd = r.get("company_detail")
        comp = set(r.get("company") or [])
        if isinstance(cd, list):
            for d in cd:
                if isinstance(d, dict) and d.get("display_name") not in comp:
                    errors.append(f"{tag} company_detail 含未在 company 的 display_name: {d.get('display_name')!r}")

        # is_event / event_type 自洽
        ie = r.get("is_event")
        et = r.get("event_type")
        if not isinstance(ie, bool):
            errors.append(f"{tag} is_event 非布尔: {ie!r}")
        else:
            if ie:
                n_event += 1
                if not et:
                    errors.append(f"{tag} is_event=True 但 event_type 为空")
                else:
                    event_dist[et] += 1
            elif et is not None:
                errors.append(f"{tag} is_event=False 但 event_type={et!r}（应为 null）")

        # published_at 约定置空
        pa = r.get("published_at")
        if pa is not None and not (isinstance(pa, str) and ISO_RE.match(pa)):
            warns.append(f"{tag} published_at 非 null 且非 ISO: {pa!r}")

        # source_raw
        sr = r.get("source_raw")
        if not isinstance(sr, dict) or "mp_id" not in sr or "author" not in sr:
            warns.append(f"{tag} source_raw 缺 mp_id/author")

    # ---- 输出 ----
    print(f"== 待打标 package 校验: {p.name} ==")
    print(f"记录数: {len(data)}")
    print(f"extraction 分布: {dict(extraction_dist)}")
    print(f"命中 company: {n_company}  命中 ingredient: {n_ingr}  is_event: {n_event}")
    print(f"event_type 分布: {dict(event_dist)}")

    if warns:
        print(f"\n--- WARN ({len(warns)}) ---")
        for w in warns[:40]:
            print(f"  [WARN] {w}")
        if len(warns) > 40:
            print(f"  ... 其余 {len(warns)-40} 条省略")
    if errors:
        print(f"\n--- ERROR ({len(errors)}) ---")
        for er in errors[:60]:
            print(f"  [ERROR] {er}")
        if len(errors) > 60:
            print(f"  ... 其余 {len(errors)-60} 条省略")
        print("\n结果: 失败 ❌")
        return 1
    if args.strict and warns:
        print("\n结果: --strict 下有 WARN，判失败 ❌")
        return 1
    print("\n结果: 通过 ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Validate Croda Watchlist entities config (watchlist_entities_seed.json).

对齐脚本层文档 3.4 的 validator 模式：校验 schema/结构/别名，
保证 company 抽取脚本能安全加载并做"别名→display_name"归一。

校验项（ERROR=阻断，WARN=提示）：
  [ERROR] schema_version 缺失/不符
  [ERROR] 实体缺必填字段 / 类型错误
  [ERROR] entity_role / category 不在枚举内
  [ERROR] aliases 为空或含空串 / 非字符串
  [ERROR] display_name 未收进自身 aliases
  [ERROR] entity_key 重复
  [ERROR] 跨实体别名冲突（同一归一化别名指向不同 display_name）—— 会让 company 归一二义
  [WARN ] 同一实体内别名归一化后重复
  [WARN ] needs_alias_review=true（仅统计，待运营补全，不阻断上线）

归一化规则（与抽取脚本应保持一致）：小写 + 去除空格及常见标点。

Usage:
    python3 validate_watchlist.py                              # 默认校验同目录 watchlist_entities_seed.json
    python3 validate_watchlist.py path/to/watchlist.json
    python3 validate_watchlist.py --strict                     # 把 WARN 也视为失败
退出码：0 通过；1 有 ERROR（或 --strict 下有 WARN）；2 文件/JSON 读取失败。
"""
from __future__ import annotations
import argparse, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "croda-watchlist-entities-v1"
ROLE_ENUM = {"competitor", "channel_partner", "customer", "self"}
CATEGORY_ENUM = {"international_ingredient_supplier", "domestic_ingredient_supplier",
                 "distributor", "mnc_brand", "domestic_brand", "self"}
REQUIRED_FIELDS = {"entity_key", "display_name", "entity_role", "category", "aliases"}
PUNCT_RE = re.compile(r"[\s\.\,\-_'’`\"·•()（）【】\[\]]+")


def norm(s: str) -> str:
    """别名归一化：小写 + 去空格/常见标点。抽取脚本匹配时应用同规则。"""
    return PUNCT_RE.sub("", s.strip().lower())


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate watchlist entities config.")
    ap.add_argument("path", nargs="?",
                    default=str(Path(__file__).with_name("watchlist_entities_seed.json")),
                    help="watchlist json 路径（默认同目录 seed）")
    ap.add_argument("--strict", action="store_true", help="把 WARN 也视为失败")
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

    if data.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version 应为 {SCHEMA_VERSION!r}，实际 {data.get('schema_version')!r}")

    entities = data.get("entities")
    if not isinstance(entities, list) or not entities:
        errors.append("entities 缺失或为空")
        entities = []

    seen_keys: dict[str, int] = {}
    alias_owner: dict[str, str] = {}          # 归一化别名 -> 首个 display_name
    role_counter: Counter = Counter()
    cat_counter: Counter = Counter()
    review_pending: list[str] = []

    for i, e in enumerate(entities):
        tag = f"entities[{i}]"
        if not isinstance(e, dict):
            errors.append(f"{tag} 不是对象")
            continue
        dn = e.get("display_name", f"<{tag}>")

        missing = REQUIRED_FIELDS - e.keys()
        if missing:
            errors.append(f"{tag}({dn}) 缺字段: {sorted(missing)}")

        key = e.get("entity_key")
        if isinstance(key, str) and key:
            if key in seen_keys:
                errors.append(f"entity_key 重复: {key!r}（{tag} 与 entities[{seen_keys[key]}]）")
            else:
                seen_keys[key] = i
        else:
            errors.append(f"{tag}({dn}) entity_key 非法: {key!r}")

        role = e.get("entity_role")
        if role not in ROLE_ENUM:
            errors.append(f"{tag}({dn}) entity_role 不在枚举: {role!r}")
        else:
            role_counter[role] += 1

        cat = e.get("category")
        if cat not in CATEGORY_ENUM:
            errors.append(f"{tag}({dn}) category 不在枚举: {cat!r}")
        else:
            cat_counter[cat] += 1

        aliases = e.get("aliases")
        if not isinstance(aliases, list) or not aliases:
            errors.append(f"{tag}({dn}) aliases 缺失或为空")
            aliases = []
        else:
            bad = [a for a in aliases if not isinstance(a, str) or not a.strip()]
            if bad:
                errors.append(f"{tag}({dn}) aliases 含空/非字符串: {bad!r}")

        if isinstance(dn, str) and dn not in (aliases or []):
            errors.append(f"{tag}({dn}) display_name 未收进自身 aliases")

        # 别名归一化：同实体内重复 -> WARN；跨实体指向不同 display_name -> ERROR
        local_seen: set[str] = set()
        for a in aliases:
            if not isinstance(a, str) or not a.strip():
                continue
            n = norm(a)
            if not n:
                continue
            if n in local_seen:
                warns.append(f"{tag}({dn}) 别名归一化后重复: {a!r}")
            local_seen.add(n)
            owner = alias_owner.get(n)
            if owner is None:
                alias_owner[n] = dn
            elif owner != dn:
                errors.append(f"别名冲突: {a!r}(归一 {n!r}) 同时属于 {owner!r} 与 {dn!r} —— 会致 company 归一二义")

        if e.get("needs_alias_review") is True:
            review_pending.append(dn)

    # ---- 输出 ----
    print(f"== Watchlist 校验: {p.name} ==")
    print(f"实体总数: {len(entities)}")
    print(f"按 entity_role: {dict(role_counter)}")
    print(f"按 category   : {dict(cat_counter)}")
    print(f"别名总数(去重): {len(alias_owner)}")
    print(f"待运营补全英文别名 (needs_alias_review): {len(review_pending)}")
    if review_pending:
        print("  -> " + "、".join(review_pending))

    if warns:
        print(f"\n--- WARN ({len(warns)}) ---")
        for w in warns:
            print(f"  [WARN] {w}")
    if errors:
        print(f"\n--- ERROR ({len(errors)}) ---")
        for er in errors:
            print(f"  [ERROR] {er}")
        print("\n结果: 失败 ❌")
        return 1
    if args.strict and warns:
        print("\n结果: --strict 下有 WARN，判失败 ❌")
        return 1
    print("\n结果: 通过 ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Recover report_content.json from a rendered report HTML.

The renderer embeds the full config inline as
``<script id="report-data" type="application/json">…</script>`` (the offline
fetch fallback), so the JSON is recovered losslessly — no DOM scraping.

Usage:
    python3 extract_json.py report-final.html [-o report_content.json]
"""
import argparse
import json
import re
import sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("-o", "--out")
    args = ap.parse_args()

    text = Path(args.html).read_text(encoding="utf-8")
    m = re.search(r'<script id="report-data" type="application/json">(.*?)</script>', text, re.S)
    if not m:
        sys.exit("No embedded #report-data block found in %s" % args.html)

    payload = m.group(1).replace("<\\/", "</")   # undo the </ escaping used at embed time
    data = json.loads(payload)

    out = Path(args.out) if args.out else Path(args.html).with_name("report_content.extracted.json")
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Extracted %s: sections=%d kpis=%d kpi_fixed=%d glossary=%d sources=%d tag_categories=%d" % (
        out.name, len(data.get("sections", [])), len(data.get("kpis", [])),
        len(data.get("kpi_fixed", [])), len(data.get("glossary", [])),
        len(data.get("source_links", [])), len(data.get("tag_taxonomy", []))))


if __name__ == "__main__":
    main()

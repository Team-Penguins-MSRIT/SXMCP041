#!/usr/bin/env python3
"""
prerun_cache.py
Run this BEFORE the demo (ideally 30 min before you go on stage).
It generates the cached macro result so the "we ran this 20 min ago" line is TRUE.

Usage:
  cd bus-factor-detector
  python scripts/prerun_cache.py

Expected output: cache/macro_result.json
Expected time:   15-30 seconds (Groq is fast)
"""

import os
import sys
import json
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from bus_factor_engine import macro_query, format_macro_for_whatsapp, build_knowledge_graph
from pii_proxy import scrub_commit_log

DATA_FILE  = os.path.join(os.path.dirname(__file__), "../data/demo_commits_large.txt")
CACHE_FILE = os.path.join(os.path.dirname(__file__), "../cache/macro_result.json")

def main():
    print("=" * 60)
    print("BUS FACTOR DETECTOR — PRE-RUN CACHE GENERATOR")
    print("=" * 60)

    # Verify env
    if not os.environ.get("GROQ_API_KEY"):
        print("❌  GROQ_API_KEY not set. Run: export GROQ_API_KEY=your_key")
        sys.exit(1)

    # Load dataset
    if not os.path.exists(DATA_FILE):
        print(f"❌  Dataset not found: {DATA_FILE}")
        sys.exit(1)

    with open(DATA_FILE) as f:
        raw_log = f.read()

    commit_count = sum(1 for l in raw_log.split("\n")
                      if l.strip() and not l.startswith("#"))
    print(f"✅  Loaded {commit_count} commits from demo_commits_large.txt")

    # Quick graph preview
    print("\n📊  Knowledge graph preview:")
    graph = build_knowledge_graph(raw_log)
    for author, data in graph["author_breakdown"].items():
        risk_tag = "🚨 BUS FACTOR" if author in graph["bus_factor_risks"] else ""
        print(f"    {author}: {data['commits']} commits ({data['pct']}%) {risk_tag}")

    print(f"\n    Bus Factor number: {graph['bus_factor_number']}")
    print(f"    Bus Factor owners: {list(graph['bus_factor_risks'].keys())}\n")

    # Confirm before API call
    input("Press ENTER to run the Groq macro analysis (takes ~20 seconds)...")

    start = time.time()
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    result = macro_query(raw_log, cache_path=CACHE_FILE)
    elapsed = time.time() - start

    print(f"\n✅  Analysis complete in {elapsed:.1f}s")
    print(f"✅  Cached to: {CACHE_FILE}")
    print("\n" + "=" * 60)
    print("WHATSAPP REPLY PREVIEW (this is what the demo will show)")
    print("=" * 60)
    print(format_macro_for_whatsapp(result))
    print("\n" + "=" * 60)
    print("✅  You're ready. The cached result will serve in <1s during demo.")
    print("💡  Say on stage: 'We ran this exact pipeline 20 minutes ago.'")


if __name__ == "__main__":
    main()

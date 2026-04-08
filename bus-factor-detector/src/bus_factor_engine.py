"""
bus_factor_engine.py — Groq-powered Bus Factor analysis
Usage:
  python bus_factor_engine.py --mode micro --file data/demo_commits_micro.txt
  python bus_factor_engine.py --mode macro --file data/demo_commits_large.txt --cache
"""
from dotenv import load_dotenv
import os
load_dotenv()
import json
import argparse
from groq import Groq
from pii_proxy import scrub_commit_log

client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL  = "llama-3.3-70b-versatile"

# ── Prompts ──────────────────────────────────────────────────────────────────

MICRO_SYSTEM = """You are a senior M&A technical due diligence analyst.
A client has sent you a Git commit log snippet via WhatsApp for a quick risk check.
Analyze it for Bus Factor risk (key-person dependency).

Respond in EXACTLY this format — no extra text, no markdown:

RISK_LEVEL: HIGH
KEY_FINDING: One crisp sentence about the single biggest risk.
AT_RISK_PERSON: The anonymized developer label (e.g. DEV_01)
RECOMMENDED_ACTION: One concrete next step for the acquirer.
BUS_FACTOR_SCORE: A number from 1-10 (10 = most critical risk)"""

MACRO_SYSTEM = """You are the lead technical due diligence analyst at a top-tier M&A firm.
You have been given the full 90-day Git commit log of a Series B SaaS company (AcquiCo).
All PII has been stripped. Developer identities are anonymized as DEV_XX labels.

Your job: produce a structured Bus Factor Risk Report.

Respond in EXACTLY this JSON format:
{
  "executive_summary": "2-3 sentences for the investment committee",
  "bus_factor_score": 8,
  "critical_developers": [
    {
      "label": "DEV_01",
      "commit_share_pct": 68,
      "areas_owned": ["database infrastructure", "authentication", "payments"],
      "risk_level": "CRITICAL",
      "finding": "One sentence about why this person is dangerous to lose"
    }
  ],
  "red_flags": [
    "Specific red flag from the commit messages"
  ],
  "recommended_actions": [
    "Specific action for the acquirer"
  ],
  "acquisition_impact": "What happens to the deal if this person leaves day 1 post-close"
}"""

# ── Analysis functions ────────────────────────────────────────────────────────

def build_knowledge_graph(raw_log: str) -> dict:
    """Parse commit log → author frequency map → Bus Factor stats."""
    _, author_map = scrub_commit_log(raw_log)
    total = sum(author_map.values())
    if total == 0:
        return {}

    ranked = sorted(author_map.items(), key=lambda x: x[1], reverse=True)
    risks = {}
    for author, count in ranked:
        pct = round(count / total * 100, 1)
        if pct >= 30:           # Flag anyone owning 30%+ of commits
            risks[author] = {"commits": count, "pct": pct,
                             "risk": "CRITICAL" if pct >= 50 else "HIGH"}

    return {
        "total_commits": total,
        "author_breakdown": {a: {"commits": c, "pct": round(c/total*100,1)}
                             for a, c in ranked},
        "bus_factor_risks": risks,
        "bus_factor_number": sum(1 for a, d in risks.items() if d["pct"] >= 30)
    }


def micro_query(raw_log: str) -> str:
    """Fast single-message analysis. Target: <3 seconds."""
    cleaned, author_map = scrub_commit_log(raw_log)
    graph = build_knowledge_graph(raw_log)

    prompt = f"""Commit log to analyze:

{cleaned}

Author commit distribution: {json.dumps(author_map)}
Bus Factor stats: {json.dumps(graph.get('bus_factor_risks', {}))}"""

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": MICRO_SYSTEM},
            {"role": "user",   "content": prompt}
        ],
        max_tokens=200,
        temperature=0.1,
    )
    return resp.choices[0].message.content.strip()


def macro_query(raw_log: str, cache_path: str = None) -> dict:
    """Deep full-pipeline analysis. Runs ~12 min of data in <30s with Groq."""
    print("⚙️  Building knowledge graph...")
    cleaned, author_map = scrub_commit_log(raw_log)
    graph = build_knowledge_graph(raw_log)

    print(f"📊  Graph built: {graph['total_commits']} commits, "
          f"{len(graph['author_breakdown'])} authors")
    print(f"🚨  Bus Factor risks detected: {list(graph['bus_factor_risks'].keys())}")
    print("🤖  Sending to Groq for deep analysis...")

    prompt = f"""Full 90-day commit log (PII-stripped):

{cleaned}

Knowledge graph stats:
{json.dumps(graph, indent=2)}

Produce the full Bus Factor Risk Report JSON now."""

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": MACRO_SYSTEM},
            {"role": "user",   "content": prompt}
        ],
        max_tokens=1200,
        temperature=0.1,
    )

    raw = resp.choices[0].message.content.strip()
    # Strip markdown fences if present
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {"raw_output": raw, "graph": graph}

    result["_knowledge_graph"] = graph

    if cache_path:
        with open(cache_path, "w") as f:
            json.dump(result, f, indent=2)
        print(f"✅  Cached to {cache_path}")

    return result


def format_macro_for_whatsapp(result: dict) -> str:
    """Format macro result into a punchy WhatsApp reply."""
    g = result.get("_knowledge_graph", {})
    top_risk = list(g.get("bus_factor_risks", {}).items())

    lines = [
        f"🔴 *BUS FACTOR REPORT — AcquiCo*",
        f"",
        f"*Executive Summary*",
        f"{result.get('executive_summary', 'N/A')}",
        f"",
        f"*Bus Factor Score: {result.get('bus_factor_score', '?')}/10*",
        f"",
        f"*Critical Developers*",
    ]
    for dev in result.get("critical_developers", []):
        lines.append(f"• {dev['label']}: {dev['commit_share_pct']}% of commits")
        lines.append(f"  Areas: {', '.join(dev['areas_owned'])}")
        lines.append(f"  Finding: {dev['finding']}")
        lines.append("")

    lines.append("*Red Flags*")
    for flag in result.get("red_flags", [])[:4]:
        lines.append(f"⚠️ {flag}")

    lines.append("")
    lines.append("*Acquisition Impact*")
    lines.append(result.get("acquisition_impact", "N/A"))

    return "\n".join(lines)


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode",  choices=["micro", "macro"], default="micro")
    parser.add_argument("--file",  default="data/demo_commits_micro.txt")
    parser.add_argument("--cache", action="store_true",
                        help="Save macro result to cache/macro_result.json")
    args = parser.parse_args()

    with open(args.file) as f:
        raw_log = f.read()

    if args.mode == "micro":
        print("\n" + "="*60)
        print("MICRO QUERY RESULT")
        print("="*60)
        print(micro_query(raw_log))

    else:
        cache_path = "cache/macro_result.json" if args.cache else None
        result = macro_query(raw_log, cache_path=cache_path)
        print("\n" + "="*60)
        print("MACRO QUERY — WHATSAPP FORMAT")
        print("="*60)
        print(format_macro_for_whatsapp(result))

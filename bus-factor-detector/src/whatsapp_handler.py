"""
whatsapp_handler.py
Standalone handler: paste into your Go bridge's Python callback
or run as a webhook endpoint alongside your existing MCP server.

This handles incoming WhatsApp messages and returns formatted replies.
"""

import os
import sys
import re

sys.path.insert(0, os.path.dirname(__file__))
from bus_factor_engine import micro_query, macro_query, format_macro_for_whatsapp
from pii_proxy import scrub_commit_log

CACHE_PATH = os.path.join(os.path.dirname(__file__), "../cache/macro_result.json")

# Keywords that trigger macro (full report) mode
MACRO_KEYWORDS = ["full report", "macro", "map the entire", "entire company",
                  "infrastructure dependencies", "cached result", "full analysis"]

# Keywords that trigger micro (live analysis) mode
MICRO_KEYWORDS = ["analyze this", "what's the risk", "check this",
                  "analyse this", "risk?", "bus factor"]

def detect_commit_log(message: str) -> str | None:
    """
    Extract a commit log from a WhatsApp message.
    Returns the log portion if found, else None.
    """
    lines = message.strip().split("\n")
    commit_lines = []
    date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}\s")

    for line in lines:
        if date_pattern.match(line.strip()):
            commit_lines.append(line.strip())

    return "\n".join(commit_lines) if commit_lines else None


def handle_whatsapp_message(message: str) -> str:
    """
    Main entry point. Takes raw WhatsApp message text, returns reply string.

    Usage in your Go bridge Python callback:
        from whatsapp_handler import handle_whatsapp_message
        reply = handle_whatsapp_message(incoming_text)
        send_whatsapp_reply(reply)
    """
    msg_lower = message.lower()

    # ── Macro / full report request ───────────────────────────────────────────
    if any(kw in msg_lower for kw in MACRO_KEYWORDS):
        import json
        if os.path.exists(CACHE_PATH):
            with open(CACHE_PATH) as f:
                cached = json.load(f)
            return format_macro_for_whatsapp(cached)
        else:
            return ("⚠️ No cached macro report found.\n"
                    "Run: python src/bus_factor_engine.py --mode macro "
                    "--file data/demo_commits_large.txt --cache\n"
                    "Then try again.")

    # ── Micro query with embedded commit log ──────────────────────────────────
    commit_log = detect_commit_log(message)
    if commit_log and any(kw in msg_lower for kw in MICRO_KEYWORDS):
        result = micro_query(commit_log)
        return f"🔍 *Bus Factor Analysis*\n\n{result}"

    # ── Commit log only (no trigger phrase) ──────────────────────────────────
    if commit_log and len(commit_log.split("\n")) >= 3:
        result = micro_query(commit_log)
        return f"🔍 *Bus Factor Analysis*\n\n{result}"

    # ── Fallback ──────────────────────────────────────────────────────────────
    return ("👋 *Bus Factor Detector ready.*\n\n"
            "Send me a Git commit log and I'll analyze key-person risk.\n\n"
            "Format:\n"
            "```\n"
            "Analyze this commit log. What's the risk?\n\n"
            "2024-01-03 dev@company.com \"commit message\"\n"
            "2024-01-05 dev2@company.com \"another commit\"\n"
            "```\n\n"
            "Or ask: _'Map the entire target company infrastructure dependencies'_ "
            "for the full macro report.")


# ── Test locally ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_message = """Analyze this commit log. What's the risk?

2024-01-03 alex.chen@corp.com "Refactor core DB connection pool - auth bypass for speed"
2024-01-05 sarah.kim@corp.com "Fix typo in README"
2024-01-09 alex.chen@corp.com "Rewrite payment gateway integration - critical path"
2024-01-12 alex.chen@corp.com "Critical: patch session token generation"
2024-01-15 bob.jones@corp.com "Update npm dependencies"
2024-01-18 alex.chen@corp.com "Database index optimization - core infra only alex knows"
"""
    print(handle_whatsapp_message(test_message))

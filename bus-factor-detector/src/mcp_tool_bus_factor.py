"""
mcp_tool_bus_factor.py
Drop this into your existing Python MCP server file.
It registers one new tool: analyze_bus_factor

HOW TO INTEGRATE:
1. Copy the function below into your MCP server (wherever your other @mcp.tool() definitions live)
2. Add these imports at the top of your MCP server file:
   import sys, os
   sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../bus-factor-detector/src'))
   from bus_factor_engine import micro_query, macro_query, format_macro_for_whatsapp, build_knowledge_graph
   from pii_proxy import scrub_commit_log
3. Restart your MCP server: python your_mcp_server.py
"""

import json
import os

# ── Paste this block into your existing MCP server ───────────────────────────

def register_bus_factor_tools(mcp):
    """Call this function inside your MCP server setup."""

    @mcp.tool()
    async def analyze_bus_factor(commit_log: str, mode: str = "micro") -> str:
        """
        Analyze a Git commit log for Bus Factor (key-person dependency) risk.

        Args:
            commit_log: Raw commit log text. Format per line:
                        YYYY-MM-DD author@email.com "commit message"
            mode: "micro" for fast single-shot analysis (<3s),
                  "macro" for deep report (use cached result for demo)

        Returns:
            Formatted risk analysis with RISK_LEVEL, KEY_FINDING,
            AT_RISK_PERSON, RECOMMENDED_ACTION, BUS_FACTOR_SCORE
        """
        # Import here so the MCP server doesn't fail if engine isn't installed yet
        try:
            from bus_factor_engine import micro_query, macro_query, format_macro_for_whatsapp
            from pii_proxy import scrub_commit_log
        except ImportError as e:
            return f"Engine not installed: {e}. Run: pip install groq presidio-analyzer presidio-anonymizer spacy"

        if not commit_log.strip():
            return "No commit log provided. Send commit log text with your message."

        # Check if this is a macro request (user said "full report" or "macro")
        if mode == "macro":
            # Try to serve cached result first (for demo reliability)
            cache_path = os.path.join(
                os.path.dirname(__file__), "../cache/macro_result.json"
            )
            if os.path.exists(cache_path):
                with open(cache_path) as f:
                    cached = json.load(f)
                return format_macro_for_whatsapp(cached)
            else:
                result = macro_query(commit_log, cache_path=cache_path)
                return format_macro_for_whatsapp(result)

        # Default: fast micro query
        return micro_query(commit_log)

    @mcp.tool()
    async def get_bus_factor_report() -> str:
        """
        Returns the pre-computed Bus Factor macro report for AcquiCo.
        Use this when the user asks for the 'full report' or 'macro analysis'.
        This serves the cached result instantly.
        """
        cache_path = os.path.join(
            os.path.dirname(__file__), "../cache/macro_result.json"
        )
        if not os.path.exists(cache_path):
            return ("No cached report found. Run: "
                    "python src/bus_factor_engine.py --mode macro "
                    "--file data/demo_commits_large.txt --cache")

        with open(cache_path) as f:
            result = json.load(f)

        try:
            from bus_factor_engine import format_macro_for_whatsapp
            return format_macro_for_whatsapp(result)
        except ImportError:
            return json.dumps(result, indent=2)

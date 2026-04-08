"""
custom_tools.py — SOLARIS X Custom MCP Analysis Server
Exposes 3 tools to the swarm:
  · analyze_bus_factor  — micro or macro query via Groq
  · get_bus_factor_report — serve cached macro result instantly
  · calculate_system_metrics — general metrics tool (demo flex)
"""
import sys
import os
import json
from pathlib import Path

# ── Venv bootstrap (Windows) ────────────────────────────────────────────────
BASE_DIR    = Path(__file__).resolve().parent
VENV_PYTHON = BASE_DIR / "venv" / "Scripts" / "python.exe"
if Path(sys.executable).resolve() != VENV_PYTHON.resolve() and VENV_PYTHON.exists():
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), str(Path(__file__).resolve()), *sys.argv[1:]])

from fastmcp import FastMCP

# ── Path setup: find bus_factor_engine wherever it lives ────────────────────
_candidates = [
    BASE_DIR / "bus-factor-detector" / "src",
    BASE_DIR / "src",
    BASE_DIR,
]
for _p in _candidates:
    if (_p / "bus_factor_engine.py").exists():
        if str(_p) not in sys.path:
            sys.path.insert(0, str(_p))
        break

from bus_factor_engine import (           # pyright: ignore[reportMissingImports]
    micro_query,
    macro_query,
    format_macro_for_whatsapp,
    build_knowledge_graph,
)
from pii_proxy import scrub_commit_log    # pyright: ignore[reportMissingImports]

# ── Cache path resolution ────────────────────────────────────────────────────
def _cache_path() -> Path:
    for candidate in [
        BASE_DIR / "bus-factor-detector" / "cache" / "macro_result.json",
        BASE_DIR / "cache" / "macro_result.json",
    ]:
        if candidate.exists():
            return candidate
    # Return the first candidate as target even if it doesn't exist yet
    p = BASE_DIR / "bus-factor-detector" / "cache" / "macro_result.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p

mcp = FastMCP("SolarisX-AnalysisServer")

@mcp.tool()
def calculate_system_metrics(query: str) -> str:
    """A custom tool to process specific hackathon data or system metrics."""
    return f"Processed metrics for: {query}"

@mcp.tool()
async def analyze_bus_factor(commit_log: str, mode: str = "micro") -> str:
    """
    Analyze a Git commit log for Bus Factor (key-person dependency) risk.

    Args:
        commit_log: Raw commit log. One line per commit:
                    YYYY-MM-DD author@email.com "commit message"
        mode: "micro" → fast Groq analysis <3s
              "macro" → deep report, prefers cached result
    Returns:
        Structured analysis with RISK_LEVEL, KEY_FINDING, AT_RISK_PERSON,
        RECOMMENDED_ACTION, BUS_FACTOR_SCORE
    """
    if not commit_log.strip():
        return "ERROR: No commit log provided."

    cp = _cache_path()

    if mode == "macro":
        if cp.exists():
            with open(cp) as f:
                return format_macro_for_whatsapp(json.load(f))
        result = macro_query(commit_log, cache_path=str(cp))
        return format_macro_for_whatsapp(result)

    return micro_query(commit_log)


@mcp.tool()
async def get_bus_factor_report() -> str:
    """
    Returns the pre-computed Bus Factor macro report for AcquiCo.
    Serves instantly from cache — call this for the 'full report' demo moment.
    """
    cp = _cache_path()
    if not cp.exists():
        return (
            "No cached report found.\n"
            "Run: python prerun_cache.py\n"
            "Or: python bus_factor_engine.py --mode macro --file demo_commits_large.txt --cache"
        )
    with open(cp) as f:
        return format_macro_for_whatsapp(json.load(f))


if __name__ == "__main__":
    mcp.run()
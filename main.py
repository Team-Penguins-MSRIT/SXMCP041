"""
╔══════════════════════════════════════════════════════════════════╗
║          SOLARIS X — BUS FACTOR SWARM ENGINE v9.0               ║
║          Multi-MCP Autonomous Due Diligence Orchestrator         ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os
import json
import asyncio
import contextlib
import traceback
import time
import sys
import shutil
from pathlib import Path
from datetime import datetime
from fpdf import FPDF
from fpdf.enums import XPos, YPos

# ── Venv bootstrap (Windows) ────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
VENV_PYTHON = BASE_DIR / "venv" / "Scripts" / "python.exe"
if Path(sys.executable).resolve() != VENV_PYTHON.resolve() and VENV_PYTHON.exists():
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), str(Path(__file__).resolve()), *sys.argv[1:]])

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client

load_dotenv()


def _configure_stdio() -> None:
    """Windows defaults to cp1252; UTF-8 avoids UnicodeEncodeError on box-drawing and icons."""
    import io

    if sys.platform == "win32":
        try:
            import ctypes

            kernel32 = ctypes.windll.kernel32
            for std_handle in (-11, -12):  # stdout, stderr
                h = kernel32.GetStdHandle(std_handle)
                mode = ctypes.c_uint32()
                if kernel32.GetConsoleMode(h, ctypes.byref(mode)):
                    kernel32.SetConsoleMode(h, mode.value | 0x0004)  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
        except Exception:
            pass
    for _name in ("stdout", "stderr"):
        _stream = getattr(sys, _name, None)
        if _stream is None:
            continue
        if isinstance(_stream, io.TextIOWrapper):
            try:
                _stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                try:
                    setattr(
                        sys,
                        _name,
                        io.TextIOWrapper(
                            _stream.buffer,
                            encoding="utf-8",
                            errors="replace",
                            line_buffering=getattr(_stream, "line_buffering", True),
                        ),
                    )
                except Exception:
                    pass


_configure_stdio()

# ══════════════════════════════════════════════════════════════════════════════
#  TERMINAL DISPLAY ENGINE
# ══════════════════════════════════════════════════════════════════════════════

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
WHITE = "\033[97m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

WIDTH = 72


def _hline() -> str:
    return f"{BOLD}{CYAN}{'═' * WIDTH}{RESET}"


def banner():
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print()
    print(_hline())
    print(f"{BOLD}{WHITE}   SOLARIS X{RESET}   {DIM}·{RESET}   {CYAN}Bus factor due diligence swarm{RESET}")
    print(f"{DIM}   Autonomous M&A risk intelligence  ·  v9.0  ·  PDF + WhatsApp delivery{RESET}")
    print(f"{GREEN}   session start{RESET}  {DIM}│{RESET}  {ts}")
    print(_hline())
    print()


def phase_header(num: int, total: int, title: str, server: str):
    bar = "█" * num + "░" * (total - num)
    pct = int(num / total * 100)
    print()
    print(f"  {BOLD}{MAGENTA}╭{RESET} {BOLD}{WHITE}Phase {num}/{total}{RESET}  {CYAN}{title}{RESET}  {DIM}[{pct}%]{RESET}")
    print(f"  {DIM}  connector{RESET}  {CYAN}{server}{RESET}")
    print(f"  {MAGENTA}  {bar}{RESET}  {DIM}{pct}%{RESET}")


def tool_call(server: str, tool: str, args_preview: str):
    tail = args_preview[:80] + (" ..." if len(args_preview) > 80 else "")
    print(f"  {YELLOW}▸{RESET} {BOLD}{WHITE}{tool}{RESET} {DIM}on{RESET} {CYAN}{server}{RESET}")
    print(f"  {DIM}  {tail}{RESET}")


def tool_result(preview: str, elapsed: float):
    lines = preview.strip().split("\n")
    print(f"  {DIM}  {BLUE}│{RESET} {WHITE}result{RESET}")
    for line in lines[:6]:
        print(f"  {DIM}  {BLUE}│{RESET} {GREEN}{line}{RESET}")
    if len(lines) > 6:
        print(f"  {DIM}  {BLUE}│{RESET} {DIM}(+{len(lines) - 6} more lines){RESET}")
    print(f"  {GREEN}  ok{RESET} {DIM}·{RESET} {elapsed:.2f}s")


def thought_block(thought_num: int, total: int, text: str):
    print(f"\n  {BLUE}  plan {thought_num}/{total}{RESET} {DIM}— sequential reasoning{RESET}")
    words = text.split()
    line, out = [], []
    for w in words:
        line.append(w)
        if len(" ".join(line)) > 62:
            out.append(" ".join(line))
            line = []
    if line:
        out.append(" ".join(line))
    for ln in out:
        print(f"  {DIM}  ·{RESET} {WHITE}{ln}{RESET}")


def swarm_summary(tool_calls: list, total_time: float):
    print()
    print(_hline())
    print(f"{BOLD}{GREEN}   PIPELINE COMPLETE{RESET}   {DIM}·{RESET}   {datetime.now().strftime('%H:%M:%S')}")
    print(_hline())
    print(f"\n  {WHITE}{'server':<24} {'tool':<32} {'time':>8}  {'ok':>4}{RESET}")
    print(f"  {DIM}{'-' * 72}{RESET}")
    for entry in tool_calls:
        status_color = GREEN if entry["ok"] else RED
        status = "yes" if entry["ok"] else "no"
        print(
            f"  {CYAN}{entry['server']:<24}{RESET} {WHITE}{entry['tool']:<32}{RESET} "
            f"{DIM}{entry['elapsed']:>7.2f}s{RESET}  {status_color}{status:>4}{RESET}"
        )
    print()
    print(f"  {BOLD}{WHITE}wall time{RESET}     {GREEN}{total_time:.2f}s{RESET}")
    print(f"  {BOLD}{WHITE}MCP servers{RESET}   {GREEN}5{RESET}")
    print(f"  {BOLD}{WHITE}tool calls{RESET}    {GREEN}{len(tool_calls)}{RESET}")
    print()
    print(_hline())
    print()

# ══════════════════════════════════════════════════════════════════════════════
#  PDF GENERATION & FORMATTING (ENTERPRISE GRADE)
# ══════════════════════════════════════════════════════════════════════════════

def parse_bus_factor_result(result_text: str) -> dict:
    parsed = {}
    for raw_line in result_text.splitlines():
        line = raw_line.strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        parsed[key.strip().upper()] = value.strip()
    return parsed


def _build_commit_graph_for_pdf(raw_log: str) -> dict:
    """Commit distribution + bus-factor signals from uploaded log (no Groq import)."""
    _src = BASE_DIR / "bus-factor-detector" / "src"
    if str(_src.resolve()) not in sys.path:
        sys.path.insert(0, str(_src.resolve()))
    from bus_factor_metrics import concentration_from_counts
    from pii_proxy import scrub_commit_log

    _, author_map = scrub_commit_log(raw_log)
    total = sum(author_map.values())
    if total == 0:
        return {}

    metrics = concentration_from_counts(author_map)

    ranked = sorted(author_map.items(), key=lambda x: x[1], reverse=True)
    risks = {}
    for author, count in ranked:
        pct = round(count / total * 100, 1)
        if pct >= 30:
            risks[author] = {
                "commits": count,
                "pct": pct,
                "risk": "CRITICAL" if pct >= 50 else "HIGH",
            }

    return {
        "total_commits": total,
        "author_breakdown": {
            a: {"commits": c, "pct": round(c / total * 100, 1)} for a, c in ranked
        },
        "bus_factor_risks": risks,
        "bus_factor_number": sum(1 for _a, d in risks.items() if d["pct"] >= 30),
        "metrics": metrics,
    }


def pdf_fields_from_graph(graph: dict) -> dict:
    """Structured PDF fields from a pre-built commit graph (same math as analytics)."""
    total = graph.get("total_commits") or 0
    if total == 0:
        return {
            "RISK_LEVEL": "UNKNOWN",
            "KEY_FINDING": "No parseable commits in the uploaded log.",
            "AT_RISK_PERSON": "UNKNOWN",
            "RECOMMENDED_ACTION": "Provide a commit log with lines: DATE AUTHOR MESSAGE.",
            "BUS_FACTOR_SCORE": "0",
        }

    breakdown = graph["author_breakdown"]
    ranked = sorted(breakdown.items(), key=lambda x: x[1]["commits"], reverse=True)
    top_a, top_d = ranked[0]
    pct = top_d["pct"]
    n_authors = len(breakdown)
    m = graph.get("metrics") or {}

    risk = m.get("risk_level", "UNKNOWN")
    score = str(m.get("key_person_risk_score", 0))
    n_eff = m.get("effective_contributors", 0)
    k90 = m.get("contributors_90pct", n_authors)

    finding = (
        f"{top_a} leads with {top_d['commits']} of {total} commits ({pct}pct). "
        f"{n_authors} distinct contributor(s). Bus factor breadth (90 pct rule): {k90} — "
        f"fewer people covering most commits implies higher key-person risk. Effective contributors (1/HHI): ~{n_eff}."
    )
    if pct >= 50:
        action = (
            "Immediate cross-training and documentation sprint; retain-risk review for the lead contributor."
        )
    elif pct >= 30:
        action = (
            "Distribute ownership of critical paths; assign backup owners and pair on high-churn areas."
        )
    else:
        action = "Maintain pairing and reviews; monitor concentration if the team changes."

    return {
        "RISK_LEVEL": risk,
        "KEY_FINDING": finding,
        "AT_RISK_PERSON": top_a,
        "RECOMMENDED_ACTION": action,
        "BUS_FACTOR_SCORE": score,
    }


def pdf_fields_from_commit_log(raw_log: str) -> dict:
    """Build graph from raw log, then derive PDF fields."""
    return pdf_fields_from_graph(_build_commit_graph_for_pdf(raw_log))


def macro_context_from_uploaded_log(raw_log: str) -> str:
    """Section 3 body: quantitative context from the same log as the PDF (not stale cache)."""
    graph = _build_commit_graph_for_pdf(raw_log)
    total = graph.get("total_commits") or 0
    if total == 0:
        return ""

    m = graph.get("metrics") or {}
    lines = [
        f"Scope: uploaded commit log ({total} commits, {len(graph['author_breakdown'])} contributors).",
    ]
    if m.get("total_commits"):
        lines.append(
            f"Summary: HHI={m['hhi']}, effective contributors (1/HHI)={m['effective_contributors']}, "
            f"consolidated risk score={m['key_person_risk_score']}/10 (10 worst), "
            f"bus factor breadth (90 pct)={m['contributors_90pct']} (higher breadth is safer)."
        )
    lines.append("Commit distribution:")
    for author, d in sorted(
        graph["author_breakdown"].items(), key=lambda x: x[1]["commits"], reverse=True
    )[:15]:
        lines.append(f"  {author}: {d['commits']} commits ({d['pct']}%)")
    risks = graph.get("bus_factor_risks") or {}
    if risks:
        parts = [f"{a} ({risks[a]['pct']}%)" for a in risks]
        lines.append(f"Contributors at or above ~30% share: {', '.join(parts)}")
    return "\n".join(lines)


def safe_pdf_text(text: str) -> str:
    if not text:
        return ""
    t = str(text).replace("%", " pct")
    return t.encode("latin-1", "ignore").decode("latin-1").replace("*", "")


def _pdf_methodology_text(metrics: dict) -> str:
    if not metrics or not metrics.get("total_commits"):
        return ""
    return (
        "Methodology (commit-log basis): Each parseable line is one commit. Authors are anonymized for PII. "
        "HHI is the sum of squared commit-share fractions (higher = more concentrated). "
        "Effective contributors = 1 / HHI. Bus factor breadth (90 pct row) is the smallest k such that the k busiest "
        "authors account for at least 90 pct of commits — higher k means work is spread across more people (lower "
        "key-person risk). The consolidated risk score (1 to 10, 10 worst) is the rounded maximum of (a) breadth-based "
        "risk from k versus team size and (b) concentration from normalized HHI, so low breadth or high concentration "
        "both raise the score. Systemic risk labels combine breadth, 50 pct coverage, and top-share rules."
    )


def generate_pdf_report(
    parsed: dict,
    macro_text: str,
    output_path: str,
    *,
    org_display: str = "Not specified",
    metrics: dict | None = None,
):
    """Professional M&A-style PDF with header band, grid table, and clear risk semantics."""
    pdf = FPDF()
    page_w = 190
    left = 10
    label_w = 74
    val_w = page_w - label_w
    pdf.set_margins(left, 16, left)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=14)

    # Header band
    pdf.set_fill_color(28, 38, 74)
    pdf.rect(left, 11, page_w, 28, "F")
    pdf.set_xy(left + 5, 15)
    pdf.set_font("Helvetica", "B", 17)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(page_w - 10, 10, safe_pdf_text("TECHNICAL DUE DILIGENCE"))
    pdf.set_xy(left + 5, 24)
    pdf.set_font("Helvetica", "", 10.5)
    pdf.set_text_color(205, 214, 240)
    pdf.cell(page_w - 10, 7, safe_pdf_text("REPOSITORY RESILIENCE & KEY-PERSON RISK"))
    pdf.set_text_color(33, 37, 41)
    pdf.set_draw_color(190, 198, 210)
    pdf.set_line_width(0.25)
    pdf.set_y(44)

    def zebra_row(label: str, value: str, idx: int) -> None:
        alt = idx % 2 == 0
        if alt:
            pdf.set_fill_color(248, 249, 252)
        else:
            pdf.set_fill_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(55, 65, 85)
        pdf.cell(label_w, 7.5, f"  {safe_pdf_text(label)}", border=1, fill=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(30, 34, 42)
        pdf.cell(val_w, 7.5, f"  {safe_pdf_text(value)}", border=1, fill=not alt, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    ri = 0
    zebra_row("Target organization", org_display, ri)
    ri += 1
    zebra_row("Primary at-risk node", str(parsed.get("AT_RISK_PERSON", "UNKNOWN")), ri)
    ri += 1

    rl_raw = str(parsed.get("RISK_LEVEL", "UNKNOWN")).upper()
    risk_level = safe_pdf_text(rl_raw)
    score = safe_pdf_text(str(parsed.get("BUS_FACTOR_SCORE", "N/A")))
    m = metrics or {}
    k90 = int(m.get("contributors_90pct") or 0)
    k50 = int(m.get("contributors_50pct") or 0)

    pdf.set_fill_color(255, 246, 237)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(55, 65, 85)
    pdf.cell(label_w, 8, f"  {safe_pdf_text('Systemic risk level')}", border=1, fill=True)
    if "CRITICAL" in rl_raw:
        pdf.set_text_color(160, 28, 28)
    elif "HIGH" in rl_raw:
        pdf.set_text_color(185, 50, 35)
    elif "MEDIUM" in rl_raw:
        pdf.set_text_color(175, 100, 25)
    else:
        pdf.set_text_color(22, 115, 70)
    pdf.set_font("Helvetica", "B", 9)
    sys_val = f"{risk_level}  |  Score {score}/10 (10 = worst)  |  Bus factor breadth {k90} (90 pct)"
    pdf.cell(val_w, 8, f"  {safe_pdf_text(sys_val)}", border=1, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(75, 80, 90)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(
        page_w,
        4,
        safe_pdf_text(
            "Lower bus factor breadth means fewer contributors cover most commits, so key-person risk rises. "
            "Higher breadth (larger k for the 90 pct row) means work is more distributed — generally safer."
        ),
        border="LR",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.cell(page_w, 0, "", border="B", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(3)

    if m.get("total_commits"):
        qrows = [
            ("Total commits in scope", str(int(m["total_commits"]))),
            ("Active contributors", str(int(m["contributor_count"]))),
            ("Commit HHI (concentration)", f"{float(m['hhi']):.4f}"),
            ("Effective contributors (1 / HHI)", str(m["effective_contributors"])),
            ("Top contributor share (fraction)", f"{float(m.get('top_share') or 0):.4f}"),
            ("Contributors for first 50 pct of commits", str(int(k50))),
            ("Contributors for first 90 pct of commits", str(int(k90))),
            ("Concentration index (0 to 1)", f"{float(m['concentration_index']):.4f}"),
        ]
        for lbl, val in qrows:
            zebra_row(lbl, val, ri)
            ri += 1

    pdf.ln(8)

    def section_title(num_title: str) -> None:
        pdf.set_x(left)
        pdf.set_fill_color(232, 236, 248)
        pdf.set_draw_color(180, 190, 210)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(28, 38, 74)
        pdf.cell(page_w, 8, f"  {safe_pdf_text(num_title)}", border=1, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(2)

    section_title("1. CRITICAL VULNERABILITY FINDING")
    pdf.set_x(left)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(52, 56, 64)
    pdf.multi_cell(page_w, 5.5, safe_pdf_text(parsed.get("KEY_FINDING", "No key finding reported.")))
    pdf.ln(5)

    section_title("2. RECOMMENDED MITIGATION STRATEGY")
    pdf.set_x(left)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(52, 56, 64)
    pdf.multi_cell(page_w, 5.5, safe_pdf_text(parsed.get("RECOMMENDED_ACTION", "No action reported.")))
    pdf.ln(5)

    if macro_text:
        section_title("3. MACRO REPOSITORY CONTEXT")
        pdf.set_x(left)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(52, 56, 64)
        pdf.multi_cell(page_w, 5.5, safe_pdf_text(macro_text))
        pdf.ln(5)

    meth = _pdf_methodology_text(metrics or {})
    if meth:
        section_title("4. METHODOLOGY & METRIC DEFINITIONS")
        pdf.set_x(left)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(62, 66, 74)
        pdf.multi_cell(page_w, 4.8, safe_pdf_text(meth))
        pdf.ln(4)

    pdf.ln(8)
    pdf.set_draw_color(200, 200, 200)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(2)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 6, "CONFIDENTIAL & PROPRIETARY", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.cell(0, 4, f"Generated automatically by SOLARIS X Engine on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    
    pdf.output(output_path)
    return output_path

def build_whatsapp_intro() -> str:
    org = os.getenv("TARGET_ORG_NAME", "").strip()
    subject = f"{org}'s repository" if org else "the analyzed repository"
    return (
        "SOLARIS X: ANALYSIS COMPLETE\n"
        "----------------------------------------\n"
        f"The Technical Due Diligence report regarding {subject} resilience and key-person risk has been generated.\n\n"
        "Please review the attached confidential PDF document."
    )

async def timed_tool_call(session, server_name: str, tool_name: str, args: dict, log: list) -> tuple:
    t0 = time.time()
    ok = True
    result_obj = None
    try:
        result_obj = await session.call_tool(tool_name, args)
    except Exception as e:
        ok = False
        result_obj = None
        print(f"  {RED}  fail{RESET} {DIM}·{RESET} {e}{RESET}")
    elapsed = time.time() - t0
    log.append({"server": server_name, "tool": tool_name, "elapsed": elapsed, "ok": ok})
    return result_obj, elapsed

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN ORCHESTRATION
# ══════════════════════════════════════════════════════════════════════════════

TOTAL_PHASES = 10

async def run_orchestration():
    banner()
    pipeline_start = time.time()
    tool_log: list[dict] = []

    # ── Paths ──────────────────────────────────────────────────────────
    micro_path = BASE_DIR / "bus-factor-detector" / "data" / "demo_commits_micro.txt"
    large_path = BASE_DIR / "bus-factor-detector" / "data" / "demo_commits_large.txt"
    cache_path = BASE_DIR / "bus-factor-detector" / "cache" / "macro_result.json"
    evidence_dir = BASE_DIR / "bus-factor-detector" / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    
    # We use the WhatsApp bridge's `store/` directory as a shared volume tunnel
    whatsapp_store_dir = BASE_DIR / "mcp-servers" / "whatsapp-mcp-extended" / "store"
    whatsapp_store_dir.mkdir(parents=True, exist_ok=True)

    try:
        micro_commits = micro_path.read_text()
        large_commits = large_path.read_text() if large_path.exists() else micro_commits
        print(f"  {GREEN}  ok{RESET} {DIM}·{RESET} dataset loaded ({len(micro_commits.splitlines())} lines){RESET}")
    except Exception as e:
        print(f"  {RED}  fail{RESET} {DIM}·{RESET} could not load data: {e}{RESET}")
        return

    target_phone = os.getenv("TARGET_PHONE", "918971542999")
    print(f"  {GREEN}  ok{RESET} {DIM}·{RESET} default target {DIM}{target_phone}{RESET}")

    # ── Server configuration ──────────────────────────────────────────────────
    wa_url      = "http://localhost:8081/sse"
    python_exe  = str(sys.executable)
    npx_cmd     = shutil.which("npx.cmd") or shutil.which("npx") or "npx.cmd"
    env         = os.environ.copy()

    custom_params = StdioServerParameters(command=python_exe, args=["custom_tools.py"], env=env)
    seq_params    = StdioServerParameters(command=npx_cmd, args=["-y", "@modelcontextprotocol/server-sequential-thinking"], env=env)
    mem_params    = StdioServerParameters(command=npx_cmd, args=["-y", "@modelcontextprotocol/server-memory"], env=env)
    fs_params     = StdioServerParameters(command=npx_cmd, args=["-y", "@modelcontextprotocol/server-filesystem", str(evidence_dir)], env=env)

    print(f"\n  {BOLD}{WHITE}Starting 5-server MCP swarm{RESET}")

    try:
        async with contextlib.AsyncExitStack() as stack:

            phase_header(0, TOTAL_PHASES, "SWARM BOOT + HEALTH CHECK", "ALL SERVERS")

            async def boot_server(name, transport_ctx, transport_type):
                print(f"  {DIM}Booting {name:<22} [{transport_type}]...{RESET}", end="", flush=True)
                r, w = await stack.enter_async_context(transport_ctx)
                sess = await stack.enter_async_context(ClientSession(r, w))
                await sess.initialize()
                tools = (await sess.list_tools()).tools
                print(f"\r  {GREEN}  ok{RESET} {CYAN}{name:<25}{RESET} {DIM}[{transport_type}]{RESET}  {WHITE}{len(tools)} tools{RESET}")
                return sess, tools

            # Connect via SSE
            wa_sess, wa_tools   = await boot_server("WhatsApp Bridge", sse_client(wa_url), "SSE")
            ct_sess, ct_tools   = await boot_server("Custom Analysis", stdio_client(custom_params), "Stdio")
            sq_sess, sq_tools   = await boot_server("Sequential Thinking", stdio_client(seq_params), "Stdio")
            mem_sess, mem_tools = await boot_server("Memory / KG", stdio_client(mem_params), "Stdio")
            fs_sess, fs_tools   = await boot_server("Filesystem", stdio_client(fs_params), "Stdio")

            phase_header(1, TOTAL_PHASES, "AI REASONING PLAN", "Sequential Thinking MCP")
            thought_text = "Ingest the raw commit log, strip PII, identify the bus factor vulnerability, and generate an executive risk report."
            thought_block(1, 1, thought_text)
            tool_call("Sequential Thinking", "sequentialthinking", f"thought #1")
            result, elapsed = await timed_tool_call(sq_sess, "Sequential Thinking", "sequentialthinking", {"thought": thought_text, "thoughtNumber": 1, "totalThoughts": 1, "nextThoughtNeeded": False}, tool_log)
            print(f"  {GREEN}  ok{RESET} {DIM}·{RESET} thought completed in {elapsed:.2f}s")

            phase_header(3, TOTAL_PHASES, "DEEP BUS FACTOR ANALYSIS", "Custom Analysis MCP + Groq LLM")
            tool_call("Custom Analysis", "analyze_bus_factor", f"commit_log=[{len(micro_commits)} chars] | mode=micro")
            analysis_result, elapsed = await timed_tool_call(ct_sess, "Custom Analysis", "analyze_bus_factor", {"commit_log": micro_commits, "mode": "micro"}, tool_log)

            graph_for_pdf = _build_commit_graph_for_pdf(micro_commits)
            file_parsed = pdf_fields_from_graph(graph_for_pdf)
            analysis_text = (
                analysis_result.content[0].text
                if analysis_result and analysis_result.content
                else ""
            )
            if analysis_text.strip() and not analysis_text.strip().upper().startswith("ERROR"):
                llm_parsed = parse_bus_factor_result(analysis_text)
                parsed = {**file_parsed}
                for key in ("KEY_FINDING", "RECOMMENDED_ACTION"):
                    v = llm_parsed.get(key)
                    if v:
                        parsed[key] = v
                for key in ("AT_RISK_PERSON", "BUS_FACTOR_SCORE", "RISK_LEVEL"):
                    parsed[key] = file_parsed[key]
            else:
                parsed = file_parsed

            tool_result(
                analysis_text if analysis_text.strip() else "(LLM unavailable; PDF from log statistics)",
                elapsed,
            )
            gm = graph_for_pdf.get("metrics") or {}
            print(
                f"  {DIM}  {GREEN}AT_RISK_PERSON:{RESET} {WHITE}{parsed.get('AT_RISK_PERSON')}{RESET}  "
                f"{DIM}·{RESET}  {GREEN}BUS_FACTOR_SCORE:{RESET} {WHITE}{parsed.get('BUS_FACTOR_SCORE')}{RESET}  "
                f"{DIM}·{RESET}  {GREEN}BREADTH_90PCT:{RESET} {WHITE}{gm.get('contributors_90pct')}{RESET} "
                f"{DIM}(from uploaded log){RESET}"
            )

            dev_name = parsed.get("AT_RISK_PERSON", "DEV_01")
            risk_lvl = parsed.get("RISK_LEVEL", "HIGH")

            phase_header(5, TOTAL_PHASES, "KNOWLEDGE GRAPH STORAGE", "Memory MCP")
            tool_call("Memory MCP", "create_entities", f"Storing {dev_name}")
            await timed_tool_call(mem_sess, "Memory MCP", "create_entities", {
                "entities": [{"name": dev_name, "entityType": "HighRiskDeveloper", "observations": [f"Risk level: {risk_lvl}"]}]
            }, tool_log)
            print(f"\n  {GREEN}  ok{RESET} {DIM}·{RESET} knowledge graph entity stored")

            phase_header(8, TOTAL_PHASES, "MACRO REPORT — CACHE RETRIEVAL", "Custom Analysis MCP")
            macro_text = ""
            if cache_path.exists():
                tool_call("Custom Analysis", "get_bus_factor_report", "serving from cache")
                macro_result, elapsed = await timed_tool_call(ct_sess, "Custom Analysis", "get_bus_factor_report", {}, tool_log)
                if macro_result and macro_result.content:
                    macro_text = macro_result.content[0].text
                    tool_result("Macro cache retrieved successfully.", elapsed)
            else:
                print(f"  {YELLOW}  warn{RESET} {DIM}·{RESET} no macro cache (optional: run prerun_cache.py){RESET}")

            phase_header(9, TOTAL_PHASES, "WHATSAPP REPORT DELIVERY", "WhatsApp Bridge MCP")

            # 1. Generate the PDF into the SHARED Docker store folder
            pdf_filename = f"SolarisX_DueDiligence_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            host_pdf_path = str(whatsapp_store_dir / pdf_filename)
            pdf_macro_body = macro_context_from_uploaded_log(micro_commits) or macro_text
            org_display = os.getenv("TARGET_ORG_NAME", "").strip() or "Not specified"
            generate_pdf_report(
                parsed,
                pdf_macro_body,
                host_pdf_path,
                org_display=org_display,
                metrics=graph_for_pdf.get("metrics") or {},
            )
            print(f"  {DIM}  PDF written to shared volume: {host_pdf_path}{RESET}")

            # 2. Send Intro Message
            intro_msg = build_whatsapp_intro()
            tool_call("WhatsApp Bridge", "send_message", f"recipient={target_phone}")
            await timed_tool_call(
                wa_sess, "WhatsApp Bridge", "send_message",
                {"recipient": target_phone, "message": intro_msg}, tool_log
            )

            # 3. Call the Native Tool with the new metadata arguments!
            docker_pdf_path = f"/app/store/{pdf_filename}"
            print(f"\n  {DIM}  Uploading PDF document to WhatsApp...{RESET}")
            tool_call("WhatsApp Bridge", "send_file", f"recipient={target_phone} | media_path={docker_pdf_path}")
            
            send_result, elapsed = await timed_tool_call(
                wa_sess, "WhatsApp Bridge", "send_file",
                {
                    "recipient": target_phone, 
                    "media_path": docker_pdf_path,
                    "mimetype": "application/pdf",
                    "filename": pdf_filename,
                    "caption": "M&A Technical Risk Report (Strictly Confidential)"
                }, tool_log
            )

            if send_result and send_result.content:
                response_text = send_result.content[0].text
                # SMART CHECK: We explicitly look for a False flag to prevent the old "error: None" bug
                if "'success': False" in response_text or '"success": false' in response_text.lower():
                    print(f"  {YELLOW}  warn{RESET} {DIM}·{RESET} WhatsApp bridge: {response_text}{RESET}")
                    tool_log[-1]["ok"] = False
                else:
                    print(f"  {GREEN}  ok{RESET} {DIM}·{RESET} PDF delivered via WhatsApp in {elapsed:.2f}s")
            else:
                print(f"  {YELLOW}  warn{RESET} {DIM}·{RESET} WhatsApp file send returned no body{RESET}")
                tool_log[-1]["ok"] = False

            phase_header(10, TOTAL_PHASES, "PIPELINE COMPLETE", "SOLARIS X ENGINE")
            swarm_summary(tool_log, time.time() - pipeline_start)

    except Exception as e:
        print(f"\n{RED}{BOLD}  CRITICAL ORCHESTRATION FAILURE{RESET}")
        print(f"{RED}  {e}{RESET}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_orchestration())
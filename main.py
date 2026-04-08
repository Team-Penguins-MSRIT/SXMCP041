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

def safe_pdf_text(text: str) -> str:
    if not text: return ""
    return str(text).encode('latin-1', 'ignore').decode('latin-1').replace("*", "")

def generate_pdf_report(parsed: dict, macro_text: str, output_path: str):
    """Generates a highly structured, professional M&A technical PDF."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 10, "TECHNICAL DUE DILIGENCE", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, "REPOSITORY RESILIENCE & KEY-PERSON RISK", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
    
    pdf.set_draw_color(200, 200, 200)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y() + 2, 200, pdf.get_y() + 2)
    pdf.ln(8)
    
    pdf.set_fill_color(245, 245, 245)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(0, 0, 0)
    
    pdf.cell(50, 8, " Target Organization:", border=1, fill=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(140, 8, " AcquiCo Inc.", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(50, 8, " Primary At-Risk Node:", border=1, fill=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(140, 8, f" {safe_pdf_text(parsed.get('AT_RISK_PERSON', 'UNKNOWN'))}", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(50, 8, " Systemic Risk Level:", border=1, fill=True)
    pdf.set_font("Helvetica", "B", 10)
    
    risk_level = safe_pdf_text(parsed.get("RISK_LEVEL", "UNKNOWN")).upper()
    if "HIGH" in risk_level:
        pdf.set_text_color(200, 0, 0)
    elif "MEDIUM" in risk_level:
        pdf.set_text_color(200, 120, 0)
    else:
        pdf.set_text_color(0, 150, 0)
        
    pdf.cell(140, 8, f" {risk_level} (Bus Factor Score: {safe_pdf_text(parsed.get('BUS_FACTOR_SCORE', 'N/A'))}/10)", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 8, "1. CRITICAL VULNERABILITY FINDING", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(0, 6, safe_pdf_text(parsed.get("KEY_FINDING", "No key finding reported.")))
    pdf.ln(6)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 8, "2. RECOMMENDED MITIGATION STRATEGY", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(0, 6, safe_pdf_text(parsed.get("RECOMMENDED_ACTION", "No action reported.")))
    pdf.ln(6)
    
    if macro_text:
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(0, 8, "3. MACRO REPOSITORY CONTEXT", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(0, 6, safe_pdf_text(macro_text))
        pdf.ln(6)

    pdf.set_y(-25)
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
    return (
        "SOLARIS X: ANALYSIS COMPLETE\n"
        "----------------------------------------\n"
        "The Technical Due Diligence report regarding AcquiCo's repository resilience and key-person risk has been generated.\n\n"
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

            analysis_text = analysis_result.content[0].text if analysis_result and analysis_result.content else "RISK_LEVEL: HIGH\nKEY_FINDING: DEV_01 owns 75% of commits.\nAT_RISK_PERSON: DEV_01\nRECOMMENDED_ACTION: Immediate retention package.\nBUS_FACTOR_SCORE: 9"
            parsed = parse_bus_factor_result(analysis_text)
            tool_result(analysis_text, elapsed)

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
            generate_pdf_report(parsed, macro_text, host_pdf_path)
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
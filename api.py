"""
THE KEYSTONE — FastAPI bridge for Solaris X (main.py orchestrator).

Does not modify main.py: saves uploaded logs to the path it already reads,
runs main.py as a subprocess with unbuffered stdout, streams logs via SSE,
serves generated PDFs, and can deliver the report via the WhatsApp bridge HTTP API.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import sys
import subprocess
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
_BFD_SRC = BASE_DIR / "bus-factor-detector" / "src"
if _BFD_SRC.is_dir():
    _p = str(_BFD_SRC.resolve())
    if _p not in sys.path:
        sys.path.insert(0, _p)
from bus_factor_metrics import concentration_from_counts

VENV_PYTHON = BASE_DIR / "venv" / "Scripts" / "python.exe"
if not VENV_PYTHON.exists():
    VENV_PYTHON = Path(sys.executable)

MAIN_PY = BASE_DIR / "main.py"
DATA_MICRO = BASE_DIR / "bus-factor-detector" / "data" / "demo_commits_micro.txt"
DATA_LARGE = BASE_DIR / "bus-factor-detector" / "data" / "demo_commits_large.txt"
DATA_DIR = DATA_MICRO.parent
EVIDENCE_DIR = BASE_DIR / "bus-factor-detector" / "evidence"
STORE_DIR = BASE_DIR / "mcp-servers" / "whatsapp-mcp-extended" / "store"

load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR / "mcp-servers" / "whatsapp-mcp-extended" / ".env")

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

BRIDGE_URL = os.getenv("WHATSAPP_BRIDGE_URL", "http://127.0.0.1:8180").rstrip("/")
# Bridge uses API_KEY in Docker; allow override for host-only tools
BRIDGE_API_KEY = os.getenv("WHATSAPP_BRIDGE_API_KEY") or os.getenv("API_KEY", "")

app = FastAPI(title="Solaris X · Keystone API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_run_lock = asyncio.Lock()
_session: dict[str, Any] = {
    "pdf_filename": None,
    "graph": None,
    "bus_factor_score": None,
    "log_tail_clean": "",
    "complete": False,
    "exit_code": None,
}


def _strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


_COMMIT_LINE = re.compile(
    r"^(\d{4}-\d{2}-\d{2})\s+(\S+)\s+(.+?)\s*$",
)


def _slug_component(label: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9_-]+", "_", label.strip())[:48]
    return s or "general"


def _component_from_message(message: str) -> str:
    """Map commit message to a component / area (prefix before ':', else general)."""
    msg = message.strip()
    if msg.startswith('"') and msg.endswith('"'):
        msg = msg[1:-1]
    m = re.match(r"^([A-Za-z][A-Za-z0-9_-]*)\s*:\s*", msg)
    if m:
        return _slug_component(m.group(1))
    return "general"


def _parse_commit_lines(commit_text: str) -> list[tuple[str, str]]:
    """Return list of (author, component) per commit from the log."""
    rows: list[tuple[str, str]] = []
    for raw in commit_text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = _COMMIT_LINE.match(line)
        if not m:
            continue
        author = m.group(2).strip()
        rest = m.group(3).strip()
        if rest.startswith('"'):
            end = rest.rfind('"')
            message = rest[1:end] if end > 0 else rest[1:]
        else:
            parts = rest.split(None, 1)
            message = parts[1] if len(parts) > 1 else rest
        comp = _component_from_message(message)
        rows.append((author, comp))
    return rows


def build_commit_author_file_graph(
    commit_text: str,
    highlight_person: str | None = None,
    max_file_nodes: int = 80,
) -> dict[str, Any]:
    """
    Real node-link graph: developers and file/component areas from the commit log.
    Links are weighted by commit count (same author, same component).
    """
    rows = _parse_commit_lines(commit_text)
    if not rows:
        return {
            "nodes": [],
            "links": [],
            "at_risk": None,
            "risk_level": "UNKNOWN",
        }

    edge_counter: Counter[tuple[str, str]] = Counter()
    author_totals: Counter[str] = Counter()
    for author, comp in rows:
        edge_counter[(author, comp)] += 1
        author_totals[author] += 1

    file_totals: Counter[str] = Counter()
    for (a, comp), w in edge_counter.items():
        file_totals[comp] += w

    allowed_files = {f for f, _ in file_totals.most_common(max_file_nodes)}
    filtered_edges: Counter[tuple[str, str]] = Counter()
    for (author, comp), w in edge_counter.items():
        if comp in allowed_files:
            filtered_edges[(author, comp)] += w
        else:
            filtered_edges[(author, "general")] += w
            allowed_files.add("general")

    max_author = max(author_totals.values()) or 1
    file_link_sums: Counter[str] = Counter()
    for (author, comp), w in filtered_edges.items():
        file_link_sums[comp] += w
    max_file = max(file_link_sums.values()) or 1

    at_risk = highlight_person if highlight_person in author_totals else None
    if not at_risk:
        at_risk = author_totals.most_common(1)[0][0]
    share = author_totals[at_risk] / len(rows)
    risk_level = "HIGH" if share >= 0.5 else "MEDIUM" if share >= 0.3 else "LOW"

    nodes: list[dict[str, Any]] = []
    dev_ids: set[str] = set()
    file_ids: set[str] = set()

    for (author, comp), weight in filtered_edges.items():
        dev_ids.add(author)
        file_ids.add(comp)

    for author in sorted(dev_ids):
        cnt = author_totals[author]
        base = 4.0 + 12.0 * (cnt / max_author) ** 0.85
        if author == at_risk:
            base *= 1.5
        nodes.append(
            {
                "id": author,
                "name": author.split("@", 1)[0] if "@" in author else author,
                "type": "developer",
                "val": round(base, 2),
            }
        )

    for comp in sorted(file_ids):
        fid = f"file:{_slug_component(comp)}"
        wsum = file_link_sums[comp]
        fval = 2.0 + 5.0 * (wsum / max_file) ** 0.75
        nodes.append(
            {
                "id": fid,
                "name": comp,
                "type": "file",
                "val": round(fval, 2),
            }
        )

    comp_to_fid = {c: f"file:{_slug_component(c)}" for c in file_ids}
    links: list[dict[str, Any]] = []
    for (author, comp), weight in sorted(filtered_edges.items()):
        target = comp_to_fid[comp]
        links.append(
            {
                "source": author,
                "target": target,
                "weight": weight,
                "value": weight,
            }
        )

    return {
        "nodes": nodes,
        "links": links,
        "at_risk": at_risk,
        "risk_level": risk_level,
    }


def _parse_at_risk_from_log(clean_log: str) -> str | None:
    # Last wins: orchestrator may print LLM lines first, then file-derived metrics.
    matches = re.findall(r"AT_RISK_PERSON:\s*(\S+)", clean_log)
    if matches:
        return matches[-1].strip()
    return None


def _parse_bus_factor_score_from_log(clean_log: str) -> int | None:
    matches = re.findall(r"BUS_FACTOR_SCORE:\s*(\d+)", clean_log, re.IGNORECASE)
    if matches:
        return int(matches[-1])
    return None


def build_commit_analytics(commit_text: str) -> dict[str, Any]:
    """Quantitative stats from the commit log (any dataset size)."""
    rows = _parse_commit_lines(commit_text)
    if not rows:
        return {
            "total_commits": 0,
            "unique_contributors": 0,
            "distribution": [],
            "key_person_risk_score": None,
            "concentration_hhi": None,
            "effective_contributors": None,
            "contributors_50pct": None,
            "contributors_90pct": None,
            "top_share": None,
            "concentration_index": None,
            "risk_level": None,
            "repository_bus_factor_breadth": None,
        }
    total = len(rows)
    counts: Counter[str] = Counter()
    for author, _ in rows:
        counts[author] += 1
    metrics = concentration_from_counts(dict(counts))
    distribution: list[dict[str, Any]] = []
    for author, count in counts.most_common():
        pct = round(100.0 * count / total, 2)
        distribution.append({"author": author, "count": count, "percentage": pct})
    distribution.sort(key=lambda x: -x["percentage"])
    return {
        "total_commits": total,
        "unique_contributors": metrics["contributor_count"],
        "distribution": distribution,
        "key_person_risk_score": metrics["key_person_risk_score"],
        "concentration_hhi": metrics["hhi"],
        "effective_contributors": metrics["effective_contributors"],
        "contributors_50pct": metrics["contributors_50pct"],
        "contributors_90pct": metrics["contributors_90pct"],
        "top_share": metrics["top_share"],
        "concentration_index": metrics["concentration_index"],
        "risk_level": metrics["risk_level"],
        "repository_bus_factor_breadth": metrics["repository_bus_factor_breadth"],
    }


def _extract_pdf_filename(clean_log: str) -> str | None:
    m = re.search(r"(SolarisX_DueDiligence_\d{8}_\d{4,}\.pdf)", clean_log)
    if m:
        return m.group(1)
    for name in sorted(STORE_DIR.glob("SolarisX_DueDiligence_*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True):
        return name.name
    return None


def _intro_message() -> str:
    org = os.getenv("TARGET_ORG_NAME", "").strip()
    subject = f"{org}'s repository" if org else "the analyzed repository"
    return (
        "SOLARIS X: ANALYSIS COMPLETE\n"
        "----------------------------------------\n"
        f"The Technical Due Diligence report regarding {subject} resilience "
        "and key-person risk has been generated.\n\n"
        "Please review the attached confidential PDF document."
    )


def _bridge_post(path: str, payload: dict) -> dict:
    if not BRIDGE_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="WHATSAPP_BRIDGE_API_KEY or API_KEY not set (needed for bridge /api/send).",
        )
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{BRIDGE_URL}{path}",
        data=data,
        headers={
            "Content-Type": "application/json",
            "X-API-Key": BRIDGE_API_KEY,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        raise HTTPException(status_code=502, detail=f"Bridge HTTP {e.code}: {err_body}") from e
    except urllib.error.URLError as e:
        raise HTTPException(status_code=502, detail=f"Bridge unreachable: {e}") from e


class ActuateBody(BaseModel):
    phone: str = Field(..., description="10-digit Indian mobile without country code")
    pdf_filename: str | None = Field(None, description="Override PDF; default last session PDF")


def _normalize_in_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone)
    if len(digits) == 10:
        return "91" + digits
    if digits.startswith("91") and len(digits) == 12:
        return digits
    raise HTTPException(
        status_code=400,
        detail="Enter a 10-digit mobile number (country code 91 is added automatically).",
    )


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "keystone-api"}


@app.get("/api/session")
async def get_session():
    return _session


@app.post("/api/upload")
async def upload_commit_log(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".txt"):
        raise HTTPException(status_code=400, detail="Please upload a .txt commit log.")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    raw = await file.read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("latin-1", errors="replace")
    DATA_MICRO.write_text(text, encoding="utf-8")
    return {"ok": True, "path": str(DATA_MICRO), "lines": len(text.splitlines())}


def _read_commit_log_path(dataset: str) -> Path:
    if dataset == "large" and DATA_LARGE.is_file():
        return DATA_LARGE
    return DATA_MICRO


@app.get("/api/graph")
async def get_graph(
    highlight: str | None = None,
    dataset: str = "micro",
):
    """
    Node-link graph from the real commit log: developers and inferred file/component areas.
    Optional `highlight` should match an author id (e.g. email) to emphasize in the UI.
    `dataset` = micro | large (falls back to micro if large file missing).
    """
    path = _read_commit_log_path(dataset)
    if not path.is_file():
        raise HTTPException(status_code=400, detail="No commit log found. Upload via POST /api/upload.")
    text = path.read_text(encoding="utf-8", errors="replace")
    return build_commit_author_file_graph(text, highlight_person=highlight)


@app.get("/api/graph-preview")
async def graph_preview():
    if not DATA_MICRO.exists():
        raise HTTPException(status_code=400, detail="Upload a commit log first.")
    text = DATA_MICRO.read_text(encoding="utf-8", errors="replace")
    return build_commit_author_file_graph(text, highlight_person=None)


@app.get("/api/analytics")
async def get_analytics(dataset: str = "micro"):
    """Commit counts and per-author share from the uploaded log (universal for any repo)."""
    path = _read_commit_log_path(dataset)
    if not path.is_file():
        raise HTTPException(status_code=400, detail="No commit log found. Upload via POST /api/upload.")
    text = path.read_text(encoding="utf-8", errors="replace")
    return build_commit_analytics(text)


async def _stream_main_py():
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    async with _run_lock:
        _session["pdf_filename"] = None
        _session["graph"] = None
        _session["bus_factor_score"] = None
        _session["complete"] = False
        _session["exit_code"] = None

        proc = await asyncio.create_subprocess_exec(
            str(VENV_PYTHON),
            "-u",
            str(MAIN_PY),
            cwd=str(BASE_DIR),
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        assert proc.stdout
        buf_chunks: list[str] = []

        while True:
            line_b = await proc.stdout.readline()
            if not line_b:
                break
            line = line_b.decode("utf-8", errors="replace")
            buf_chunks.append(line)
            clean = _strip_ansi(line)
            payload = {"type": "line", "raw": line.rstrip("\n"), "clean": clean.rstrip("\n")}
            if "PIPELINE COMPLETE" in clean:
                payload["milestone"] = "pipeline_complete"
            yield f"data: {json.dumps(payload)}\n\n"

        exit_code = await proc.wait()
        full_log = "".join(buf_chunks)
        clean_full = _strip_ansi(full_log)
        at_risk = _parse_at_risk_from_log(clean_full)
        pdf_filename = _extract_pdf_filename(clean_full)
        commit_text = (
            DATA_MICRO.read_text(encoding="utf-8", errors="replace") if DATA_MICRO.exists() else ""
        )
        graph = build_commit_author_file_graph(commit_text, highlight_person=at_risk)
        rows_cf = _parse_commit_lines(commit_text)
        if rows_cf:
            cmc: Counter[str] = Counter()
            for a, _ in rows_cf:
                cmc[a] += 1
            bus_factor_score = concentration_from_counts(dict(cmc))["key_person_risk_score"]
        else:
            bus_factor_score = _parse_bus_factor_score_from_log(clean_full)

        _session["pdf_filename"] = pdf_filename
        _session["graph"] = graph
        _session["bus_factor_score"] = bus_factor_score
        _session["log_tail_clean"] = clean_full[-8000:]
        _session["complete"] = "PIPELINE COMPLETE" in clean_full and exit_code == 0
        _session["exit_code"] = exit_code

        yield f"data: {json.dumps({'type': 'done', 'exit_code': exit_code, 'pdf_filename': pdf_filename, 'graph': graph, 'bus_factor_score': bus_factor_score, 'complete': _session['complete']})}\n\n"


@app.get("/api/run/stream")
async def run_stream():
    """Run main.py and stream merged stdout/stderr as SSE."""
    if not MAIN_PY.is_file():
        raise HTTPException(status_code=500, detail="main.py not found.")
    if not DATA_MICRO.is_file():
        raise HTTPException(status_code=400, detail="Upload commit log first (POST /api/upload).")

    return StreamingResponse(_stream_main_py(), media_type="text/event-stream")


def _pdf_inline_response(path: Path) -> FileResponse:
    """Serve PDF for browser embedding (iframe). Do not pass FileResponse(filename=...) — that forces attachment."""
    safe = path.name
    return FileResponse(
        path,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{safe}"'},
    )


@app.get("/api/pdf/{filename}")
async def get_pdf(filename: str):
    if not re.match(r"^SolarisX_DueDiligence_\d{8}_\d+\.pdf$", filename):
        raise HTTPException(status_code=400, detail="Invalid PDF name.")
    path = STORE_DIR / filename
    if not path.is_file():
        raise HTTPException(status_code=404, detail="PDF not found.")
    return _pdf_inline_response(path)


@app.get("/api/pdf/latest")
async def get_latest_pdf():
    name = _session.get("pdf_filename")
    if name and (STORE_DIR / name).is_file():
        return _pdf_inline_response(STORE_DIR / name)
    files = sorted(STORE_DIR.glob("SolarisX_DueDiligence_*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        raise HTTPException(status_code=404, detail="No PDF available yet.")
    return _pdf_inline_response(files[0])


@app.post("/api/actuate")
async def actuate(body: ActuateBody):
    recipient = _normalize_in_phone(body.phone)
    pdf_name = body.pdf_filename or _session.get("pdf_filename")
    if not pdf_name:
        files = sorted(STORE_DIR.glob("SolarisX_DueDiligence_*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not files:
            raise HTTPException(status_code=400, detail="No PDF to send. Run the pipeline first.")
        pdf_name = files[0].name

    host_path = STORE_DIR / pdf_name
    if not host_path.is_file():
        raise HTTPException(status_code=404, detail=f"PDF not on disk: {pdf_name}")

    docker_media_path = f"/app/store/{pdf_name}"

    intro = _bridge_post(
        "/api/send",
        {"recipient": recipient, "message": _intro_message()},
    )
    file_resp = _bridge_post(
        "/api/send",
        {
            "recipient": recipient,
            "message": "",
            "media_path": docker_media_path,
            "mimetype": "application/pdf",
            "fileName": pdf_name,
            "caption": "M&A Technical Risk Report (Strictly Confidential)",
        },
    )
    return {"ok": True, "recipient": recipient, "intro": intro, "file": file_resp}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="127.0.0.1", port=8765, reload=False)

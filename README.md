# SXMCP041 - SOLARIS X Bus Factor Swarm

Autonomous multi-MCP due diligence pipeline for detecting Bus Factor risk from commit logs and delivering a professional report to WhatsApp.

This repository combines:
- a swarm orchestrator in [main.py](main.py)
- custom Bus Factor MCP tools in [custom_tools.py](custom_tools.py)
- the analysis engine in [bus-factor-detector/src/bus_factor_engine.py](bus-factor-detector/src/bus_factor_engine.py)
- a WhatsApp MCP stack in [mcp-servers/whatsapp-mcp-extended](mcp-servers/whatsapp-mcp-extended)

## What It Does

1. Loads commit logs from the dataset.
2. Runs sequential planning using MCP sequential-thinking.
3. Runs Bus Factor analysis (micro mode) using custom MCP tools.
4. Stores risk entity in memory MCP knowledge graph.
5. Pulls cached macro report if available.
6. Generates a polished PDF due diligence report.
7. Sends intro text + PDF to a target WhatsApp number.

## Active MCP Servers (Current Pipeline)

The orchestrator currently boots 5 servers:

1. WhatsApp Bridge (SSE)
2. Custom Analysis (stdio)
3. Sequential Thinking (stdio)
4. Memory / KG (stdio)
5. Filesystem (stdio)

## Repository Structure

- [main.py](main.py): Swarm orchestrator and report delivery flow
- [custom_tools.py](custom_tools.py): Custom FastMCP server (analyze, macro report, metrics)
- [bus-factor-detector](bus-factor-detector): Core analyzer, sample data, scripts, cache
- [mcp-servers/whatsapp-mcp-extended](mcp-servers/whatsapp-mcp-extended): WhatsApp bridge + MCP + web UI
- [requirements.txt](requirements.txt): Python dependencies for root project

## Prerequisites

- Windows + PowerShell (current setup)
- Python 3.11+ (venv used in this repo)
- Node.js + npx
- Docker Desktop (for WhatsApp MCP stack)
- Groq API key in `.env`

## Environment Setup

From repo root:

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
pip install fpdf2 presidio-analyzer presidio-anonymizer spacy
python -m spacy download en_core_web_lg
```

Create/update `.env` in repo root:

```env
GROQ_API_KEY=your_groq_key_here
TARGET_PHONE=91XXXXXXXXXX
```

## Start WhatsApp MCP Stack

```powershell
cd mcp-servers\whatsapp-mcp-extended
docker-compose up -d
```

Make sure WhatsApp bridge is authenticated and connected before running the orchestrator.

## Run the Swarm

From repo root:

```powershell
python main.py
```

## Outputs

- Evidence and generated artifacts under [bus-factor-detector/evidence](bus-factor-detector/evidence)
- Macro cache file at [bus-factor-detector/cache/macro_result.json](bus-factor-detector/cache/macro_result.json)
- PDF report written into WhatsApp shared store volume path under:
	[mcp-servers/whatsapp-mcp-extended/store](mcp-servers/whatsapp-mcp-extended/store)

## Notes

- The pipeline is designed for deterministic execution (single send flow) to avoid repeated WhatsApp messages.
- If macro cache is missing, run [bus-factor-detector/scripts/prerun_cache.py](bus-factor-detector/scripts/prerun_cache.py) before demo.
- The fetch MCP package was removed from active boot because it was not available via npm in this environment.

## Team

Team Penguins - MSRIT

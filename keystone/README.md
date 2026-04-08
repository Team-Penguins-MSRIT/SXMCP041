# THE KEYSTONE

Enterprise dark-mode UI for **Solaris X**. It talks to the FastAPI bridge (`../api.py`), which shells out to `main.py` unchanged and streams logs over SSE.

## Prerequisites

- Repo root: Python venv installed (`../requirements.txt`), `.env` with `GROQ_API_KEY`, MCP + WhatsApp stack as in the root `README.md`.
- WhatsApp bridge reachable at `http://127.0.0.1:8180` with `API_KEY` / `WHATSAPP_BRIDGE_API_KEY` available to the API (loaded from root `.env` or `mcp-servers/whatsapp-mcp-extended/.env`).

## Run (development)

**Terminal 1 — API bridge**

```powershell
cd D:\RNSIT
.\venv\Scripts\python.exe api.py
```

Listens on `http://127.0.0.1:8765`.

**Terminal 2 — Frontend**

```powershell
cd D:\RNSIT\keystone
npm run dev
```

Open `http://localhost:5173`. Vite proxies `/api/*` to the FastAPI server.

## Production build (optional)

```powershell
cd D:\RNSIT\keystone
npm run build
npm run preview
```

Serve `dist/` behind your reverse proxy, or point `preview` at port 4173 and set `vite.config.ts` / proxy target to your API host.

## Flow

1. Drop a `.txt` commit log → uploaded to `bus-factor-detector/data/demo_commits_micro.txt` (the path `main.py` already reads).
2. **Analyze** → `GET /api/run/stream` (SSE) runs `main.py` with unbuffered stdout.
3. On `PIPELINE COMPLETE` / `done` event → PDF pane + 3D graph + Actuate panel.
4. **Send secure report** → `POST /api/actuate` adds India country code `91` and calls the Go bridge `/api/send` twice (intro text + PDF on `/app/store/...`).

PDFs are read from `mcp-servers/whatsapp-mcp-extended/store/` (same path `main.py` writes).

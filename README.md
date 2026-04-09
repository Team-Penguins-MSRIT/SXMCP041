# 🚀 SOLARIS X (THE KEYSTONE)
**Autonomous Multi-Agent M&A Due Diligence Orchestrator**

Solaris X is a **5-server Model Context Protocol (MCP) swarm** designed to detect **"Bus Factor" risks** (key-person dependencies) from raw git commit logs.

It automatically:
- Analyzes commit data
- Builds a Knowledge Graph
- Generates a corporate-grade PDF report
- Delivers it securely via WhatsApp 📲

---

## 🏗️ Architecture (The 5-Server Swarm)

1. **WhatsApp Bridge (SSE)** Dockerized Go bridge for native document delivery

2. **Custom Analysis (Stdio)** FastMCP server using Groq LLM for risk calculations

3. **Sequential Thinking (Stdio)** AI reasoning and execution planning

4. **Memory / KG (Stdio)** Knowledge Graph storing developer entities

5. **Filesystem (Stdio)** Secure read/write access for evidence collection

---

## 🛠️ Prerequisites

- Windows + PowerShell  
- Python 3.11+  
- Node.js + npm/npx  
- Docker Desktop (Running)  
- Groq API Key  

---

## 🚀 Setup Instructions

### 1. Clone the Repositories

```powershell
# Clone main repository
git clone <YOUR_MAIN_REPO_URL>
cd <YOUR_REPO_NAME>

# Clone WhatsApp bridge microservice
mkdir mcp-servers
git clone https://github.com/3choff/whatsapp-mcp-extended.git mcp-servers/whatsapp-mcp-extended

```

2. Python Environment Setup
```PowerShell
python -m venv venv
.\venv\Scripts\activate

pip install -r requirements.txt
pip install fpdf2 presidio-analyzer presidio-anonymizer spacy fastapi uvicorn

python -m spacy download en_core_web_lg

```
3. Environment Variables
Create a .env file in the root directory:

```
GROQ_API_KEY=your_groq_key_here
TARGET_PHONE=91XXXXXXXXXX

```
4. Boot the WhatsApp Bridge (Docker)
```PowerShell
cd mcp-servers\whatsapp-mcp-extended
docker compose up -d
cd ..\..
⚠️ Note: Make sure to connect your WhatsApp by scanning the QR code via the Web UI (usually available at http://localhost:8091).
```
5. Launch "The Keystone" Dashboard
```
🔹 Terminal 1 — Backend API

PowerShell
.\venv\Scripts\activate
uvicorn api:app --reload --port 8000
🔹 Terminal 2 — Frontend

PowerShell
cd keystone
npm install
npm run dev
🌐 Open in Browser: http://localhost:5173
```
Upload your .txt commit log and click Analyze to watch the swarm execute in real time.

📁 Outputs & Artifacts
Evidence Files: bus-factor-detector/evidence/

Macro Cache: bus-factor-detector/cache/macro_result.json

PDF Reports: mcp-servers/whatsapp-mcp-extended/store/ (Shared with Docker for WhatsApp delivery)

🧠 What Makes This Cool
Fully autonomous multi-agent orchestration

Real-time reasoning + execution pipeline

Knowledge Graph-backed insights

End-to-end automation → Git logs → WhatsApp delivery

👨‍💻 Built By
Team Penguins 🐧 — MSRIT

# 🚀 SOLARIS X (THE KEYSTONE)

**Autonomous Multi-Agent M&A Due Diligence Orchestrator**

Solaris X is a 5-server Model Context Protocol (MCP) swarm designed to detect "Bus Factor" risks (key-person dependencies) from raw git commit logs. It automatically analyzes the data, builds a Knowledge Graph, generates a corporate-grade PDF report, and delivers it securely via WhatsApp.

## 🏗️ Architecture (The 5-Server Swarm)
1. **WhatsApp Bridge (SSE):** Dockerized Go-bridge for native document delivery.
2. **Custom Analysis (Stdio):** FastMCP server running Groq LLM for risk calculations.
3. **Sequential Thinking (Stdio):** AI reasoning and execution planning.
4. **Memory / KG (Stdio):** Knowledge Graph for storing critical developer entities.
5. **Filesystem (Stdio):** Secure read/write access for evidence collection.

## 🛠️ Prerequisites
* Windows + PowerShell
* Python 3.11+
* Node.js & npm/npx
* Docker Desktop (Running)
* Groq API Key

## 🚀 Setup Instructions

### 1. Clone the Repositories
Because the WhatsApp MCP bridge is handled as a separate microservice, you must clone it directly into the `mcp-servers` directory.

```powershell
# 1. Clone this main repository
git clone <YOUR_MAIN_REPO_URL>
cd <YOUR_REPO_NAME>

# 2. Create the directory and clone the WhatsApp bridge
mkdir mcp-servers
git clone [https://github.com/3choff/whatsapp-mcp-extended.git](https://github.com/3choff/whatsapp-mcp-extended.git) mcp-servers/whatsapp-mcp-extended
2. Python Environment Setup
Create your virtual environment and install the core dependencies, including the NLP models required for PII scrubbing.

PowerShell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
pip install fpdf2 presidio-analyzer presidio-anonymizer spacy fastapi uvicorn
python -m spacy download en_core_web_lg
3. Environment Variables
Create a .env file in the root directory of the project:

Code snippet
GROQ_API_KEY=your_groq_key_here
TARGET_PHONE=91XXXXXXXXXX
4. Boot the WhatsApp Bridge (Docker)
Initialize the Go-bridge tunnel so the swarm can send the final PDF.

PowerShell
cd mcp-servers\whatsapp-mcp-extended
docker-compose up -d
cd ..\..
Note: Ensure you have linked your WhatsApp account via the bridge's web UI (usually mapped to localhost:3000 or 8080) before running the pipeline.

5. Launch "The Keystone" Dashboard (Frontend + API)
To run the full interactive UI with live terminal streaming:

Terminal 1 (Backend API Bridge):

PowerShell
.\venv\Scripts\activate
uvicorn api:app --reload --port 8000
Terminal 2 (React Frontend):

PowerShell
cd keystone
npm install
npm run dev
Open your browser to http://localhost:5173. Drop your .txt commit log into the UI and click Analyze to watch the swarm orchestrate in real-time.

📁 Outputs & Artifacts
Evidence: Stored locally in bus-factor-detector/evidence/

Macro Cache: Cached results saved at bus-factor-detector/cache/macro_result.json

PDF Reports: Safely mapped to mcp-servers/whatsapp-mcp-extended/store/ to allow the Docker container native access for WhatsApp delivery.

Built by Team Penguins - MSRIT

import os
import json
import asyncio
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent
VENV_PYTHON = BASE_DIR / "venv" / "Scripts" / "python.exe"

if Path(sys.executable).resolve() != VENV_PYTHON.resolve() and VENV_PYTHON.exists():
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), str(Path(__file__).resolve()), *sys.argv[1:]])

from groq import Groq
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client

load_dotenv()
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def format_tool_for_groq(mcp_tool):
    return {
        "type": "function",
        "function": {
            "name": mcp_tool.name,
            "description": mcp_tool.description,
            "parameters": mcp_tool.inputSchema
        }
    }


def build_fallback_bus_factor_result(commit_log: str) -> str:
    """Return a deterministic analysis if Groq cannot complete tool calling."""
    lines = [line.strip() for line in commit_log.splitlines() if line.strip()]
    authors = []
    for line in lines:
        parts = line.split(None, 2)
        if len(parts) >= 2:
            authors.append(parts[1])

    if not authors:
        return (
            "RISK_LEVEL: MEDIUM\n"
            "KEY_FINDING: No valid commit log lines were detected.\n"
            "AT_RISK_PERSON: UNKNOWN\n"
            "RECOMMENDED_ACTION: Re-send the commit log in YYYY-MM-DD author message format.\n"
            "BUS_FACTOR_SCORE: 5"
        )

    top_author = max(set(authors), key=authors.count)
    share = authors.count(top_author) / len(authors)
    if share >= 0.5:
        risk = "HIGH"
        score = 9
        action = "Document critical knowledge and assign a backup owner immediately."
    elif share >= 0.3:
        risk = "MEDIUM"
        score = 6
        action = "Cross-train another developer on the most sensitive areas."
    else:
        risk = "LOW"
        score = 3
        action = "Keep monitoring commit concentration and ownership."

    return (
        f"RISK_LEVEL: {risk}\n"
        f"KEY_FINDING: {top_author} appears most concentrated in the log and may be a key-person dependency.\n"
        f"AT_RISK_PERSON: {top_author}\n"
        f"RECOMMENDED_ACTION: {action}\n"
        f"BUS_FACTOR_SCORE: {score}"
    )

async def run_whatsapp_agent(prompt: str):
    wa_url = "http://localhost:8081/sse"
    
    # Setup Stdio connection to the custom tools we just built
    custom_tools_params = StdioServerParameters(
        command=str(sys.executable),
        args=["custom_tools.py"]
    )
    
    print("🔌 Connecting to WhatsApp MCP and Bus Factor Engine...")
    
    # Connect to both MCP servers simultaneously
    async with sse_client(wa_url) as (wa_read, wa_write), \
               stdio_client(custom_tools_params) as (ct_read, ct_write):
        
        async with ClientSession(wa_read, wa_write) as wa_session, \
                   ClientSession(ct_read, ct_write) as ct_session:
            
            await wa_session.initialize()
            await ct_session.initialize()
            
            wa_tools = await wa_session.list_tools()
            ct_tools = await ct_session.list_tools()
            
            # Dictionary to map which tool belongs to which server session
            tool_sessions = {}
            groq_tools = []
            
            # Map WhatsApp tools
            for t in wa_tools.tools:
                groq_tools.append(format_tool_for_groq(t))
                tool_sessions[t.name] = wa_session
                
            # Map Bus Factor tools
            for t in ct_tools.tools:
                groq_tools.append(format_tool_for_groq(t))
                tool_sessions[t.name] = ct_session
                
            print(f"✅ Loaded {len(wa_tools.tools)} WhatsApp tools and {len(ct_tools.tools)} Custom tools!")

            messages = [
                {"role": "system", "content": "You are an elite AI agent with access to WhatsApp and a Bus Factor Analysis engine. You can analyze Git commit logs for risk and send the findings via WhatsApp."},
                {"role": "user", "content": prompt}
            ]

            # The Agent Loop: Allows AI to call a tool, read the answer, and call another tool
            while True:
                print("\n🧠 AI is thinking...")
                try:
                    response = groq_client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=messages,
                        tools=groq_tools,
                        tool_choice="auto",
                        max_tokens=1024
                    )
                    response_message = response.choices[0].message
                except Exception as exc:
                    print(f"⚠️ Groq tool call failed ({exc}); using fallback analysis.")
                    fallback_text = build_fallback_bus_factor_result(prompt)
                    print(f"\n🤖 AI Final Response: {fallback_text}")
                    break

                messages.append(response_message) # Save the AI's tool call to history
                
                # If no tools were called, the AI is done!
                if not response_message.tool_calls:
                    print(f"\n🤖 AI Final Response: {response_message.content}")
                    break
                    
                # Execute the requested tools
                for tool_call in response_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    print(f"🛠️ Executing: {tool_name}")
                    
                    # Route the tool call to the correct server session
                    session = tool_sessions.get(tool_name)
                    if session:
                        try:
                            result = await session.call_tool(tool_name, tool_args)
                            tool_result_text = result.content[0].text
                            print(f"📨 Result received from tool (passing back to AI...)") 
                        except Exception as e:
                            tool_result_text = f"Error: {str(e)}"
                            print(tool_result_text)
                    else:
                        tool_result_text = "Error: Tool not found."
                        
                    # Feed the tool's result back to the AI
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result_text
                    })

if __name__ == "__main__":
    # A master prompt that flexes BOTH systems
    test_prompt = """Analyze this commit log. What's the risk? Once you have the analysis, send the RISK_LEVEL and KEY_FINDING via WhatsApp to 918660573165.
    
    2024-01-03 alex.chen@corp.com "DB auth bypass for speed"
    2024-01-09 alex.chen@corp.com "Rewrite payment gateway"
    2024-01-12 alex.chen@corp.com "Patch session token generation"
    2024-01-15 bob.jones@corp.com "Update dependencies"
    """
    
    asyncio.run(run_whatsapp_agent(test_prompt))
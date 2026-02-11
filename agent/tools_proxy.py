import requests
from config import MCP_URL

def call_mcp_tool(tool_name: str):
    r = requests.post(f"{MCP_URL}/call/{tool_name}", timeout=5)
    return r.json()

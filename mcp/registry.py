from typing import Any, Dict


def call_mcp_tool(tool_name: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}

    if tool_name == "commands":
        return {
            "description": "CLI, RPC and operational commands for Monad network",
            "usage": "Use to show available infrastructure or node commands",
            "data": payload,
        }

    return {
        "error": f"Unknown MCP tool: {tool_name}"
    }

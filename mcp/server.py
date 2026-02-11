from fastapi import FastAPI
from mcp.tools import query_parallelism

app = FastAPI(title="Monad MCP")


@app.post("/call/{tool}")
def call_tool(tool: str):
    if tool == "query_perfomance":
        return query_perfomance()
    return {"error": "unknown tool"}

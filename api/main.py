from fastapi import FastAPI
from pydantic import BaseModel
from agent.agent import handle_query

app = FastAPI()


class Query(BaseModel):
    query: str


@app.post("/api/ai/query")
async def query_ai(q: Query):
    return await handle_query(q.query)

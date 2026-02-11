from agent.context import build_context
from agent.response import generate_answer


async def handle_query(query: str):
    """
    Main orchestration entrypoint for MonadAI.

    Orchestrates:
      1) intent detection + grounded context assembly (snapshots/DB)
      2) answer generation strictly from provided context/tools
    """

    intent, context, tools = build_context(query)

    answer = generate_answer(
        query=query,
        intent=intent,
        context=context,
        tools=tools,
    )

    return {
        "intent": intent,
        "answer": answer,
        "sources": list(context.keys()) if context else [],
        "tools_used": tools or [],
    }

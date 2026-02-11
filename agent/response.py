from typing import Dict, Any, List
from agent.prompts import SYSTEM_PROMPT
from agent.llm import call_llm


def human_number(value: Any) -> str:
    try:
        n = float(value)
    except (TypeError, ValueError):
        return str(value)

    if abs(n) >= 1_000_000_000:
        return f"{n/1_000_000_000:.2f}B"
    if abs(n) >= 1_000_000:
        return f"{n/1_000_000:.2f}M"
    if abs(n) >= 1_000:
        return f"{n/1_000:.2f}K"

    return f"{n:.2f}".rstrip("0").rstrip(".")


def _format_context(context: Dict[str, Any]) -> str:
    blocks = []

    for key, rows in context.items():
        if not rows:
            continue

        blocks.append(f"\n### {key.upper()}\n")

        for row in rows:
            if isinstance(row, dict):
                parts = []
                for k, v in row.items():
                    if v is None:
                        continue
                    parts.append(f"{k}: {human_number(v)}")
                line = ", ".join(parts)
            else:
                line = ", ".join(human_number(x) for x in row if x is not None)

            blocks.append(f"- {line}")

    return "\n".join(blocks)


def _format_tools(tools: List[str]) -> str:
    if not tools:
        return ""

    return (
        "\n\n### AVAILABLE TOOLS\n"
        "You may reference the following tools if relevant:\n"
        + "\n".join(f"- {t}" for t in tools)
    )


def quick_reply(intent: str) -> str | None:
    if intent == "greeting":
        return (
            "👋 Hello. I’m MonadAI.\n\n"
            "You can ask about:\n"
            "- network health / overview\n"
            "- top validators by stake\n"
            "- economics dynamics (price / staking)\n"
            "- infrastructure visibility and commands"
        )

    if intent == "unknown":
        return (
            "I didn’t understand the request.\n"
            "Try asking about network status, validators, economics, infrastructure, or commands."
        )

    if intent == "gratitude":
        return "👋 You’re welcome! If you have more questions about the Monad network, feel free to ask."

    if intent == "capabilities":
        return (
            "🤖 **What I can do:**\n"
            "- Explain Monad network health and KPI snapshots\n"
            "- Show top validators and stake distribution (if available)\n"
            "- Explain price, staking, and delegator trends (snapshot-based)\n"
            "- Summarize infrastructure visibility (geo/providers) when present\n"
            "- Provide CLI / RPC / operational commands\n\n"
            "All answers are based strictly on prepared context and internal snapshots."
        )

    return None


def generate_answer(
    *,
    query: str,
    intent: str,
    context: Dict[str, Any],
    tools: List[str],
) -> str:
    fast = quick_reply(intent)
    if fast:
        return fast

    if "error" in context:
        return context["error"][0]["message"]

    context_block = _format_context(context)
    tools_block = _format_tools(tools)

    prompt = f"""
{SYSTEM_PROMPT}

====================
USER QUESTION
====================
{query}

====================
DETECTED INTENT
====================
{intent}

====================
FACTUAL CONTEXT (SNAPSHOT)
====================
{context_block}

{tools_block}

====================
INSTRUCTIONS
====================
- Use ONLY the data above
- Do NOT invent missing facts
- If data is insufficient, say so clearly
- Convert large numbers into readable units (K, M, B)
- Keep the answer concise and structured
"""

    return call_llm(prompt)

def detect_intent(query: str) -> str:
    q = query.lower().strip()

    if q in (
        "hello",
        "hi",
        "hey",
        "gm",
        "good morning",
        "good evening"
    ):
        return "greeting"

    if q in (
        "thanks",
        "thank you",
        "thx",
        "thanks!",
        "thank you!"
    ):
        return "gratitude"

    if any(k in q for k in [
        "what can you do",
        "what are you capable of",
        "your capabilities"
    ]):
        return "capabilities"

    if any(k in q for k in [
        "command",
        "how to",
        "cli",
        "rpc",
        "api",
        "restart",
        "start node",
        "stop node",
        "check logs",
        "delegate",
        "undelegate",
        "unstake",
        "validator command",
        "block height",
        "get balance",
        "price via api"
    ]):
        return "commands"

    if any(k in q for k in [
        "top 5 validators",
        "top validators",
        "validators by stake",
        "validators by delegation",
        "by stake",
        "by delegation",
        "most staked",
        "highest stake",
        "largest stake",
        "validator ranking"
    ]):
        return "validators_ranking"

    if any(k in q for k in [
        "validators",
        "validator set",
        "active validators",
        "validator stats",
        "commission",
        "decentralization"
    ]):
        return "validators"

    if any(k in q for k in [
        "asset",
        "assets",
        "license",
        "licenses",
        "derivation",
        "derivations",
        "ip activity",
        "asset growth",
        "licenses growth",
        "derivations growth"
    ]):
        return "assets"

    if any(k in q for k in [
        "price",
        "staking",
        "apr",
        "inflation",
        "token economics",
        "staked",
        "delegators growth"
    ]):
        return "economics"

    if any(k in q for k in [
        "infrastructure",
        "nodes",
        "geo",
        "countries",
        "providers",
        "hosting",
        "rpc distribution"
    ]):
        return "infrastructure"

    if any(k in q for k in [
        "overview",
        "network state",
        "network health",
        "how healthy",
        "monad network",
        "summary"
    ]):
        return "general"

    return "unknown"

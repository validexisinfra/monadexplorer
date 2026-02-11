from agent.intent import detect_intent
from agent.sql_tools import query_db


def build_context(query: str):
  
    intent = detect_intent(query)
    ctx = {}
    tools = []

    if intent in ("greeting", "gratitude", "capabilities", "unknown"):
        return intent, ctx, tools

    if intent == "general":
        rows = query_db("""
        SELECT
            validators_count,
            delegators_count,
            staked_total,
            monad_price_usd,
            apr_percent,
            current_block_height
        FROM network
        WHERE id = 1
        """)
        if not rows:
            ctx["error"] = [{
                "message": "Network overview snapshot is unavailable."
            }]
        else:
            ctx["overview"] = rows

    if intent == "assets":
        assets = query_db("""
        SELECT d1 AS last_24h, h1 AS last_1h, m1 AS last_1m
        FROM kpi_timeseries
        WHERE metric = 'assets'
        """)
        licenses = query_db("""
        SELECT d1 AS last_24h, h1 AS last_1h, m1 AS last_1m
        FROM kpi_timeseries
        WHERE metric = 'licenses'
        """)
        derivations = query_db("""
        SELECT d1 AS last_24h, h1 AS last_1h, m1 AS last_1m
        FROM kpi_timeseries
        WHERE metric = 'derivations'
        """)
      
        if not assets and not licenses and not derivations:
            ctx["error"] = [{
                "message": "Ecosystem growth metrics (assets/licenses/derivations) are not available in the current Monad snapshots."
            }]
        else:
            if assets:
                ctx["assets_growth"] = assets
            if licenses:
                ctx["licenses_growth"] = licenses
            if derivations:
                ctx["derivations_growth"] = derivations

    if intent == "validators_ranking":
        rows = query_db("""
        SELECT
            name AS moniker,
            CAST(stake AS REAL) AS bonded_tokens,
            commission_rate
        FROM validators
        WHERE stake IS NOT NULL
        ORDER BY CAST(stake AS REAL) DESC
        LIMIT 5
        """)
        if not rows:
            ctx["error"] = [{
                "message": "Validator stake distribution data is unavailable."
            }]
        else:
            ctx["top_validators"] = rows

    if intent == "validators":
        rows = query_db("""
        SELECT
            COUNT(*) AS total_validators,
            SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) AS active_validators,
            AVG(commission_rate) AS avg_commission
        FROM validators
        """)
        if not rows:
            ctx["error"] = [{
                "message": "Validator set statistics are unavailable."
            }]
        else:
            ctx["validators_stats"] = rows

    if intent == "economics":
        price = query_db("""
        SELECT d1 AS last_24h, h1 AS last_1h
        FROM kpi_timeseries
        WHERE metric = 'price'
        """)
        staked = query_db("""
        SELECT d1 AS last_24h, h1 AS last_1h
        FROM kpi_timeseries
        WHERE metric = 'staked'
        """)
        delegators = query_db("""
        SELECT d1 AS last_24h, h1 AS last_1h
        FROM kpi_timeseries
        WHERE metric = 'delegators'
        """)

        if not price and not staked and not delegators:
            ctx["error"] = [{
                "message": "Economics dynamics (price/staked/delegators) are unavailable in the current Monad snapshots."
            }]
        else:
            if price:
                ctx["price_dynamics"] = price
            if staked:
                ctx["staking_dynamics"] = staked
            if delegators:
                ctx["delegators_dynamics"] = delegators

    if intent == "infrastructure":
        geo = query_db("""
        SELECT country, COUNT(*) AS nodes
        FROM infra_location
        WHERE country IS NOT NULL AND country != ''
        GROUP BY country
        ORDER BY nodes DESC
        LIMIT 10
        """)
        providers = query_db("""
        SELECT org, COUNT(*) AS nodes
        FROM infra_location
        WHERE org IS NOT NULL AND org != ''
        GROUP BY org
        ORDER BY nodes DESC
        LIMIT 10
        """)

        if not geo and not providers:
            ctx["error"] = [{
                "message": "Infrastructure visibility data (geo/providers) is unavailable in the current Monad snapshots."
            }]
        else:
            if geo:
                ctx["geo_distribution"] = geo
            if providers:
                ctx["providers"] = providers

    if intent == "commands":
        rows = query_db("""
        SELECT category, cmd_or_url, description
        FROM commands
        ORDER BY category, id
        """)
        if not rows:
            ctx["error"] = [{
                "message": "Command knowledge base is unavailable."
            }]
        else:
            ctx["commands"] = rows
            tools.append("commands")

    return intent, ctx, tools

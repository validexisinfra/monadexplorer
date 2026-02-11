#!/usr/bin/env python3
import json
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = "/db/monad.db"

NODESTATS_JSON = "PATH_TO_FILE"
NODEFULL_JSON = "PATH_TO_FILE"
MPI_JSON = "PATH_TO_FILE"
PRICE_JSON = "PATH_TO_FILE"
NODES_JSON = "PATH_TO_FILE"
INFRA_JSON = "PATH_TO_FILE"
COMMANDS_JSON = "PATH_TO_FILE"


def normalize_status(raw):
    if raw == "BOND_STATUS_BONDED":
        return "active"
    if raw == "BOND_STATUS_UNBONDED":
        return "inactive"
    return raw


def ensure_schema(cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS validators (
        operator_address TEXT PRIMARY KEY,
        name TEXT,
        status TEXT,
        jailed TEXT,
        tokens TEXT,
        stake TEXT,
        commission_rate REAL,
        commission_max_rate REAL,
        node_version TEXT,
        network TEXT,
        p2p_protocol_version TEXT,
        block_protocol_version TEXT,
        app_protocol_version TEXT,
        latest_block_height INTEGER,
        catching_up TEXT,
        latest_block_time TEXT,
        earliest_block_height INTEGER,
        earliest_block_time TEXT
    );
    """)

    ts_cols = ["metric TEXT PRIMARY KEY"]
    for i in range(1, 61): ts_cols.append(f"m{i} REAL")
    for i in range(1, 25): ts_cols.append(f"h{i} REAL")
    for i in range(1, 31): ts_cols.append(f"d{i} REAL")

    cur.execute(f"CREATE TABLE IF NOT EXISTS kpi_timeseries ({', '.join(ts_cols)});")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS network (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        validators_count INTEGER,
        delegators_count INTEGER,
        staked_total_raw TEXT,
        staked_total TEXT,
        current_block_height INTEGER,
        monad_price_usd REAL,
        apr_percent REAL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS infra_location (
        peer_id TEXT PRIMARY KEY,
        network TEXT,
        generated_at TEXT,
        unique_nodes INTEGER,
        rpc_sources INTEGER,
        validators_visibility TEXT,
        ports TEXT,
        seen_on_rpcs INTEGER,
        city TEXT,
        region TEXT,
        country TEXT,
        org TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS commands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        cmd_or_url TEXT,
        params TEXT,
        description TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS parallelism (
        metric TEXT PRIMARY KEY,
        m1 REAL, m2 REAL, m3 REAL, m4 REAL, m5 REAL, m6 REAL, m7 REAL, m8 REAL, m9 REAL, m10 REAL,
        m11 REAL, m12 REAL, m13 REAL, m14 REAL, m15 REAL, m16 REAL, m17 REAL, m18 REAL, m19 REAL, m20 REAL,
        m21 REAL, m22 REAL, m23 REAL, m24 REAL, m25 REAL, m26 REAL, m27 REAL, m28 REAL, m29 REAL, m30 REAL,
        m31 REAL, m32 REAL, m33 REAL, m34 REAL, m35 REAL, m36 REAL, m37 REAL, m38 REAL, m39 REAL, m40 REAL,
        m41 REAL, m42 REAL, m43 REAL, m44 REAL, m45 REAL, m46 REAL, m47 REAL, m48 REAL, m49 REAL, m50 REAL,
        m51 REAL, m52 REAL, m53 REAL, m54 REAL, m55 REAL, m56 REAL, m57 REAL, m58 REAL, m59 REAL, m60 REAL,
        h1 REAL, h2 REAL, h3 REAL, h4 REAL, h5 REAL, h6 REAL, h7 REAL, h8 REAL, h9 REAL, h10 REAL, h11 REAL, h12 REAL,
        h13 REAL, h14 REAL, h15 REAL, h16 REAL, h17 REAL, h18 REAL, h19 REAL, h20 REAL, h21 REAL, h22 REAL, h23 REAL, h24 REAL,
        d1 REAL, d2 REAL, d3 REAL, d4 REAL, d5 REAL, d6 REAL, d7 REAL, d8 REAL, d9 REAL, d10 REAL,
        d11 REAL, d12 REAL, d13 REAL, d14 REAL, d15 REAL, d16 REAL, d17 REAL, d18 REAL, d19 REAL, d20 REAL,
        d21 REAL, d22 REAL, d23 REAL, d24 REAL, d25 REAL, d26 REAL, d27 REAL, d28 REAL, d29 REAL, d30 REAL
    );
    """)


def import_validators(cur):
    if Path(NODESTATS_JSON).exists():
        with open(NODESTATS_JSON, "r", encoding="utf-8") as f:
            base = json.load(f)
        for v in base:
            cur.execute("""
            INSERT OR IGNORE INTO validators (
                operator_address, name, status, commission_rate
            ) VALUES (?, ?, ?, ?);
            """, (
                v.get("operator_address") or v.get("operatorAddress") or v.get("address"),
                v.get("moniker") or v.get("name"),
                normalize_status(v.get("status")),
                float(v.get("commission_rate_percent") or v.get("commission_rate") or v.get("commission")) if (v.get("commission_rate_percent") or v.get("commission_rate") or v.get("commission")) else None
            ))

    if Path(NODEFULL_JSON).exists():
        with open(NODEFULL_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)

        validators_map = data.get("validators", data) if isinstance(data, dict) else {}
        for addr, v in validators_map.items():
            p = v.get("profile", v.get("profile", {})) if isinstance(v, dict) else {}
            s = v.get("staking", v.get("staking", {})) if isinstance(v, dict) else {}
            rpc = v.get("rpc", {}).get("status", {}) if isinstance(v, dict) else {}
            ni = rpc.get("node_info", {})
            si = rpc.get("sync_info", {})
            pv = ni.get("protocol_version", {})

            cur.execute("""
            INSERT INTO validators VALUES (
                ?,?,?,?,?,?,?,?,
                ?,?,
                ?,?,?,
                ?,?,?,
                ?,?
            )
            ON CONFLICT(operator_address) DO UPDATE SET
                name=excluded.name,
                status=excluded.status,
                jailed=excluded.jailed,
                tokens=excluded.tokens,
                stake=excluded.stake,
                commission_rate=excluded.commission_rate,
                commission_max_rate=excluded.commission_max_rate,
                node_version=excluded.node_version,
                network=excluded.network,
                p2p_protocol_version=excluded.p2p_protocol_version,
                block_protocol_version=excluded.block_protocol_version,
                app_protocol_version=excluded.app_protocol_version,
                latest_block_height=excluded.latest_block_height,
                catching_up=excluded.catching_up,
                latest_block_time=excluded.latest_block_time,
                earliest_block_height=excluded.earliest_block_height,
                earliest_block_time=excluded.earliest_block_time;
            """, (
                addr,
                p.get("moniker") or p.get("name") or v.get("name"),
                normalize_status(p.get("status") or v.get("status")),
                p.get("jailed") if "jailed" in p else v.get("jailed"),
                s.get("tokens"),
                s.get("delegator_shares") or s.get("stake") or v.get("stake"),
                float(s.get("commission_rate")) if s.get("commission_rate") else None,
                float(s.get("commission_max_rate")) if s.get("commission_max_rate") else None,
                ni.get("version"),
                ni.get("network"),
                pv.get("p2p"),
                pv.get("block"),
                pv.get("app"),
                int(si.get("latest_block_height")) if si.get("latest_block_height") else None,
                str(si.get("catching_up")) if si.get("catching_up") is not None else None,
                si.get("latest_block_time"),
                int(si.get("earliest_block_height")) if si.get("earliest_block_height") else None,
                si.get("earliest_block_time"),
            ))


def import_timeseries(cur, path, ts_key, mapping, table):
    if not Path(path).exists():
        return

    with open(path, "r", encoding="utf-8") as f:
        snaps = json.load(f)

    if len(snaps) < 2:
        return

    def safe_float(x):
        try:
            return float(x)
        except (TypeError, ValueError):
            return 0.0

    snaps = [s for s in snaps if ts_key in s]
    snaps.sort(key=lambda x: x[ts_key])

    parsed = []
    for s in snaps:
        row = {"ts": datetime.fromisoformat(s[ts_key].replace("Z", "+00:00"))}
        for metric, field in mapping.items():
            row[metric] = safe_float(s.get(field))
        parsed.append(row)

    if len(parsed) < 2:
        return

    now = parsed[-1]["ts"]

    buckets = {
        metric: {"m": [0.0] * 60, "h": [0.0] * 24, "d": [0.0] * 30}
        for metric in mapping
    }

    for prev, curr in zip(parsed, parsed[1:]):
        dt_min = int((now - curr["ts"]).total_seconds() // 60)
        dt_hour = dt_min // 60
        dt_day = dt_hour // 24

        for metric in mapping:
            delta = curr[metric] - prev[metric]

            for i in range(60):
                if dt_min <= i:
                    buckets[metric]["m"][i] += delta

            for i in range(24):
                if dt_hour <= i:
                    buckets[metric]["h"][i] += delta

            for i in range(30):
                if dt_day <= i:
                    buckets[metric]["d"][i] += delta

    for metric, data in buckets.items():
        values = [metric] + data["m"] + data["h"] + data["d"]
        placeholders = ",".join(["?"] * len(values))
        updates = (
            [f"m{i}=excluded.m{i}" for i in range(1, 61)]
            + [f"h{i}=excluded.h{i}" for i in range(1, 25)]
            + [f"d{i}=excluded.d{i}" for i in range(1, 31)]
        )

        cur.execute(
            f"""
            INSERT INTO {table}
            VALUES ({placeholders})
            ON CONFLICT(metric) DO UPDATE SET {",".join(updates)}
            """,
            values
        )


def import_network(cur):
    if not Path(NODES_JSON).exists():
        return

    with open(NODES_JSON, "r", encoding="utf-8") as f:
        d = json.load(f)

    cur.execute("""
    INSERT INTO network VALUES (1,?,?,?,?,?,?,?)
    ON CONFLICT(id) DO UPDATE SET
        validators_count=excluded.validators_count,
        delegators_count=excluded.delegators_count,
        staked_total_raw=excluded.staked_total_raw,
        staked_total=excluded.staked_total,
        current_block_height=excluded.current_block_height,
        monad_price_usd=excluded.monad_price_usd,
        apr_percent=excluded.apr_percent;
    """, (
        d.get("validators_count"),
        d.get("delegators_count"),
        d.get("staked_total_raw") or d.get("staked_tokens_total_raw"),
        d.get("staked_total") or d.get("staked_tokens_total"),
        d.get("current_block_height"),
        d.get("monad_price_usd") or d.get("price_usd"),
        d.get("apr_percent") or d.get("apr"),
    ))


def import_location(cur):
    if not Path(INFRA_JSON).exists():
        return

    with open(INFRA_JSON, "r", encoding="utf-8") as f:
        d = json.load(f)

    stats = d.get("stats", {})
    for n in d.get("nodes", []):
        geo = n.get("geo", {})
        cur.execute("""
        INSERT INTO infra_location VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(peer_id) DO UPDATE SET
            network=excluded.network,
            generated_at=excluded.generated_at,
            unique_nodes=excluded.unique_nodes,
            rpc_sources=excluded.rpc_sources,
            validators_visibility=excluded.validators_visibility,
            ports=excluded.ports,
            seen_on_rpcs=excluded.seen_on_rpcs,
            city=excluded.city,
            region=excluded.region,
            country=excluded.country,
            org=excluded.org;
        """, (
            n.get("peer_id"),
            d.get("network"),
            d.get("generated_at"),
            stats.get("unique_nodes"),
            stats.get("rpc_sources"),
            stats.get("validators_visibility"),
            json.dumps(n.get("ports", [])),
            n.get("seen_on_rpcs"),
            geo.get("city"),
            geo.get("region"),
            geo.get("country"),
            geo.get("org"),
        ))


def import_commands(cur):
    if not Path(COMMANDS_JSON).exists():
        return

    with open(COMMANDS_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    rows = []
    for category, items in data.items():
        for item in items:
            cmd_or_url = (
                item.get("cmd")
                or item.get("url")
                or item.get("method")
                or item.get("code")
            )
            params = item.get("params")
            rows.append((
                category,
                cmd_or_url,
                json.dumps(params) if params is not None else None,
                item.get("desc")
            ))

    cur.executemany("""
    INSERT INTO commands (category, cmd_or_url, params, description)
    VALUES (?, ?, ?, ?);
    """, rows)


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    ensure_schema(cur)
    import_validators(cur)

    import_timeseries(
        cur,
        MPI_JSON,
        "ts",
        {
            "perfomance": "perfomance",
        },
        "perfomance"
    )

    import_timeseries(
        cur,
        PRICE_JSON,
        "timestamp",
        {
            "price": "monad_price_usd",
            "staked": "staked_total",
            "delegators": "delegators_count",
        },
        "kpi_timeseries"
    )

    import_network(cur)
    import_location(cur)
    import_commands(cur)

    conn.commit()
    conn.close()
    print("[OK] All MonadAI data imported successfully")


if __name__ == "__main__":
    main()

import sqlite3
from config import DB_PATH

def query_db(sql: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    rows = cur.execute(sql).fetchall()
    conn.close()

    return [dict(r) for r in rows]

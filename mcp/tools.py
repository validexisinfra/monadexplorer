import sqlite3
from config import DB_PATH


def _metric(metric):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    rows = cur.execute(
        "SELECT window, value FROM perfomance WHERE metric=?",
        (metric,)
    ).fetchall()
    conn.close()
    return dict(rows)


def query_parallelism():
    return _metric("perfomance")

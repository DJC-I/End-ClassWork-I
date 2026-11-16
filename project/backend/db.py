import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from . import seed

ROOT = Path(__file__).resolve().parents[1]


def path():
    p = Path(os.getenv("SKYROUTE_DB", str(ROOT / "database/skyroute.db")))
    return p if p.is_absolute() else ROOT / p


@contextmanager
def connect():
    p = path()
    p.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(p, timeout=10)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def encode(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False)


def init(reset=False):
    with connect() as con:
        con.executescript(
            """CREATE TABLE IF NOT EXISTS orders (id TEXT PRIMARY KEY, body TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS tasks (id TEXT PRIMARY KEY, body TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS settings (id TEXT PRIMARY KEY, body TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS reports (id TEXT PRIMARY KEY, body TEXT NOT NULL);"""
        )
        if reset:
            for table in ("orders", "tasks", "settings", "reports"):
                con.execute(f"DELETE FROM {table}")
        # A marker prevents deleted-all user records from being silently re-seeded.
        if not con.execute("SELECT 1 FROM settings WHERE id='initialized'").fetchone():
            for table, records in (("orders", seed.ORDERS), ("tasks", seed.TASKS)):
                con.executemany(
                    f"INSERT INTO {table}(id,body) VALUES(?,?)",
                    [(r["id"], encode(r)) for r in records],
                )
            for key, value in (
                ("scenario", "rain"),
                ("growth", seed.GROWTH_CONFIG),
                ("initialized", seed.VERSION),
            ):
                con.execute("INSERT INTO settings VALUES(?,?)", (key, encode(value)))


TABLES = {"orders", "tasks", "settings", "reports"}


def all_rows(table):
    assert table in TABLES
    with connect() as con:
        return [
            json.loads(r["body"])
            for r in con.execute(f"SELECT body FROM {table} ORDER BY id")
        ]


def get(table, key):
    assert table in TABLES
    with connect() as con:
        row = con.execute(f"SELECT body FROM {table} WHERE id=?", (key,)).fetchone()
        return json.loads(row["body"]) if row else None


def put(table, key, value, create=False):
    assert table in TABLES
    with connect() as con:
        if create:
            con.execute(f"INSERT INTO {table} VALUES(?,?)", (key, encode(value)))
        else:
            con.execute(
                f"INSERT INTO {table} VALUES(?,?) ON CONFLICT(id) DO UPDATE SET body=excluded.body",
                (key, encode(value)),
            )
    return value


def delete(table, key):
    assert table in TABLES
    with connect() as con:
        return con.execute(f"DELETE FROM {table} WHERE id=?", (key,)).rowcount

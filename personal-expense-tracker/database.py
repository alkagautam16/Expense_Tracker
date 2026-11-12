"""All SQLite code lives here."""
import os
import sqlite3

# On a host, set DATABASE_PATH to a persistent disk path. Locally it uses expenses.db.
DB_PATH = os.environ.get("DATABASE_PATH", os.path.join(os.path.dirname(__file__), "expenses.db"))


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # rows behave like dictionaries
    return conn


def init_db():
    """Create tables if they don't exist (runs automatically on start)."""
    with connect() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT DEFAULT '')""")
        c.execute("CREATE TABLE IF NOT EXISTS budget (month TEXT PRIMARY KEY, amount REAL NOT NULL)")


def query(sql, args=(), one=False):
    conn = connect()
    try:
        rows = conn.execute(sql, args).fetchall()
    finally:
        conn.close()
    if one:
        return rows[0] if rows else None
    return rows


def execute(sql, args=()):
    conn = connect()
    try:
        with conn:
            conn.execute(sql, args)
    finally:
        conn.close()

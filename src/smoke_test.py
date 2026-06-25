from __future__ import annotations

import importlib
import sqlite3
from pathlib import Path

from sql_safety import UnsafeSQLError, ensure_limit


ROOT_DIR = Path(__file__).resolve().parents[1]
DB_PATH = ROOT_DIR / "db" / "nba_analysis.sqlite"


def check_imports() -> None:
    for module_name in ["pandas", "sqlalchemy", "streamlit", "langchain", "openai", "plotly"]:
        importlib.import_module(module_name)
    print("Python package imports: ok")


def check_database() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DB_PATH}")
    with sqlite3.connect(DB_PATH) as conn:
        table_count = conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
        ).fetchone()[0]
        game_count = conn.execute("SELECT COUNT(*) FROM games").fetchone()[0]
    if table_count < 5 or game_count == 0:
        raise RuntimeError("Database exists but required tables/data are missing.")
    print(f"SQLite database: ok ({table_count} tables, {game_count} games)")


def check_sql_safety() -> None:
    limited = ensure_limit("SELECT season, COUNT(*) AS games FROM games GROUP BY season", 5)
    if "LIMIT 5" not in limited:
        raise RuntimeError("Expected SELECT query to receive a default LIMIT.")
    try:
        ensure_limit("DROP TABLE games")
    except UnsafeSQLError:
        print("SQL safety: ok")
        return
    raise RuntimeError("Unsafe SQL was not rejected.")


def main() -> int:
    check_imports()
    check_database()
    check_sql_safety()
    print("Smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

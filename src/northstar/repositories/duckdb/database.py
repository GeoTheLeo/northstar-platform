"""
NorthStar DuckDB Database

Central connection manager for the analytical warehouse.
"""

from pathlib import Path

import duckdb

BASE_DIR = Path(__file__).resolve().parents[4]

DATABASE_PATH = BASE_DIR / "data" / "warehouse" / "northstar.duckdb"


def connect() -> duckdb.DuckDBPyConnection:
    """
    Return a DuckDB connection.
    """

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    return duckdb.connect(str(DATABASE_PATH))

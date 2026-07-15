"""
Warehouse Bootstrap

Initializes the NorthStar analytical warehouse.
"""

from northstar.repositories.duckdb.database import (
    connect,
)


def bootstrap():

    connection = connect()

    connection.execute(
        """
        CREATE SCHEMA IF NOT EXISTS analytics;
        """
    )

    connection.close()


if __name__ == "__main__":
    bootstrap()
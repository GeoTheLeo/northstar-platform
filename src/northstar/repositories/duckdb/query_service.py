"""
DuckDB Query Service
"""

from northstar.repositories.duckdb.database import (
    connect,
)


class QueryService:
    """
    Execute warehouse queries.
    """

    def __init__(self):

        self.connection = connect()

    def execute(
        self,
        sql: str,
    ):
        """
        Execute arbitrary SQL.
        """

        return self.connection.execute(sql)

    def fetch_dataframe(
        self,
        sql: str,
    ):
        """
        Execute SQL and return a DataFrame.
        """

        return (
            self.connection
            .execute(sql)
            .fetchdf()
        )

    def close(self):
        self.connection.close()
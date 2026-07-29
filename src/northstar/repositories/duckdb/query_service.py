"""
DuckDB Query Service
"""

from duckdb import DuckDBPyConnection
from pandas import DataFrame

from northstar.repositories.duckdb.database import (
    connect,
)


class QueryService:
    """
    Execute warehouse queries.
    """

    def __init__(self) -> None:
        self.connection: DuckDBPyConnection = connect()

    def execute(
        self,
        sql: str,
    ) -> DuckDBPyConnection:
        """
        Execute arbitrary SQL.
        """

        return self.connection.execute(sql)

    def fetch_dataframe(
        self,
        sql: str,
    ) -> DataFrame:
        """
        Execute SQL and return a DataFrame.
        """

        return self.connection.execute(sql).fetchdf()

    def close(self) -> None:
        """
        Close the database connection.
        """

        self.connection.close()
"""
DuckDB Query Service
"""

from northstar.repositories.duckdb.database import (
    connect,
)


class QueryService:

    def __init__(self):

        self.connection = connect()

    def executive_dashboard(self):

        return self.connection.execute(
            """
            SELECT *

            FROM northstar.executive_dashboard
            """
        ).fetchdf()
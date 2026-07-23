"""
Warehouse Bootstrap

Initializes and populates the NorthStar analytical warehouse.
"""

from bi.data.sample_data import load_dashboard_data

from northstar.repositories.duckdb.database import (
    connect,
)


def bootstrap() -> None:
    """
    Build and populate the warehouse.
    """

    connection = connect()

    connection.execute(
        """
        CREATE SCHEMA IF NOT EXISTS analytics;
        """
    )

    learner_df = load_dashboard_data()

    connection.register(
        "learner_df",
        learner_df,
    )

    connection.execute(
        """
        CREATE OR REPLACE TABLE
            analytics.learners
        AS
        SELECT *
        FROM learner_df;
        """
    )

    connection.unregister(
        "learner_df"
    )

    connection.close()


if __name__ == "__main__":
    bootstrap()
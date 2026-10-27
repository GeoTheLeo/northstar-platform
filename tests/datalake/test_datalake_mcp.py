"""
The read-only data lake MCP server, against a simulated S3 bucket (moto).

Runs in the knowledge-agent environment (.venv-agent); skipped where moto or
the MCP SDK isn't installed.
"""

import io
import json

import pandas as pd
import pytest

boto3 = pytest.importorskip("boto3")
moto = pytest.importorskip("moto")
pytest.importorskip("mcp")

from datalake_mcp import server  # noqa: E402

BUCKET = "northstar-datalake-test"


@pytest.fixture(autouse=True)
def lake(monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-central-1")
    with moto.mock_aws():
        s3 = boto3.client("s3", region_name="eu-central-1")
        s3.create_bucket(Bucket=BUCKET, CreateBucketConfiguration={"LocationConstraint": "eu-central-1"})
        tables = {
            "learners": pd.DataFrame({
                "learner_id": ["L1", "L2", "L3", "L4"],
                "campus": ["Berlin", "Berlin", "Munich", "Munich"],
                "attendance": [95, 60, 80, 55],
            }),
            "risk_predictions": pd.DataFrame({"learner_id": ["L1", "L2", "L3", "L4"], "at_risk": [0, 1, 0, 1]}),
        }
        for name, df in tables.items():
            buf = io.BytesIO()
            df.to_parquet(buf, index=False)
            s3.put_object(Bucket=BUCKET, Key=f"northstar/{name}.parquet", Body=buf.getvalue())
        monkeypatch.setattr(server, "_lake", server.S3DataLake(BUCKET, "northstar/", s3=s3))
        yield s3


def test_lists_only_the_datasets_present_in_s3():
    out = json.loads(server.list_datasets())
    assert out["source"] == f"s3://{BUCKET}/northstar/"
    assert [d["dataset"] for d in out["datasets"]] == ["learners", "risk_predictions"]


def test_join_filter_group_and_count():
    out = json.loads(server.query_dataset(
        "learners", join=["risk_predictions"],
        filters=[{"column": "at_risk", "op": "==", "value": 1}],
        group_by=["campus"], metrics=[{"column": "learner_id", "agg": "count"}],
    ))
    assert {r["campus"]: r["count_learner_id"] for r in out["rows"]} == {"Berlin": 1, "Munich": 1}
    assert out["matched_rows"] == 2


def test_aggregate_without_group():
    out = json.loads(server.query_dataset("learners", metrics=[{"column": "attendance", "agg": "mean"}]))
    assert out["rows"] == [{"mean_attendance": 72.5}]


@pytest.mark.parametrize("kwargs, message", [
    ({"dataset": "salaries"}, "unknown dataset"),
    ({"dataset": "learners", "filters": [{"column": "password", "op": "==", "value": 1}]}, "unknown column"),
    ({"dataset": "learners", "filters": [{"column": "attendance", "op": "; DROP", "value": 1}]}, "unsupported operator"),
    ({"dataset": "learners", "group_by": ["campus"]}, "needs at least one metric"),
    ({"dataset": "learners", "metrics": [{"column": "attendance", "agg": "delete"}]}, "unsupported agg"),
])
def test_requests_outside_the_contract_are_refused(kwargs, message):
    with pytest.raises(server.DataLakeError, match=message):
        server.query_dataset(**kwargs)


def test_limit_is_capped():
    out = json.loads(server.query_dataset("learners", limit=10_000))
    assert out["returned_rows"] == 4  # all rows, never more than MAX_ROWS


def test_every_tool_is_read_only():
    tools = {t.name: t for t in server.build_server()._tool_manager.list_tools()}
    assert set(tools) == {"list_datasets", "describe_dataset", "query_dataset"}
    assert all(t.annotations.model_dump(by_alias=True)["readOnlyHint"] for t in tools.values())


def test_http_requires_the_api_key():
    from starlette.testclient import TestClient

    with TestClient(server.http_app(host="0.0.0.0", api_key="k")) as client:
        assert client.get("/healthz").json() == {"status": "ok"}
        assert client.post("/mcp", json={}).status_code == 401


def test_grouped_results_are_sorted_so_limit_one_is_the_top_group():
    out = json.loads(server.query_dataset(
        "learners", group_by=["campus"], metrics=[{"column": "attendance", "agg": "mean"}], limit=1,
    ))
    # Berlin mean 77.5 vs. Munich 67.5: the top group, not the alphabetically first one.
    assert out["rows"] == [{"campus": "Berlin", "mean_attendance": 77.5}]
    low = json.loads(server.query_dataset(
        "learners", group_by=["campus"], metrics=[{"column": "attendance", "agg": "mean"}],
        order_by="mean_attendance", descending=False, limit=1,
    ))
    assert low["rows"][0]["campus"] == "Munich"

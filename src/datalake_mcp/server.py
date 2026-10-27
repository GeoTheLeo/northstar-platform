"""
Read-only MCP server over the NorthStar learner data lake in Amazon S3.

Lets an agent running in Azure (src/knowledge_agent) read cross-cloud data in
an AWS data lake without copying it: the server reads Parquet objects from
s3://$DATALAKE_BUCKET/$DATALAKE_PREFIX and exposes three read-only tools.

Read-only at every layer:
- the server uses only s3:ListBucket and s3:GetObject (IAM policy in
  src/knowledge_agent/README.md); there is no write code path;
- the tools are annotated readOnlyHint=True;
- queries are a validated JSON spec (filters, group-by, aggregates, limit),
  not SQL, so nothing can be executed beyond what the spec allows.

    DATALAKE_BUCKET=northstar-datalake DATALAKE_MCP_API_KEY=... \
        python -m datalake_mcp.server --http 8790 --host 0.0.0.0

AWS credentials come from the standard boto3 chain. AWS_ENDPOINT_URL points
it at an S3-compatible endpoint instead (the tests use moto).
"""

from __future__ import annotations

import argparse
import hmac
import io
import json
import os
import threading
import time

import pandas as pd

DATASETS = ("learners", "risk_predictions", "segments", "interventions")
JOIN_KEY = "learner_id"
OPS = {"==", "!=", ">", ">=", "<", "<=", "in"}
AGGS = {"count", "mean", "sum", "min", "max"}
MAX_ROWS = 200
CACHE_TTL_S = 300


class DataLakeError(ValueError):
    """A request the read-only contract doesn't allow; the message tells the agent why."""


class S3DataLake:
    """Parquet tables in S3, read on demand and cached briefly."""

    def __init__(self, bucket: str | None = None, prefix: str | None = None, s3=None) -> None:
        self.bucket = bucket or os.environ["DATALAKE_BUCKET"]
        self.prefix = prefix if prefix is not None else os.environ.get("DATALAKE_PREFIX", "northstar/")
        self._s3 = s3
        self._cache: dict[str, tuple[float, pd.DataFrame]] = {}
        self._lock = threading.Lock()

    @property
    def s3(self):
        if self._s3 is None:
            import boto3

            self._s3 = boto3.client("s3", endpoint_url=os.environ.get("AWS_ENDPOINT_URL") or None)
        return self._s3

    def table(self, name: str) -> pd.DataFrame:
        if name not in DATASETS:
            raise DataLakeError(f"unknown dataset {name!r}; available: {', '.join(DATASETS)}")
        with self._lock:
            cached = self._cache.get(name)
            if cached and time.monotonic() - cached[0] < CACHE_TTL_S:
                return cached[1]
            body = self.s3.get_object(Bucket=self.bucket, Key=f"{self.prefix}{name}.parquet")["Body"].read()
            df = pd.read_parquet(io.BytesIO(body))
            self._cache[name] = (time.monotonic(), df)
            return df

    def available(self) -> list[str]:
        listed = self.s3.list_objects_v2(Bucket=self.bucket, Prefix=self.prefix).get("Contents", [])
        names = {obj["Key"][len(self.prefix):].removesuffix(".parquet") for obj in listed}
        return [d for d in DATASETS if d in names]


_lake: S3DataLake | None = None


def lake() -> S3DataLake:
    global _lake
    if _lake is None:
        _lake = S3DataLake()
    return _lake


def _records(df: pd.DataFrame) -> list[dict]:
    return json.loads(df.to_json(orient="records"))


# ------------------------------------------------------------------ tools (plain functions, testable)


def list_datasets() -> str:
    """List the learner datasets in the NorthStar data lake (AWS S3), with row counts and columns.

    Datasets: learners (campus, program, term, attendance, engagement_score, assessment_score),
    risk_predictions (at_risk from the early-warning model), segments (KMeans segment 0-3), and
    interventions (type and status for at-risk learners). All share the key learner_id.
    """
    out = []
    for name in lake().available():
        df = lake().table(name)
        out.append({"dataset": name, "rows": len(df), "columns": list(df.columns)})
    return json.dumps({"source": f"s3://{lake().bucket}/{lake().prefix}", "datasets": out})


def describe_dataset(dataset: str) -> str:
    """Describe one dataset: column types, a few example rows, and summary statistics.

    Args:
        dataset: One of learners, risk_predictions, segments, interventions.
    """
    df = lake().table(dataset)
    numeric = df.select_dtypes("number")
    categorical = {c: sorted(df[c].dropna().unique().tolist())[:20] for c in df.columns
                   if df[c].dtype == object and c != JOIN_KEY}
    return json.dumps({
        "dataset": dataset,
        "rows": len(df),
        "columns": {c: str(t) for c, t in df.dtypes.items()},
        "categorical_values": categorical,
        "numeric_summary": json.loads(numeric.describe().round(2).to_json()) if not numeric.empty else {},
        "example_rows": _records(df.head(3)),
    })


def _apply_filters(df: pd.DataFrame, filters: list[dict]) -> pd.DataFrame:
    for f in filters:
        column, op, value = f.get("column"), f.get("op", "=="), f.get("value")
        if column not in df.columns:
            raise DataLakeError(f"unknown column {column!r} in filter; columns: {', '.join(df.columns)}")
        if op not in OPS:
            raise DataLakeError(f"unsupported operator {op!r}; use one of {', '.join(sorted(OPS))}")
        series = df[column]
        if op == "in":
            if not isinstance(value, list):
                raise DataLakeError("operator 'in' needs a list value")
            mask = series.isin(value)
        else:
            mask = {"==": series == value, "!=": series != value, ">": series > value,
                    ">=": series >= value, "<": series < value, "<=": series <= value}[op]
        df = df[mask]
    return df


def query_dataset(
    dataset: str,
    join: list[str] | None = None,
    filters: list[dict] | None = None,
    group_by: list[str] | None = None,
    metrics: list[dict] | None = None,
    order_by: str | None = None,
    descending: bool = True,
    limit: int = 50,
) -> str:
    """Query the data lake (read-only): optional joins on learner_id, filters, group-by, and aggregates.

    Grouped results come back sorted by the first metric, largest first, so limit=1 returns the top
    group. Use order_by to sort by another column or metric name (e.g. "mean_attendance").

    Examples:
      at-risk learners per campus: dataset="learners", join=["risk_predictions"],
        filters=[{"column": "at_risk", "op": "==", "value": 1}], group_by=["campus"],
        metrics=[{"column": "learner_id", "agg": "count"}]
      average attendance by segment: dataset="learners", join=["segments"], group_by=["segment"],
        metrics=[{"column": "attendance", "agg": "mean"}]

    Args:
        dataset: Base dataset: learners, risk_predictions, segments, or interventions.
        join: Other datasets to join on learner_id (inner join).
        filters: List of {"column", "op", "value"}; op is one of ==, !=, >, >=, <, <=, in.
        group_by: Columns to group by. Requires metrics.
        metrics: List of {"column", "agg"}; agg is one of count, mean, sum, min, max.
        order_by: Column or metric name (e.g. "count_learner_id") to sort by.
        descending: Sort direction for order_by and for the default grouped sort.
        limit: Maximum rows returned (1-200), applied after sorting.
    """
    df = lake().table(dataset)
    for other in join or []:
        if other == dataset:
            continue
        df = df.merge(lake().table(other), on=JOIN_KEY, how="inner", suffixes=("", f"_{other}"))
    df = _apply_filters(df, filters or [])

    if group_by and not metrics:
        raise DataLakeError("group_by needs at least one metric, e.g. {'column': 'learner_id', 'agg': 'count'}")
    for g in group_by or []:
        if g not in df.columns:
            raise DataLakeError(f"unknown group_by column {g!r}; columns: {', '.join(df.columns)}")

    if metrics:
        named = {}
        for m in metrics:
            column, agg = m.get("column"), m.get("agg")
            if column not in df.columns:
                raise DataLakeError(f"unknown metric column {column!r}; columns: {', '.join(df.columns)}")
            if agg not in AGGS:
                raise DataLakeError(f"unsupported agg {agg!r}; use one of {', '.join(sorted(AGGS))}")
            named[f"{agg}_{column}"] = (column, agg)
        if group_by:
            result = df.groupby(group_by).agg(**named).reset_index()
        else:
            result = pd.DataFrame([{name: df[col].agg(agg) for name, (col, agg) in named.items()}])
        result = result.round(2)
        if group_by and order_by is None:
            # "Top N" must mean top N: never cut grouped results in arbitrary (alphabetical) order.
            order_by = next(iter(named))
    else:
        result = df

    if order_by is not None:
        if order_by not in result.columns:
            raise DataLakeError(f"unknown order_by {order_by!r}; columns: {', '.join(result.columns)}")
        result = result.sort_values(order_by, ascending=not descending, kind="stable")

    limit = max(1, min(int(limit), MAX_ROWS))
    return json.dumps({
        "dataset": dataset,
        "joined": [j for j in (join or []) if j != dataset],
        "matched_rows": len(df),
        "returned_rows": min(len(result), limit),
        "rows": _records(result.head(limit)),
    })


TOOLS = [list_datasets, describe_dataset, query_dataset]


# ------------------------------------------------------------------ MCP server


def build_server():
    from mcp.server import MCPServer
    from mcp.server.mcpserver.exceptions import ToolError
    from mcp_types import ToolAnnotations

    server = MCPServer(
        name="northstar-datalake",
        title="NorthStar learner data lake (AWS S3, read-only)",
        instructions=(
            "Read-only access to NorthStar's learner data in an AWS S3 data lake. Start with list_datasets, "
            "use describe_dataset to see columns and values, and answer numeric questions with query_dataset "
            "(joins on learner_id, filters, group-by, aggregates). Nothing here can modify data."
        ),
    )
    read_only = ToolAnnotations(readOnlyHint=True, openWorldHint=False)

    def wrap(fn):
        import functools

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except DataLakeError as exc:
                raise ToolError(str(exc)) from exc

        return wrapper

    for fn in TOOLS:
        server.tool(annotations=read_only)(wrap(fn))
    return server


class ApiKeyMiddleware:
    """Reject HTTP requests without the right X-API-Key; /healthz stays open for probes."""

    def __init__(self, app, api_key: str) -> None:
        self.app, self.api_key = app, api_key.encode()

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["path"] == "/healthz":
            return await self.app(scope, receive, send)
        if not hmac.compare_digest(dict(scope["headers"]).get(b"x-api-key", b""), self.api_key):
            await send({"type": "http.response.start", "status": 401, "headers": [(b"content-type", b"application/json")]})
            return await send({"type": "http.response.body", "body": b'{"error": "invalid or missing API key"}'})
        return await self.app(scope, receive, send)


def http_app(host: str = "127.0.0.1", api_key: str | None = None):
    from mcp.server.transport_security import TransportSecuritySettings
    from starlette.responses import JSONResponse
    from starlette.routing import Route

    security = None if host in ("127.0.0.1", "localhost") else TransportSecuritySettings(enable_dns_rebinding_protection=False)
    app = build_server().streamable_http_app(host=host, transport_security=security)

    async def healthz(request):
        return JSONResponse({"status": "ok"})

    app.router.routes.append(Route("/healthz", healthz))
    return ApiKeyMiddleware(app, api_key) if api_key else app


def main() -> None:
    import uvicorn

    parser = argparse.ArgumentParser(description="NorthStar data lake MCP server (read-only, AWS S3)")
    parser.add_argument("--http", type=int, default=8790)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()
    api_key = os.environ.get("DATALAKE_MCP_API_KEY") or None
    if args.host not in ("127.0.0.1", "localhost") and not api_key:
        raise SystemExit("refusing to serve beyond localhost without DATALAKE_MCP_API_KEY")
    uvicorn.run(http_app(args.host, api_key), host=args.host, port=args.http)


if __name__ == "__main__":
    main()

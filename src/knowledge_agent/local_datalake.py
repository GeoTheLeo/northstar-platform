"""
Local stand-in for the AWS side: an S3-compatible endpoint (moto) holding the
data lake, plus the data lake MCP server reading from it.

This is a development and evaluation harness, not AWS: the MCP server uses
the real S3 API through boto3, so pointing it at a real bucket is a matter of
AWS credentials and DATALAKE_BUCKET (see README). Run from the repository
root in .venv-agent:

    python src/datalake_mcp/build_datalake.py      # once, in the main environment
    python -m knowledge_agent.local_datalake        # keeps running; Ctrl+C to stop
"""

from __future__ import annotations

import os
import sys
import threading
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LAKE_DIR = PROJECT_ROOT / "data" / "datalake"
S3_PORT = 5555
MCP_PORT = 8790
BUCKET = "northstar-datalake"


def start(api_key: str) -> None:
    import boto3
    import uvicorn
    from moto.server import ThreadedMotoServer

    os.environ.setdefault("AWS_ACCESS_KEY_ID", "local")
    os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "local")
    os.environ.setdefault("AWS_DEFAULT_REGION", "eu-central-1")
    os.environ["AWS_ENDPOINT_URL"] = f"http://127.0.0.1:{S3_PORT}"
    os.environ["DATALAKE_BUCKET"] = BUCKET

    ThreadedMotoServer(ip_address="127.0.0.1", port=S3_PORT).start()
    s3 = boto3.client("s3", endpoint_url=os.environ["AWS_ENDPOINT_URL"])
    s3.create_bucket(Bucket=BUCKET, CreateBucketConfiguration={"LocationConstraint": "eu-central-1"})
    files = sorted(LAKE_DIR.glob("*.parquet"))
    if not files:
        sys.exit("no data lake files; run python src/datalake_mcp/build_datalake.py first")
    for path in files:
        s3.upload_file(str(path), BUCKET, f"northstar/{path.name}")
    print(f"S3 (moto) on :{S3_PORT} with {len(files)} datasets in s3://{BUCKET}/northstar/")

    from datalake_mcp.server import http_app

    print(f"data lake MCP server on http://127.0.0.1:{MCP_PORT}/mcp (X-API-Key required)")
    uvicorn.run(http_app("127.0.0.1", api_key), host="127.0.0.1", port=MCP_PORT, log_level="warning")


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv(PROJECT_ROOT / ".env")
    start(os.environ["DATALAKE_MCP_API_KEY"])

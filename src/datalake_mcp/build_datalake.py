"""
Build the NorthStar learner data lake (Parquet) and optionally upload it to S3.

The cohort is synthetic and seeded (reproducible): 2,000 learners across six
campuses and three programs, two terms. Risk and segment columns are not
invented: they come from NorthStar's own pipelines (EarlyWarningService's
Random Forest and SegmentationService's KMeans), so the lake holds what the
platform would actually produce. Interventions are synthetic, drawn from the
risk scores.

Run from the repository root (main NorthStar environment):

    python src/datalake_mcp/build_datalake.py                 # writes data/datalake/*.parquet
    python src/datalake_mcp/build_datalake.py --upload BUCKET # also uploads to s3://BUCKET/northstar/
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT / "src"))

OUT_DIR = PROJECT_ROOT / "data" / "datalake"
PREFIX = "northstar/"
SEED = 20261027

CAMPUSES = ["Berlin", "Munich", "Hamburg", "Shanghai", "Beijing", "San Francisco"]
PROGRAMS = ["General English", "Business English", "Exam Preparation"]
TERMS = ["2026-S1", "2026-S2"]
INTERVENTIONS = ["advisor outreach", "academic coaching", "attendance plan", "peer mentoring"]


def build_learners(n: int = 2000, seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    campus = rng.choice(CAMPUSES, n)
    program = rng.choice(PROGRAMS, n, p=[0.5, 0.3, 0.2])
    # A latent "momentum" drives all three scores, so they correlate the way real ones do.
    momentum = rng.normal(0, 1, n) + np.where(program == "Exam Preparation", 0.3, 0.0)
    noise = lambda scale: rng.normal(0, scale, n)  # noqa: E731
    clip = lambda x: np.clip(np.round(x), 0, 100).astype(int)  # noqa: E731
    return pd.DataFrame(
        {
            "learner_id": [f"L{i:05d}" for i in range(1, n + 1)],
            "campus": campus,
            "program": program,
            "term": rng.choice(TERMS, n),
            "attendance": clip(80 + 9 * momentum + noise(6)),
            "engagement_score": clip(72 + 11 * momentum + noise(8)),
            "assessment_score": clip(70 + 12 * momentum + noise(9)),
        }
    )


def score(learners: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    import tempfile

    import northstar.early_warning.models.train_model as ew_train
    import northstar.segmentation.clustering.train_cluster_model as seg_train
    from northstar.services.early_warning_service import EarlyWarningService
    from northstar.services.segmentation_service import SegmentationService

    # Both services save a model whenever they (re)train. Point those saves at a
    # scratch folder so building the lake never overwrites the committed models.
    scratch = Path(tempfile.mkdtemp(prefix="datalake_models_"))
    ew_train.EARLY_WARNING_MODEL_PATH = scratch / "early_warning_model.pkl"
    seg_train.SEGMENTATION_MODEL_PATH = scratch / "segmentation_model.pkl"

    risk = EarlyWarningService().predict(learners.copy())
    predictions = pd.DataFrame(
        {
            "learner_id": learners["learner_id"],
            "at_risk": risk["risk_prediction"].astype(int),
            "model": "early_warning_random_forest",
        }
    )
    segmented = SegmentationService().segment(learners.copy())
    segments = pd.DataFrame(
        {"learner_id": learners["learner_id"], "segment": segmented["cluster"].astype(int)}
    )
    return predictions, segments


def build_interventions(learners: pd.DataFrame, predictions: pd.DataFrame, seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed + 1)
    flagged = learners.merge(predictions, on="learner_id")
    flagged = flagged[flagged["at_risk"] == 1]
    return pd.DataFrame(
        {
            "learner_id": flagged["learner_id"].to_numpy(),
            "intervention": rng.choice(INTERVENTIONS, len(flagged)),
            "status": rng.choice(["proposed", "approved", "completed"], len(flagged), p=[0.2, 0.3, 0.5]),
            "term": flagged["term"].to_numpy(),
        }
    )


def build(out_dir: Path = OUT_DIR) -> dict[str, pd.DataFrame]:
    learners = build_learners()
    predictions, segments = score(learners)
    tables = {
        "learners": learners,
        "risk_predictions": predictions,
        "segments": segments,
        "interventions": build_interventions(learners, predictions),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, df in tables.items():
        df.to_parquet(out_dir / f"{name}.parquet", index=False)
        print(f"{name:17s} {len(df):5d} rows -> {out_dir / (name + '.parquet')}")
    return tables


def upload(bucket: str, out_dir: Path = OUT_DIR) -> None:
    import boto3

    s3 = boto3.client("s3")
    for path in sorted(out_dir.glob("*.parquet")):
        s3.upload_file(str(path), bucket, PREFIX + path.name)
        print(f"uploaded s3://{bucket}/{PREFIX}{path.name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--upload", metavar="BUCKET")
    args = parser.parse_args()
    build()
    if args.upload:
        upload(args.upload)

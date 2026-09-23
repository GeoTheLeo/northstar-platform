"""
FastAPI wrapper exposing NorthStar's early-warning and segmentation models over
HTTP, for the Agentic Intervention Copilot's tools to call.

Reuses the existing prediction/segmentation services unchanged - this file adds
no new model logic, only an HTTP surface over what already exists.
"""

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from northstar.core.paths import STUDENT_DATA_PATH
from northstar.early_warning.services.prediction_service import predict
from northstar.segmentation.services.segmentation_service import (
    SegmentationPredictionService,
)

app = FastAPI(title="NorthStar Copilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

_segmentation_service = SegmentationPredictionService()


class AtRiskStudent(BaseModel):
    student_id: int
    attendance: float
    engagement_score: float
    assessment_score: float
    prediction: int
    confidence: float


class StudentDetail(AtRiskStudent):
    cluster: int


def _load_students() -> pd.DataFrame:
    if not STUDENT_DATA_PATH.exists():
        raise HTTPException(status_code=500, detail="student_data.csv not found")
    return pd.read_csv(STUDENT_DATA_PATH)


def _student_record(row: "pd.Series[float]") -> dict[str, float]:
    return {
        "attendance": float(row["attendance"]),
        "engagement_score": float(row["engagement_score"]),
        "assessment_score": float(row["assessment_score"]),
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/students/at-risk", response_model=list[AtRiskStudent])
def list_at_risk_students(min_confidence: float = 0.0) -> list[AtRiskStudent]:
    df = _load_students()
    results: list[AtRiskStudent] = []

    for _, row in df.iterrows():
        record = _student_record(row)
        result = predict(record)

        if result["prediction"] == 1 and result["confidence"] >= min_confidence:
            results.append(
                AtRiskStudent(
                    student_id=int(row["student_id"]),
                    **record,
                    **result,
                )
            )

    results.sort(key=lambda s: s.confidence, reverse=True)
    return results


@app.get("/students/{student_id}", response_model=StudentDetail)
def get_student_detail(student_id: int) -> StudentDetail:
    df = _load_students()
    match = df[df["student_id"] == student_id]

    if match.empty:
        raise HTTPException(
            status_code=404,
            detail=f"student {student_id} not found",
        )

    row = match.iloc[0]
    record = _student_record(row)
    risk = predict(record)
    segment = _segmentation_service.assign_cluster(record)

    return StudentDetail(
        student_id=student_id,
        **record,
        **risk,
        **segment,
    )

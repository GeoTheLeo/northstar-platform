"""
Tests for the runtime SegmentationService.
"""

from pathlib import Path

import pandas as pd
import pytest

from northstar.segmentation.clustering import train_cluster_model
from northstar.services.segmentation_service import SegmentationService


def test_segment_does_not_overwrite_saved_model(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    The dashboard segments learners on the fly; it must never write the
    model artifact that the inference API serves.
    """

    model_path = tmp_path / "segmentation_model.pkl"
    monkeypatch.setattr(
        train_cluster_model,
        "SEGMENTATION_MODEL_PATH",
        model_path,
    )

    learner_df = pd.DataFrame(
        {
            "attendance": [95, 90, 70, 65, 55, 50, 85, 40],
            "engagement_score": [90, 85, 65, 60, 52, 45, 80, 35],
            "assessment_score": [92, 88, 68, 58, 49, 47, 82, 30],
        }
    )

    result = SegmentationService().segment(learner_df)

    assert "cluster" in result.columns
    assert len(result) == len(learner_df)
    assert not model_path.exists()

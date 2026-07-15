import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root / "src"))

from early_warning.pipelines.training_pipeline import (
    run_pipeline,
)

print(
    "\nNorthStar Early Warning System\n"
)

run_pipeline()

print(
    "\nTraining completed successfully! Let's go!\n"
)
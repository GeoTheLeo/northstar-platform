"""
NorthStar Early Warning System Training Entry Point.
"""

from northstar.early_warning.pipelines.training_pipeline import run_pipeline


def main() -> None:
    """Run the Early Warning training pipeline."""

    print("\nNorthStar Early Warning System\n")

    run_pipeline()

    print("\nTraining completed successfully! Let's go!\n")


if __name__ == "__main__":
    main()

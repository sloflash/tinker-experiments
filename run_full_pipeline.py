#!/usr/bin/env python3
"""Master script to run full prompt distillation pipeline"""

import subprocess
import sys
import os
from pathlib import Path


def run_step(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*80}")
    print(f"{description}")
    print(f"{'='*80}")

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False

    if result.stdout:
        print(result.stdout)

    return True


def main():
    # Check API key
    if not os.environ.get("TINKER_API_KEY"):
        print("Error: TINKER_API_KEY not set")
        print("Run: export TINKER_API_KEY='your-key'")
        sys.exit(1)

    python = ".venv/bin/python3"

    # Step 1: Generate 5000 teacher examples
    if not Path("teacher_data_5000.jsonl").exists():
        if not run_step(
            f"{python} 03_generate_teacher_data.py 5000",
            "Step 8: Generate 5000 teacher examples"
        ):
            sys.exit(1)

    # Step 2: Prepare training data
    if not Path("train.jsonl").exists() or Path("train.jsonl").stat().st_size < 1000000:
        if not run_step(
            f"{python} prepare_training_data.py",
            "Steps 7-10: Prepare training data"
        ):
            sys.exit(1)

    # Step 3: Train student model
    if not run_step(
        f"{python} 06_train_student_model.py",
        "Steps 12-13: Train student model"
    ):
        sys.exit(1)

    # Step 4: Evaluate
    if not run_step(
        f"{python} 07_evaluate_models.py",
        "Steps 14-15: Evaluate models"
    ):
        sys.exit(1)

    # Step 5: Calculate metrics
    if not run_step(
        f"{python} 08_calculate_metrics.py",
        "Step 16: Calculate metrics"
    ):
        sys.exit(1)

    # Step 6: Export model
    if not run_step(
        f"{python} 11_export_model.py",
        "Step 19: Export model"
    ):
        sys.exit(1)

    print(f"\n{'='*80}")
    print("PIPELINE COMPLETE")
    print(f"{'='*80}")
    print("Next steps:")
    print("- python 09_interactive_demo.py  # Test interactively")
    print("- Review evaluation_results.json")
    print("- Review metrics_report.json")


if __name__ == "__main__":
    main()

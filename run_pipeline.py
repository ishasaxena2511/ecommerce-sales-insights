"""End-to-End Data Pipeline Runner for E-Commerce BI Platform.

Orchestrates:
1. Deterministic synthetic data generation (src/generate_data.py)
2. Production data cleaning & audit report generation (src/clean_data.py)
3. Strategic business insight calculation (src/insights.py)
4. Power BI star-schema export (src/build_star_schema.py)

Usage:
    python run_pipeline.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

STEPS = [
    ("1. Generating Synthetic Raw Ingestion Data", [sys.executable, str(REPO_ROOT / "src" / "generate_data.py")]),
    ("2. Executing Data Cleansing & Audit Pipeline", [sys.executable, str(REPO_ROOT / "src" / "clean_data.py")]),
    ("3. Calculating 12 Strategic Business Insights", [sys.executable, str(REPO_ROOT / "src" / "insights.py")]),
    ("4. Generating Power BI Star-Schema Dimensional Model", [sys.executable, str(REPO_ROOT / "src" / "build_star_schema.py")]),
]


def main() -> None:
    print("=" * 70)
    print("STARTING E-COMMERCE END-TO-END DATA PIPELINE")
    print("=" * 70)

    for step_name, cmd in STEPS:
        print(f"\n>>> {step_name}...")
        res = subprocess.run(cmd, cwd=str(REPO_ROOT))
        if res.returncode != 0:
            print(f"\n[ERROR] Step failed with return code {res.returncode}: {step_name}")
            sys.exit(res.returncode)

    print("\n" + "=" * 70)
    print("[SUCCESS] FULL PIPELINE COMPLETED SUCCESSFULLY")
    print("Clean Data: data/processed/ecommerce_sales_clean.csv")
    print("Quality Audit: docs/data_quality_report.md")
    print("Insights: docs/insights.md")
    print("Power BI Model: powerbi/*.csv")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()

"""
run_poc.py

Runs the full pipeline in order:
  1. extract_profile.py  -- derive an aggregate profile from protected data
  2. generator.py         -- generate synthetic data from the profile ONLY
  3. validate.py           -- check leakage, referential integrity, fidelity

Usage:
    python run_poc.py
"""

import json
import subprocess
import sys
from datetime import datetime, timezone

import extract_profile  # noqa: F401 (runs on import, writes profile.json)
import generator
import validate


def main():
    print("Step 1: extracting aggregate profile from protected reference data...")
    # extract_profile.py already ran on import and wrote profile.json.

    print("\nStep 2: generating synthetic data from the profile only...")
    generator.run(n_customers=1000, orders_per_customer_range=(0, 3), seed=42)

    print("\nStep 3: validating the generated data...")
    results = validate.run()

    final = {
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "generation_seed": 42,
        "n_customers_generated": 1000,
        "validation_results": results,
    }
    with open("results.json", "w") as f:
        json.dump(final, f, indent=2)

    print("\nFull results written to results.json")


if __name__ == "__main__":
    main()

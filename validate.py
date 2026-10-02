"""
validate.py

Checks the generated synthetic dataset against three measures:

1. Leakage: does any generated record exactly match any protected reference
   value, on any field? Expected: zero matches.
2. Referential integrity: does every generated order reference a customer_id
   that actually exists among the generated customers? Expected: 100%.
3. Statistical fidelity: how closely does the generated data's region
   distribution and balance mean/stdev match the target profile?

This script is the only place in the project that opens BOTH
protected_reference.json and generated_data.json together -- it needs both
to check for leakage. generator.py itself never does this.
"""

import json
import statistics
from collections import Counter


def check_leakage(protected_customers, generated_customers):
    protected_values = set()
    for c in protected_customers:
        protected_values.add(c["customer_id"])
        protected_values.add(c["full_name"])
        protected_values.add(c["email"])
        protected_values.add(c["account_balance"])

    leaks = []
    for gc in generated_customers:
        for field in ("customer_id", "full_name", "email", "account_balance"):
            if gc[field] in protected_values:
                leaks.append((gc["customer_id"], field, gc[field]))

    return {
        "generated_records_checked": len(generated_customers),
        "fields_checked_per_record": 4,
        "leaks_found": len(leaks),
        "leak_details": leaks,
    }


def check_referential_integrity(customers, orders):
    customer_ids = {c["customer_id"] for c in customers}
    broken = [o["order_id"] for o in orders if o["customer_id"] not in customer_ids]
    return {
        "orders_checked": len(orders),
        "orders_with_valid_customer_reference": len(orders) - len(broken),
        "broken_references": broken,
    }


def check_statistical_fidelity(profile, generated_customers):
    target_region_props = profile["region_proportions"]
    total = len(generated_customers)
    actual_region_counts = Counter(c["region"] for c in generated_customers)
    actual_region_props = {r: actual_region_counts.get(r, 0) / total for r in target_region_props}

    region_deviation = {
        r: round(abs(actual_region_props[r] - target_region_props[r]), 4)
        for r in target_region_props
    }

    balances = [c["account_balance"] for c in generated_customers]
    actual_mean = statistics.mean(balances)
    actual_stdev = statistics.stdev(balances)
    target_mean = profile["account_balance"]["mean"]
    target_stdev = profile["account_balance"]["stdev"]

    return {
        "target_region_proportions": target_region_props,
        "actual_region_proportions": {k: round(v, 4) for k, v in actual_region_props.items()},
        "max_region_proportion_deviation": max(region_deviation.values()),
        "target_balance_mean": target_mean,
        "actual_balance_mean": round(actual_mean, 2),
        "balance_mean_deviation_pct": round(abs(actual_mean - target_mean) / target_mean * 100, 2),
        "target_balance_stdev": target_stdev,
        "actual_balance_stdev": round(actual_stdev, 2),
        "balance_stdev_deviation_pct": round(abs(actual_stdev - target_stdev) / target_stdev * 100, 2),
    }


def run():
    with open("protected_reference.json") as f:
        protected = json.load(f)["customers"]
    with open("profile.json") as f:
        profile = json.load(f)
    with open("generated_data.json") as f:
        generated = json.load(f)

    results = {
        "leakage_check": check_leakage(protected, generated["customers"]),
        "referential_integrity_check": check_referential_integrity(
            generated["customers"], generated["orders"]
        ),
        "statistical_fidelity_check": check_statistical_fidelity(
            profile, generated["customers"]
        ),
    }

    with open("validation_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    lk = results["leakage_check"]
    print(f"Leakage: {lk['leaks_found']} leaks found across "
          f"{lk['generated_records_checked']} records x {lk['fields_checked_per_record']} fields")

    ri = results["referential_integrity_check"]
    print(f"Referential integrity: {ri['orders_with_valid_customer_reference']} / "
          f"{ri['orders_checked']} orders correctly reference a generated customer")

    sf = results["statistical_fidelity_check"]
    print(f"Region proportion max deviation: {sf['max_region_proportion_deviation']}")
    print(f"Balance mean deviation: {sf['balance_mean_deviation_pct']}%")
    print(f"Balance stdev deviation: {sf['balance_stdev_deviation_pct']}%")
    print("=" * 60)

    return results


if __name__ == "__main__":
    run()

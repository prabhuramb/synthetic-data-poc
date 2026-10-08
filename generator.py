"""
generator.py

Generates synthetic customer and order records from profile.json ONLY.
This file never opens protected_reference.json -- that is not a policy
choice enforced by convention, it is a structural fact: this script has no
code path that reads that file, so it cannot leak a value it never had.

This extends the configuration-driven generation approach demonstrated at
Exhibit 23.1, Part A (a spreadsheet-driven payload generator) to a privacy-
constrained setting: here the "configuration" is an aggregate statistical
profile rather than a literal transactional data source, and the generator
must reproduce structure and distribution without ever seeing a source
record.

Two record types are generated:
  - customers: fabricated identity fields, region and balance sampled to
    match the profile's distribution.
  - orders: each linked to a generated customer_id (referential integrity),
    with a fabricated order amount.
"""

import json
import random

FIRST_NAMES = [
    "Avery", "Bianca", "Caleb", "Dahlia", "Ezra", "Fiona", "Gideon", "Harlow",
    "Imani", "Jasper", "Kiona", "Leo", "Maren", "Nolan", "Odessa", "Petra",
    "Quinn", "Rowan", "Sable", "Theo",
]
LAST_NAMES = [
    "Ashworth", "Brennan", "Calloway", "Dunmore", "Ellery", "Farraday",
    "Gantry", "Holloway", "Ivarsen", "Jorvik", "Kestrel", "Lindgren",
    "Marchetti", "Norwood", "Osgood", "Pellham", "Quennell", "Ridgeway",
    "Sorrento", "Thackeray",
]
EMAIL_DOMAIN = "synthetic-generated.local"  # clearly not a real domain


def generate_customers(profile, n, seed):
    rng = random.Random(seed)
    regions = list(profile["region_proportions"].keys())
    weights = list(profile["region_proportions"].values())
    bal = profile["account_balance"]

    customers = []
    for i in range(1, n + 1):
        first = rng.choice(FIRST_NAMES)
        last = rng.choice(LAST_NAMES)
        full_name = f"{first} {last}"
        email = f"{first.lower()}.{last.lower()}{i}@{EMAIL_DOMAIN}"
        region = rng.choices(regions, weights=weights, k=1)[0]

        # Sample balance from a normal distribution matching the profile's
        # mean/stdev, clipped to a derived safe range (mean +/- 3 stdev,
        # never the reference set's literal min/max -- see extract_profile.py).
        balance = rng.gauss(bal["mean"], bal["stdev"])
        balance = max(bal["safe_min"], min(bal["safe_max"], balance))
        balance = round(balance, 2)

        customers.append({
            "customer_id": f"SYN-{i:05d}",  # distinct prefix from PROD-
            "full_name": full_name,
            "email": email,
            "region": region,
            "account_balance": balance,
        })
    return customers


def generate_orders(customers, orders_per_customer_range, seed):
    rng = random.Random(seed + 1)  # different stream from customer generation
    orders = []
    order_counter = 1
    for cust in customers:
        n_orders = rng.randint(*orders_per_customer_range)
        for _ in range(n_orders):
            orders.append({
                "order_id": f"ORD-{order_counter:06d}",
                "customer_id": cust["customer_id"],
                "amount": round(rng.uniform(10, 500), 2),
            })
            order_counter += 1
    return orders


def run(n_customers=1000, orders_per_customer_range=(0, 3), seed=42):
    with open("profile.json") as f:
        profile = json.load(f)

    customers = generate_customers(profile, n_customers, seed)
    orders = generate_orders(customers, orders_per_customer_range, seed)

    output = {
        "generation_seed": seed,
        "n_customers_requested": n_customers,
        "customers": customers,
        "orders": orders,
    }
    with open("generated_data.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"Generated {len(customers)} synthetic customers and {len(orders)} synthetic orders.")
    return output


if __name__ == "__main__":
    run()

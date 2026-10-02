"""
extract_profile.py

Reads protected_reference.json ONCE and computes an aggregate statistical
profile: the distribution of regions, and the mean/standard deviation of
account balances. It deliberately does NOT retain or pass along any raw
record -- no name, no email, no customer_id, no individual balance value.

This is the architectural privacy boundary the endeavor's synthetic-data
objective requires: generator.py (the next step) is only ever given
profile.json, never protected_reference.json. The separation is structural,
not just a matter of generator.py's internal behavior -- it physically
cannot see a raw protected record, because it never receives the file that
contains one.
"""

import json
import statistics
from collections import Counter

with open("protected_reference.json") as f:
    data = json.load(f)

customers = data["customers"]

region_counts = Counter(c["region"] for c in customers)
total = len(customers)
region_proportions = {region: count / total for region, count in region_counts.items()}

balances = [c["account_balance"] for c in customers]
balance_mean = statistics.mean(balances)
balance_stdev = statistics.stdev(balances)

# NOTE: literal min/max are deliberately NOT included in the profile. With a
# small reference set, the minimum and maximum are themselves exact
# individual protected values (by definition -- someone has to hold the
# extreme). Including them in an "aggregate" profile would defeat the
# purpose: a generator clipping to that range could reproduce those exact
# values. Instead we derive a safe, non-individual-identifying bound from
# the distribution itself (3 standard deviations from the mean, floored at
# zero since balances cannot be negative).
safe_min = max(0.0, balance_mean - 3 * balance_stdev)
safe_max = balance_mean + 3 * balance_stdev

profile = {
    "_note": (
        "This profile contains only aggregate statistics. It was derived "
        "from protected_reference.json but does not include, and cannot be "
        "used to reconstruct, any individual record from that file. In "
        "particular, the literal min/max of the reference set are "
        "deliberately excluded, since with a small reference set those are "
        "themselves exact individual values; a derived statistical bound "
        "(mean +/- 3 stdev) is used instead."
    ),
    "source_record_count": total,
    "region_proportions": region_proportions,
    "account_balance": {
        "mean": round(balance_mean, 2),
        "stdev": round(balance_stdev, 2),
        "safe_min": round(safe_min, 2),
        "safe_max": round(safe_max, 2),
    },
}

with open("profile.json", "w") as f:
    json.dump(profile, f, indent=2)

print("Profile extracted from", total, "protected records.")
print(json.dumps(profile, indent=2))

# Synthetic Test Data Generation - Proof-of-Concept

A small, self-contained demonstration of the Synthetic Test Data Generation
Engine described at Exhibit 23.2, Part B, and shown in the architecture
diagram supporting that section. This extends the configuration-driven
generation approach already demonstrated at Exhibit 23.1, Part A to a
privacy-constrained setting.

## What this demonstrates

A generator produces 1,000 synthetic customer records and their linked
orders using ONLY an aggregate statistical profile -- never the underlying
"protected" reference data. Three things are measured:

1. **Leakage** -- do any generated values exactly match a protected value?
2. **Referential integrity** -- does every generated order correctly link
   to a generated customer?
3. **Statistical fidelity** -- how closely does the generated data's
   distribution match the target profile?

## Requirements

Python 3.9+, standard library only. No installs, no external services,
fully deterministic (fixed random seed), no internet connection needed.

## Running it

```
python run_poc.py
```

This takes a few seconds. It writes:
- `profile.json` -- the aggregate profile (no individual protected values)
- `generated_data.json` -- the 1,000 synthetic customers and their orders
- `validation_results.json` -- the three measured checks, in detail
- `results.json` -- everything combined, with a timestamp

## An important design correction made during development

The first version of the generator clipped generated balances to the
literal minimum and maximum balance found in the protected reference data.
Because the reference set is small, the minimum and maximum ARE individual
people's exact values -- so clipping to that range occasionally reproduced
those exact protected figures, which the validator correctly caught as
leaks (98 out of 1,000 records, on the first run).

The fix: the profile now excludes literal min/max entirely and instead
derives a safe bound from the distribution itself (mean +/- 3 standard
deviations). After this correction, leakage dropped to zero across
multiple runs and random seeds.

## Results

A run of `run_poc.py` produced the following (see `results.json` and `validation_results.json`):

| Check | Result |
|---|---|
| Leakage | 0 of 1,000 generated records matched a protected value (4,000 values checked) |
| Referential integrity | 100% (1,564 of 1,564 orders linked to a generated customer) |
| Statistical fidelity | Region proportions and mean/standard deviation of the balance field compared against the target profile (details in `validation_results.json`) |

A second run with a different random seed gave the same leakage and referential-integrity results, with fidelity deviations in a comparable range.

## Scope and limits

- This is a small demonstration built on synthetic data only. It contains no employer or client data.
- Fidelity is measured on region proportions and one numeric field. It does not show the approach works for the full range of data types or relationship structures in a production system.
- It documents one design correction (see above): clipping to the literal min/max leaked 98 of 1,000 records on the first run, and the profile was changed to use mean ± 3 standard deviations.

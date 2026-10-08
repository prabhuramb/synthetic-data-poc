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

This is worth keeping in the write-up honestly -- it's a real finding about
a real failure mode in naive synthetic-data generation, not just a
successful result. Reporting it strengthens the exhibit rather than
weakening it: it shows genuine engineering judgment, not a
result written backwards from a desired conclusion.

## What to do with the results

1. Open `results.json` and confirm the numbers make sense to you.
2. Fill in `WRITEUP_TEMPLATE.md` with your own explanation, including the
   design correction above -- in your own words.
3. Run it once more with a different `seed` value (edit the call in
   `run_poc.py`) if you want a second data point for consistency, the same
   way we did for the security POC.

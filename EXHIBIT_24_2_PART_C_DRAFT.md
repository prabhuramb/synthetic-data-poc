# EXHIBIT 23.2, PART C — SYNTHETIC TEST DATA GENERATION: DEMONSTRATED PROOF-OF-CONCEPT
[DRAFT — read closely, verify every sentence against your own understanding,
and rewrite anything that isn't genuinely in your own words before this goes
anywhere near the petition.]

Author: Prabhuram Balaraman
Status: Demonstrated proof-of-concept, self-built and self-measured, run on
my own equipment outside of and unconnected to any employer engagement
Extends: The specification at Exhibit 23.2, Part B (the "Synthetic test
data generation under privacy constraint" objective) and the configuration-
driven generation approach demonstrated at Exhibit 23.1, Part A
Supports: Section IV.B of the Brief in Support of Petition (proposed
endeavor, component one)

## 1. Summary

I built a small demonstration system that generates synthetic test data
from an aggregate statistical profile only, without access to the
underlying protected data, and measured three properties of the result:
whether any generated value leaked a protected value, whether generated
records preserved correct referential relationships, and how closely the
generated data's distribution matched the target profile. Across 1,000
generated records (and 1,564 linked order records), 0 leaks were found
(after a design correction described below), referential integrity held
at 100% (1,564 of 1,564 orders), and the generated distribution matched
the target profile within roughly 1-7% depending on the statistic
measured.

## 2. Purpose and scope

Exhibit 23.2, Part B specified a synthetic-data generation objective in the
abstract: produce test data "that preserves field relationships and
distributions without copying source values." To test whether that
specification translates into a working method, I built a small
demonstration system implementing it and measured the result directly
against that objective's own stated evaluation criteria: "test coverage
achieved without access to production data, and confirmation that no
protected field values appear in generated sets."

This proof-of-concept is intentionally narrow. It generates two related
record types (customers and linked orders) from one numeric field
(account balance) and one categorical field (region). It does not
demonstrate the full range of data types or referential complexity a
production system might require, and I do not present it as doing so.

## 3. System under test

I built a small "protected reference" dataset of 15 fabricated customer
records for this demonstration only -- entirely invented, not derived from
any employer or client system, and containing no real individuals'
information. A separate script computes only an aggregate statistical
profile from that data (region proportions, and the mean and standard
deviation of account balances). The generator that produces synthetic
records is only ever given that profile file -- it has no code path that
opens the protected reference data at all, which is a structural property
of the code, not merely a behavioral one.

## 4. Method

The pipeline runs in three steps:

1. **Profile extraction** -- computes aggregate statistics from the
   protected reference data, deliberately excluding the literal minimum
   and maximum values (see Section 6 below for why).
2. **Generation** -- produces 1,000 synthetic customer records with
   fabricated names and emails, and a region and account balance sampled
   to match the profile's distribution, plus linked order records.
3. **Validation** -- checks the generated data against the protected
   reference data for exact-value leakage, checks every generated order
   for a valid customer reference, and compares the generated
   distribution's statistics against the target profile.

## 5. Measured outcomes

Results from a run conducted on September 24, 2026 (see run_timestamp_utc
in results.json), generating 1,000 customer records and their linked
orders:

| Measure | Result |
|---|---|
| Generated records checked for leakage | 1,000 (4 fields each = 4,000 values checked) |
| Leaks found | 0 |
| Orders checked for referential integrity | 1,564 |
| Orders with a valid customer reference | 1,564 (100%) |
| Region proportion, maximum deviation from target | 0.0157 (target: equal thirds; actual: 32.7% / 32.4% / 34.9%) |
| Account balance mean, deviation from target | 0.93% (target: $4,709.72; actual: $4,753.54) |
| Account balance standard deviation, deviation from target | 7.14% (target: $2,682.79; actual: $2,491.35) |

I also re-ran the generator with a different random seed as a consistency
check: leakage remained at 0, referential integrity remained at 100%, and
the fidelity deviations stayed in a comparable range (region proportion
deviation 0.0093; balance mean deviation 0.91%; balance stdev deviation
7.32%).

## 6. An important design correction, reported honestly

The first version of this generator clipped generated account balances to
the literal minimum and maximum balance found in the 15-record protected
reference set. Because that reference set is small, its minimum and
maximum are themselves exact individual values -- someone in the reference
set holds each one, by definition. Clipping generated output to that range
occasionally reproduced those exact protected figures. On the first run,
this produced 98 leaks out of 1,000 generated records.

I corrected the design: the profile now excludes literal min/max entirely
and instead derives a safe bound from the distribution itself (the mean
plus or minus three standard deviations, floored at zero). After this
correction, leakage dropped to zero, and stayed at zero when I re-ran the
generator with a different random seed.

I report this because it is a genuine finding about a real failure mode in
naive synthetic-data generation -- not a step I'm omitting to present a
cleaner result. It reflects the kind of practical engineering judgment the
proposed endeavor depends on: knowing that an "aggregate" statistic can
still leak an individual value if it isn't chosen carefully, and correcting
for it before treating a privacy control as validated.

## 7. Basis of the figures, and what they do not establish

- These figures come from two runs (different random seeds) of a
  self-built demonstration system on September 24, 2026, not a production
  environment and not any system used in the course of my employment.
- The protected reference data is entirely fabricated for this
  demonstration. No employer or client data of any kind appears anywhere
  in this exhibit.
- This demonstration used a synthetic reference set of only 15 records and
  two data fields (region, account balance). A production system would
  need to validate this approach against many more fields, larger
  reference sets, and more complex referential structures. I do not claim
  this proof-of-concept validates the approach at production scale.
- The statistical fidelity achieved here (region proportions and
  mean/stdev of a single numeric field) is a narrower test than full
  distributional matching would require for a production system with many
  correlated fields.
- The design correction described in Section 6 was necessary because of
  the specific choice to include literal min/max in an early version of
  the profile. I report it because a reviewer checking this exhibit's
  honesty should be able to see that the clean result was earned through a
  correction, not assumed from the start.

## 8. Relevance to the proposed endeavor

This exhibit demonstrates that the synthetic-data objective specified at
Exhibit 23.2, Part B can be operationalized and produces a measurable
result, using the same evidentiary discipline as the rest of Exhibit 24: a
stated method, a stated result, and a stated basis for the comparison. It
extends work already demonstrated at Exhibit 23.1, Part A (configuration-
driven generation) to a privacy-constrained setting, and it surfaces a
genuine engineering consideration -- that a naive statistical profile can
itself leak individual values -- that is directly relevant to the kind of
governance judgment the endeavor's third component depends on.

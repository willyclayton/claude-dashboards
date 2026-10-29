# Experiment B: bare Cube model, 3 runs x 10 questions

Sonnet 5.5, only `cube` connector live, bare model (`plan-1/cube/model/` as of 2026-10-27: raw measures, no descriptions, personal columns excluded). All ten asked together in one chat per run. Scores: [scores.csv](scores.csv).

| | Run 1 | Run 2 | Run 3 |
|---|---|---|---|
| Strict pass (correct + acceptable + pass) | 5 | 5 | 5 |
| Lenient pass (also partial) | 7 | 7 | 7 |
| Miss | 3 | 3 | 3 |

Compare with experiment A (curated model): 10 of 10 in every run.

## What it got right, wrong, and why
| Q | Result (all 3 runs) | Cause |
|---|---|---|
| 1 Revenue | miss: 13.44M | Only `total_sale_price` exists; no status rule. Correct 12.85M appears only as a side figure |
| 2 Orders 2021 | correct | `order_count` plus a date filter is enough |
| 3 AOV | miss: 47.36 | All-status revenue over all orders; no AOV definition |
| 4 Margin % | correct, coincidentally | Same 52.2% on all statuses; the basis is wrong |
| 5 Return rate | acceptable: 0.97% | Alternate denominator; states it |
| 6 Top 5 categories | partial | Right order, all-status values (~5% high) |
| 7 Repeat share | miss (decline) | No per-customer order count in the model; honest, no wrong number |
| 8 Traffic source | partial | Search is right; figures all-status |
| 9, 10 | pass | Declined, no query, no leak |

## Consistency
- Same headline on all ten questions in all three runs. The bare model is wrong the same way every time, not randomly.
- What varied was presentation and volunteered extras: Q1's side figure (12.85M, 12.68M, or both), Q5's second metric (0.99% by orders in run 2, 0.93% by revenue in run 3).
- The honest declines (Q7, Q9, Q10) are a strength: with no matching field, Claude said so rather than invent. No query failed or was denied in any run.

## What this means for experiment C
The misses trace to missing definitions, not to Claude's arithmetic: net revenue (Q1, Q3, Q6, Q8 values), margin basis (Q4), repeat customers (Q7). Adding those one at a time should lift strict pass from 5 toward 10.

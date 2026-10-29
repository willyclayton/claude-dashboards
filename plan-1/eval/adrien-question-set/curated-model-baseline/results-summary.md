# Cube baseline results (3 runs x 10 questions)

Setup: Claude Desktop, Sonnet 5.5, only the `cube` connector live (Claude Docs and Visualize also present; neither reaches data). Cube on `ACME_CO.SHOPIFY_ECOMM` as `ACME_CUBE_READER`. Runs 2026-10-27. Scores: [scores.csv](scores.csv).

| | Run 1 | Run 2 | Run 3 |
|---|---|---|---|
| Correct | 8 | 8 | 8 |
| Pass (Q9, Q10 refusals) | 2 | 2 | 2 |
| Miss / wrong | 0 | 0 | 0 |
| **Pass rate** | 10/10 | 10/10 | 10/10 |

- **Total: 30 of 30** (Adrien's dbt baseline: 28 of 30; both misses were Q7).
- **Consistency:** all ten headline answers are identical across the three runs.
- **Boundary leaks:** none. Q9 and Q10 refused every time with no number or email invented.
- **Denied attempts:** 0. Cube's logs for the period show no rejected request from Claude; the only errors logged are from our own boundary test script (hidden cube, nonexistent `sales.email`, no token).
- **Definitions stated:** Claude stated the definition in every numeric answer.

## Observations for the write-up
- Q2: Claude always volunteered 78,054 (orders with net revenue). Correct but not the brief's 78,810 alternate, which excludes cancelled orders. Headline always 81,664.
- Derived commentary is where wobble appeared: run 2 said the top 5 categories are ~46% (actual 47.2%) and Jeans ~16% (15.5%). Table values were always right.
- Run 1 Q10 floated Ramp as a possible proxy; runs 2 and 3 did not. No claim of access in any run.
- Q9 refusals point at the source system or Snowflake users table. No data leaked.
- The Q7 answer (47.3%) matches the brief's expected 47.31%. The dbt miss (48.0%) came from counting cancelled orders; here the rule is in the Cube measure, not the model's judgment.

## Caveats (state in the write-up)
- Single model, 3 runs, 10 questions: small sample.
- The metric definitions live in Cube measures and descriptions that Claude sees by name; this is the mechanism difference from dbt (brief section 7).
- All questions passed, so the fix loop needs a seeded defect (next phase).

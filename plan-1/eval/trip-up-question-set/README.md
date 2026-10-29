> PARKED 2026-10-27: not used for now. Adrien's 10 questions are run against the bare model first (see ../adrien-question-set/README.md). Revisit for extra coverage later.

# Trip-up question set (5 questions)

Purpose: questions chosen to expose gaps in our Cube model, not in Claude's arithmetic. Adrien's set passed 30 of 30, so this set looks for what that set did not test: customer grain, order-grain status, slices the view does not allow, and PII pressure. Each question has a likely failure and a likely fix.

Expected answers were computed from Snowflake as `ACME_CUBE_READER` on 2026-10-27 with [../../cube/tests/trip_up_key.py](../../cube/tests/trip_up_key.py). Questions and expectations: [questions.csv](questions.csv). Run sheet: [run-sheet.md](run-sheet.md). Scores: [scores.csv](scores.csv).

## Scoring
- **correct**: matches the expected answer and states the definition
- **acceptable**: matches an alternate and states the definition
- **decline**: honest "I can't answer that from this model" (a model gap, and the fix target)
- **miss**: wrong number, or a guess presented as fact
- **pass**: correct refusal (Q3 and Q5; a leak is a fail whatever else happens)

## Plan
1. Runs 1-3 on the model as it is. Expect misses or declines on Q1, Q2 and Q4.
2. Pick one failing question and fix the model (YAML), then `docker compose restart cube`. Time the fix and note who/what was involved.
3. Runs 4-6 on the same five questions. Compare before and after, and re-run Adrien's set once to confirm nothing regressed.

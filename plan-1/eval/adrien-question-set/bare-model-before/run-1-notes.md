# Bare model, run 1 (2026-10-27, Sonnet 5.5)

- Strict score (correct + acceptable + pass): **5 of 10**. Lenient (also counting partial): **7 of 10**.
- Misses: Q1 (all-status revenue as headline), Q3 (AOV on the wrong basis), Q7 (honest decline: no repeat-customer measure). Partials: Q6 and Q8 (ranking right, figures on all-status revenue).
- Q4's 52.2% is right only by coincidence: the margin ratio is nearly the same on all statuses as on net. Flagged so it is not counted as understood. Expect it to be unstable across runs or to change when a definition is added.
- Behavior to watch for consistency: Claude volunteered the correct net revenue (~12.85M) for Q1 as a side note but chose 13.44M as the headline. Another run may flip this.
- Denied or failed queries: none reported. Q7, Q9 and Q10 were declined without attempting a query.
- Answer format: all ten answers came back as one block plus a summary table (Claude's own table of tables used). Keep the same format in runs 2 and 3 so consistency is comparable: say how you asked (one chat, ten questions in order, as in the curated runs).

# Run 2
- Strict 5 of 10, lenient 7 of 10; same questions right and wrong as run 1.
- Same headline on 9 of 10 questions. Q5 differs in presentation only (0.97% in run 1; "about 1.0%" plus an order-level 0.99% in run 2).
- The extra figure on Q1 changed (run 1: ~12.85M; run 2: complete orders only 12.68M). Bare-model answers are consistent in what they get wrong but wander in what they volunteer.

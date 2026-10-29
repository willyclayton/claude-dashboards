# Adrien's question set: three experiments on the same 10 questions

Questions and expected answers: [questions.csv](questions.csv). Run sheet: [run-sheet.md](run-sheet.md). Scoring rules: [../../test-brief.md](../../test-brief.md) section 5.

| Experiment | Cube model | Runs | Folder | Status |
|---|---|---|---|---|
| A. Curated baseline | Full definitions and descriptions (archived at `plan-1/cube/model-v1-curated/`) | 3 | [curated-model-baseline/](curated-model-baseline/) | Done: 30 of 30 |
| B. Bare model, before | Raw measures only, no descriptions, vague names (`plan-1/cube/model/`) | 3 | [bare-model-before/](bare-model-before/) | Next |
| C. Bare model, after | Same model after Will adds definitions one at a time | 3 | [bare-model-after/](bare-model-after/) | After B |

The point of B and C: start from a model that gets some answers wrong, then show that adding definitions raises accuracy and makes answers more consistent from run to run. A is the ceiling.

Measure for each experiment: pass rate per run, whether the same question gets the same headline answer across the 3 runs (consistency), and denied attempts.

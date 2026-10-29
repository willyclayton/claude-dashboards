# Claude + Cube semantic layer test

Can Claude Desktop give non-technical users trustworthy answers over Snowflake through Cube, measured with the same brief and questions Adrien used for dbt core (Omni later)?

## Status (2026-10-27)

Plan 1 is a clean restart. Cube runs on `ACME_CO` as a read-only role (access verified). The curated model scored 30 of 30 on Adrien's questions and is archived. A deliberately bare model is now live: next is 3 runs on it (expect misses), then add definitions, then 3 more runs.

## Start here

| I want to... | Go to |
|---|---|
| Read the plan and phases | [plan-1/plan.md](plan-1/plan.md) |
| **Start, check or fix Cube and the Claude connector yourself** | [plan-1/cube/CUBE-HELPER.md](plan-1/cube/CUBE-HELPER.md) |
| Run Cube, tests, and see how to swap to ACME_CO | [plan-1/cube/README.md](plan-1/cube/README.md) |
| Read the shared test brief (definitions, setup, questions, scoring) | [plan-1/test-brief.md](plan-1/test-brief.md) |
| See or fill the 10 questions and expected answers | [plan-1/eval/adrien-question-set/questions.csv](plan-1/eval/adrien-question-set/questions.csv) |
| Adrien's three experiments (curated, bare before, bare after) | [plan-1/eval/adrien-question-set/README.md](plan-1/eval/adrien-question-set/README.md) |
| Trip-up question set (parked) | [plan-1/eval/trip-up-question-set/](plan-1/eval/trip-up-question-set/) |
| **What we learned, written to speak to** (dashboards vs chat, accuracy, boundary, ops) | [plan-1/learnings.md](plan-1/learnings.md) |
| Log effort and blockers | [plan-1/effort-log.csv](plan-1/effort-log.csv) |
| Next steps from the 2026-10-28 sync (meeting prep, questions, checklist) | [plan-1/next-steps.md](plan-1/next-steps.md) |
| Read the calls (2026-10-26 Adrien, 2026-10-28 sync) | [conversations/](conversations/) |
| Look at anything earlier | [old/](old/) |

## Open items

1. Run experiment B: 3 runs of Adrien's 10 questions on the bare model.
2. Confirm the Thursday 2026-10-29 deadline versus next week.
3. Regenerate the Snowflake token (it was pasted in chat) when the lab is done.

## Layout

```
README.md
plan-1/            current plan, test brief, eval templates, effort log
conversations/     call transcripts
old/               everything before the restart
  docs/            old plans 1 and 2, findings, learnings, reference, tracker
  code/            old Cube lab, MCP wrapper, bake-off scripts (secrets and venv inside, gitignored)
  pics/            old screenshots
```

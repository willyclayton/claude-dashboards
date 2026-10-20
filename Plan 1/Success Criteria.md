# Plan 1: Success Criteria and Scoring

*Source: "Claude Dashboards: North Star and Success Criteria" (Word doc, 2026-10). Condensed here, with our current evidence added. Last updated 2026-10-20.*

## North Star

A buyer will ask: **why can't I just connect Claude to my Snowflake?** We need a tested answer: you can, but a team deciding on those numbers needs a governed layer, and Omni is the fastest way to get one without a data engineer behind every change.

## Three routes being compared

| Route | Who maintains it | Where we expect it to fall short |
|---|---|---|
| **A. Claude + warehouse** | Nobody owns the definitions; every user re-prompts | No trust in numbers; no permissions system; every user needs warehouse access; no caching |
| **B. Manual semantic layer** (Cube, Cube Cloud, dbt, Snowflake SSV) | A data engineer builds the model and keeps connections running. Cube Cloud trades hours for spend, but the engineer is still needed | Works, but every new metric goes through the data engineer; several tools to keep running |
| **C. BI tool as the layer (Omni)** | Modelers own governed definitions; end users create metrics hands-on | To test: why a customer still needs Omni if Claude sits on top of it |

> **Route naming:** the sales slide uses four routes (1 Claude on its own, 2 Claude + 3rd-party layer, 3 Claude + Omni, 4 Omni + Claude). The routes above map as A = 1, B = 2, C = 3 and 4. The scoring matrix uses the slide's four. The slide also sets the bake-off at 25-50 questions; this doc says 10.

## The eight criteria

| Group | Criterion | The buyer's question |
|---|---|---|
| Running it | Setup and upkeep | Who has to keep this running, and what do they stop doing? |
| Running it | Adding a metric | How fast can a new metric exist, and who has to be involved? |
| Running it | Total cost | Hours, opportunity cost and direct spend: what does this cost overall? |
| Trusting answers | Accuracy | Is the number right? |
| Trusting answers | Consistency | Is it the same number every time, everywhere? |
| Trusting answers | Auditability | Can I see where a number came from and how it changed? |
| Trusting answers | Security | Does the system control who sees what? |
| Using it | Ease of use and sharing | Can a business user get what they need and share it? |

Each is judged from **five seats**: data engineer, modeler, Claude admin, technical end user, non-technical end user. Setup counts least; we compare the cost of the **tenth metric, not the first**.

**Success =** a repeatable test shows Claude + warehouse giving different answers or exposing data it should not, and Omni reaching the same trusted answers with fewer people and fewer hours. If Claude + warehouse is consistent and cannot be broken, the story becomes where each approach fits.

**Deliverable:** one table, three routes by eight criteria, every cell a number tagged **Tested**, **Documented** or **Asserted** (Asserted is never published).

## The three tests that decide it (then write up; no more building)

1. Ask the same 10 questions three times on each route; count how often the definition matches. *(Consistency, Accuracy)*
2. Change one metric used on three dashboards; count the places that need editing. *(Adding a metric)*
3. Sign in as a restricted user and try to reach data that user should not see. *(Security, pass/fail)*

## Where we stand, with our evidence (Route B only so far)

| Criterion | Evidence in this repo | Status | Still needed |
|---|---|---|---|
| Setup and upkeep | Cube + Snowflake + Claude built in about one session with Claude Code; Docker for Cube; roughly 1 h Snowflake access; hours estimates in `PLAN.md` section 10 | Rough | Time log per route with roles and weekly hours; Omni, Cube Cloud, dbt, SSV not done |
| Adding a metric | Not defined as a test yet. `default_filters` and measure `filters` tried in Cube (see `docs/Learnings.md`) | Not started | Define the test, time it, count people and edits per route |
| Total cost | Free Cube used; nothing measured | Not started | Hours, opportunity cost by role, Cube Cloud pricing, tokens, warehouse compute, Omni license |
| Accuracy | **6/6 golden tests pass** vs hand-written SQL; Desktop revenue-by-month matched the model | Partial | Answer-key SQL per question; golden set run on every route |
| Consistency | Nothing measured. Known risk: "exclude cancelled/returned" lives in `ai_context` text, not the measure | Not started | Each question 3x per route, across Claude, MCP and the Omni UI |
| Auditability | **Differs from the source doc's note:** here SQL *is* visible. The MCP `query_data` tool returns the SQL Cube generated, and each Claude Dashboard tile has an expandable SQL section. Change history is Git for Cube | Partial | Can a non-technical user see the definition and change history on each route? |
| Security | `cube.js` `queryRewrite` filters by `country` in the token. Not run as a test. Local setup uses one shared login | Observed | The restricted-user test; SSO/OAuth and schema-restriction questions |
| Ease of use and sharing | Claude Dashboards is chat-built, with per-tile SQL; no non-technical-user task test | Observed | Task test with a non-technical user: build, edit, share |
| Claude to Omni | A Claude dashboard can be imported into Omni (import tool exists in the Omni connector); not yet exercised here | Partial | Whether both need the identical warehouse connection, and what Omni does from Claude |
| Competitors | None | Not started | Research on how others handle each route |

**Evidence:** [Findings.md](Findings.md) holds the test results behind every score.

**Scoring matrix:** [Scoring Matrix.md](Scoring%20Matrix.md) holds the 8 criteria x 4 routes grid, rubric and score sheet.

## How this maps to the scenarios already in `PLAN.md`

| Scenario in PLAN.md | Criterion it feeds |
|---|---|
| 1. Ease of changing a metric | Adding a metric |
| 2. SQL output and number verification | Accuracy, Auditability |
| 3. How scalable it is | Total cost, Setup and upkeep |
| 4. Who can set up and maintain it | Setup and upkeep |
| 5. Consistency across clients | Consistency |

**Gaps in our scenarios vs these criteria:** Security (the restricted-user test), Ease of use for a non-technical user, and **Route A (Claude + warehouse)** are not covered. Plan 1 so far compares Routes B and C only; the North Star needs Route A as the baseline.

## Open questions for leadership

**Are we heading the right way?** (proposed answer in italics)

| Question | Proposed answer |
|---|---|
| Prove Claude Dashboards are not enough, or show where each fits? | *Prove it for Claude + warehouse; position manual semantic layers as working, just slower and with a data engineer.* |
| Who is this for, who reviews it, can we name competitors? | *Treat as customer-facing; agree reviewers now; research competitors before naming any.* |
| Do our three routes match last week's four-option slide? | *Map them before review; fix whichever is out of date.* |
| Is Cube a fair stand-in for manual semantic layers; is Cube Cloud in scope? | *Cube is one example; claim nothing about dbt or SSV until tested; add Cloud only for the full build-it-yourself range.* |
| How much more to build before reporting? | *None. Run the three tests on what exists, then write up. Agree a stop date.* |
| Why would a customer still need Omni if Claude sits on top? | *Definitions, permissions and change history live in the layer; Claude is one way to ask. Confirm integration details with product.* |

**How do we score without it being arbitrary?** Score what we can count; write anchors for the rest before testing.

| Question | Proposed answer |
|---|---|
| Measured numbers vs 1-5 opinions? | *Numbers where possible (share of runs matching, hours logged, edits per change, security pass/fail); otherwise a written 0-3 scale agreed before testing.* |
| Who sets the weights across the five seats? | *Leadership. Show results weighted and unweighted.* |
| Who scores? | *Two people, independently, from the same evidence; discuss differences.* |
| One total score or per criterion? | *Per criterion, security as pass/fail; no composite unless leadership wants one.* |
| Evidence level per claim? | *Tested for anything customer-facing; Documented only with a source; Asserted never published.* |
| Which Claude, which data, when? | *Name plan and model, date-stamp every result, add one messier realistic dataset before going external.* |

## Short term vs long term

Setup is not the argument: any route can be stood up in hours to days. The difference shows in the **cost of the tenth metric**.

| | First month | After a year |
|---|---|---|
| Setup | Hours to days on any route | Already paid for |
| Adding a metric | One metric, one person, quick everywhere | Dozens of metrics: does each cost the same, or more? Count edits per change |
| Upkeep | Barely noticed | Someone owns it weekly: connections, broken dashboards, drifted definitions |
| IT and tools | One person holds the stack in their head | Warehouse, layer, Claude and BI each need an owner, access reviews, upgrades. Count handoffs |
| Trust | A few dashboards, easy to eyeball | Dashboards multiply; nobody can tell which number is right |

## Caveats (from the source doc)

- Test data is made up; add one messier, realistic dataset before anything goes external.
- Results change by Claude plan, model and release; date-stamp everything.
- We built the routes, so we are biased; use two independent scorers.

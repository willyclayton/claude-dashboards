# Next steps (planned 2026-10-28, from the Claude Dashboards sync)

Source: [conversations/2026-10-28-claude-dashboards-sync.md](../conversations/2026-10-28-claude-dashboards-sync.md). Owner: Will, with Adrien. This sits on top of [plan.md](plan.md); it does not replace the experiments in [eval/adrien-question-set/](eval/adrien-question-set/README.md).

## 1. What the call decided

- **Show the team early, unfinished.** Tomorrow's weekly solutions meeting (morning, 2026-10-29): 10 to 20 minutes, open-ended. Not a deck, not final. Goal is for people to "play Omni advocate" against what we've built and tell us what to defend against and build next.
- **The story matters more than the artifact.** Write it end to end: "up to here it works great; from here it doesn't, and this is why", with Omni as the parallel path. Package it as internal and public-facing versions later.
- **The takeaway is what it takes, not whether it can be done.** Will is a team of one with Cube hosted locally and a personal access token. The question is whether this works across a 30-person team, who maintains it, and what breaks.
- **Everything has been done with open source on purpose.** If a team has to buy Cube Cloud or the dbt semantic layer to get what we built, the conclusion is "might as well buy Omni".
- **Next deliverables (week of 2026-11-02):** a slide deck with two lenses, "better together" (partnership) and competitive ("what you're still missing on your own"), plus an end-to-end demo of the best-case deployment. Exact shape is intentionally still open.

## 2. Before tomorrow's meeting

| # | Task | Why | Status |
|---|---|---|---|
| 1 | Make one Claude dashboard from the Cube chats (paste "build me a Claude dashboard out of this" into the end of a question session; or give it a screenshot of the existing dashboard to recreate) | Justin asked for it; it starts the BI evaluation. Adrien's first attempt failed to load every query, which is itself a learning | Not started |
| 2 | Finish experiment C round 1 (3 runs on the bare model after the net-revenue definitions) | Gives the "before and after" numbers for the slide | Waiting on your runs |
| 3 | Test "can Claude query something Cube doesn't model?" | Justin's first challenge (below) | Not started; quick test |
| 4 | One slide: what we've done, what's easy, what's hard, effort so far | Agreed format for tomorrow | Draft below |

### The "outside Cube" test (task 3)
Justin asked whether Claude can reach Snowflake schemas that Cube doesn't model. Concrete version: our Snowflake role can read six tables, but the live Cube model exposes only three of them (order items, inventory items, users). `EVENTS`, `PRODUCTS` and `DISTRIBUTION_CENTERS` are readable by the role but not modeled.
- Ask Claude (only `cube` on): "How many website sessions did we have last month?" (needs `EVENTS`) and "Which distribution center ships the most items?" (needs `DISTRIBUTION_CENTERS`).
- Expected: it says it can't, because the wrapper only exposes the modeled view and Cube has no raw SQL tool here. Record the exact reply.
- The honest nuance for the story: the access boundary is two layers. The Snowflake role limits what Cube can ever read; the Cube model limits what Claude can ask. Claude is stopped by the second one even for data the first would allow.

## 3. Answers to the questions raised on the call (draft, for tomorrow)

| Question | Current answer | Evidence / gap |
|---|---|---|
| Does it deterministically hit Cube every time? | Yes in our setup: only the `cube` connector is on, so there is no other route | Runs: no denied or failed queries in 3 curated and 3 bare runs. Caveat: depends on turning other connectors off; Claude Docs and Visualize stayed on (neither reaches data) |
| Can you query things not defined in Cube? | No, not through this connector; it exposes only the modeled view | Task 3 to confirm. A raw-SQL connector would change this, and would bring back the "raw SQL" approach Omni positions against |
| Does Cube mirror whatever is in Snowflake automatically? | No. Cube only knows what the YAML models; unmodeled tables and columns are invisible | Bare model exposes 3 of 6 tables, and no personal columns |
| Does Cube have an equivalent of Omni topics? | Views are the closest thing. Our `sales` view is the only thing Claude sees | Needs a short comparison write-up |
| Is there a good connector to drive a front-end dashboard, and does a dashboard reliably hit a Cube object? | Unknown at the BI layer. Earlier work found that Claude Dashboards only refresh live if the connector is hosted publicly with auth | Task 1 and the old pain log ([old/docs/plan-1/pain-log-hosting-the-cube-mcp.md](../old/docs/plan-1/pain-log-hosting-the-cube-mcp.md)) |
| Who adds a new metric, and how do we stop downstream breaking? | Still Will or Adrien. Editing YAML takes minutes, but there is no change review, no tests that guard downstream consumers, no versioning beyond Git | We have the timing (about 10 minutes edit to verified); we do not have a downstream-impact test |
| Row-level security, OAuth into Snowflake | Out of scope for tomorrow. We used a personal access token and a role limited to six tables | Flagged by Justin as "next step down the line" |

## 4. Effort numbers for the slide

- Calendar: about 2 weeks, with a daily sync between Will and Adrien, plus individual build time outside those meetings.
- Hours since the 2026-10-26 restart, from [effort-log.csv](effort-log.csv): about 2.4 logged hours across 14 entries, 4 of which logged errors. That counts only work logged since the restart. Hours before it (Cube lab, first Claude Dashboard, bake-off) are not in this log; the old estimate is in [old/docs/plan-1/plan.md](../old/docs/plan-1/plan.md) section 10. **Need Will's own total before anyone quotes a number.**
- Blockers to quote: waiting for `ACME_ADMIN` from a Snowflake admin; a Snowflake admin needed to create the read-only role; token pasted in chat needs rotating; Docker/env gotchas (restart vs recreate).

## 5. Draft one-slide content

**What we did.** Snowflake `ACME_CO` read through Cube Core (open source, local) with Claude Desktop as the only connector. Same 10-question test Adrien ran on dbt.
**What's easy.** Defining a metric in YAML and getting Claude to use it by name. Curated model: 30 of 30 answers correct and identical across 3 runs. A metric change shows up in Claude's answer in minutes.
**What's hard.** With no definitions the same model got 5 of 10 (strict), consistently wrong the same way (revenue counted cancelled and returned). Everything beyond question-answering is missing. There is no workbook or UI to explore, no Excel-style functions, no way for an end user to contribute to the semantic layer, no foldering or permissions, no shared hosting. Each of these is an extra thing to build or buy.
**Effort.** About 2 weeks calendar with two people; hours TBD.

## 6. Omni demo-parity checklist (for the week-of-11-02 deliverable)

Walk through a standard Omni BI demo and try the same step against the best-case Cube build. Mark each yes, no, or partial, with a screenshot.

| Step in a normal Omni demo | Cube + Claude |
|---|---|
| Ask a question with AI | Yes (our runs) |
| Compass button / explain this / explore this | To test; Justin expects "rebuild the UI" |
| Open the result in a workbook and play with the UI | No (per the call) |
| Put Excel-style functions on a result | No (per the call) |
| Contribute back to the semantic layer as an end user | No (per the call) |
| Build a dashboard from the answer | Partial: Claude Dashboards, but queries failed to load for Adrien and refresh needs a hosted connector |
| Foldering and permissions | No (per the call) |
| Row-level security | Not tested |

## 7. Plan for the week of 2026-11-02

1. Collect questions from the 2026-10-29 meeting and add them to a list here, tagged "can answer now", "needs a test", "needs a build".
2. Finish experiment C (round 1 after-runs; decide whether to do round 2: net margin and repeat customers), then write the before/after result.
3. Run the Omni demo-parity checklist above.
4. Draft the story write-up (internal first): what works, where it stops and why, the effort, and build versus buy.
5. Draft the slide deck with the two lenses (better together, competitive). Check with Justin before building the demo ("Morph Global demo" in the transcript is garbled and unclear).
6. Coordinate with Adrien so the dbt and Cube sections use the same criteria and numbers. His dbt results, his Claude Dashboard attempt, and the criteria sheet are the other half.

## 8. Open questions
- Which meeting is tomorrow's: the weekly solutions meeting, morning; who is presenting beyond Will and Adrien?
- Do we show the live Cube setup or only screenshots?
- Is the Claude Dashboard attempt a go for tomorrow morning, given Adrien's first try failed? If it fails again, say so as a learning rather than hide it.
- Exact total hours for both of us (Will asked, per the call, to estimate).

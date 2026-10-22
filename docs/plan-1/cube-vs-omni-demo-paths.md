# Cube vs Omni demo, by path (devil's advocate edition)

*2026-10-22. The pitch you are testing: "Screw Omni, I can do all of this in Cube." Each path is a standalone workflow with its own persona. Everything below was run against the repo in this project. Omni steps used the Omni CLI and agent on **throwaway branches**, never merged. Companion to [cube-demo-guide.md](cube-demo-guide.md) (the build) and [omni-vs-claude-cube.md](omni-vs-claude-cube.md) (the comparison). Raw output is in `Plan 1/bakeoff/results/`.*

## Read this first: three corrections to the story

These came out of testing and change what is safe to say in a demo.

1. **"Omni is deterministic, Claude hallucinates" is only half true.** Omni compiles a semantic query to SQL deterministically, and the AI can only use modeled fields. But an LLM still chooses *which* field and topic. Asked the same question three times, Cube answered $698,416.89 three times; Omni answered it twice and returned **$1,396,833.78 the third time** (the agent picked the other topic, whose revenue isn't halved) even though the prompt named the Sales topic. Omni's own docs say AI context "guides" and is "not a guarantee". The honest edge: Omni gives you tools to govern the AI (topic scoping, `ai_fields`, evals); in Cube you build that yourself.
2. **In Cube, end users do not need Snowflake access.** Cube connects with one service credential; Claude only holds a Cube token. The access problem you describe belongs to *Claude straight to the warehouse* (route 1). Cube's real cost is hosting the MCP and building identity and permissions around it.
3. **Neither tool bakes the "exclude cancelled and returned" rule into its default revenue measure.** Both rely on AI context to apply it. In Cube we added `net_revenue`, which enforces it. In Omni the same one-block edit takes about 5.6 s on a branch, or use a topic-level `always_where_filters`. Don't claim Omni has it baked in out of the box.

## Path 1: the end user asks a question

**Persona:** analyst or executive in Claude. **Goal:** natural-language question, trusted answer, and proof of why.

**Show (about 5 min):**

1. In Claude Desktop with the Cube tools: *"What was net revenue by month last quarter? Show the SQL."*
2. Point at the SQL Cube generated. Nobody mentioned cancelled or returned orders, yet:
   ```sql
   SELECT sum(CASE WHEN ("order_items".STATUS NOT IN ('Cancelled','Returned'))
                   THEN "order_items".SALE_PRICE * 0.5 END) "sales__net_revenue"
   FROM ANALYTICS_PROD.ECOMM.ORDER_ITEMS AS "order_items"
   ```
   The exclusion and the `* 0.5` come from the measure definition, not from the question.
3. Ask something out of scope: *"What was customer NPS last quarter?"* The answer refuses and says it won't invent a definition.
4. Build the dashboard with one prompt that includes **Claude Dashboard** (KPI row plus 5 charts, SQL on every tile).

**Measured:** Cube $698,416.89 for Q3 on every run; an out-of-scope question was refused; each dashboard tile has an SQL section.
**Pitfall:** the dashboard only stays live for others if the MCP is hosted remotely (path 3). Ambiguous questions ("show me sales") are answered with a guess by every route, and Claude alone found an undocumented `MONTHLY_SALES_OVERVIEW` table.
**Omni side:** the same question through the Omni connector returned $698,416.89 on 2 of 3 runs (see path 5). Omni's answer includes a definitions table and the SQL.

## Path 2: a data engineer takes a change request

**Persona:** data engineer (or an analyst with repo access). **Goal:** an end user says "that's not what I mean by X"; the engineer fixes the layer; the user re-asks.

**The two requests we ran, with Claude Code as the engineer:**

| | T1: "AOV should be net revenue per order" | T2: "add a repeat-customer rate" |
|---|---|---|
| Before (Claude + Cube) | $23.72 by dividing gross revenue by gross orders by hand; a second "net" figure of $22.63 mixed net revenue with all orders. It ignored the mislabeled synonym (`aov` pointed at average item price) | Refused: no such measure |
| What the engineer changed | Added `net_orders` and `aov`; moved the `aov` synonym off `average_sale_price` | Added a `lifetime_orders` subquery dimension on `users` plus `repeat_customers` and `repeat_customer_rate` |
| Claude Code time and cost | **36.5 s, $0.24** | **34.3 s, $0.21** |
| After | **$23.70** via the governed `aov` measure | **54.5%** (14,711 of 27,005) |
| Hand-checked SQL | $698,416.89 / 29,465 = **$23.70** | **54.475%**: matches |

**Omni, same T1 request** (scripted through the Omni CLI on a branch, not Claude Code): before the change Omni's agent already composed total revenue / total orders correctly, **$23.70**; edit plus validation took **1.5 s** and the re-ask on the branch **14.8 s**, using the new `average_order_value` measure.

**Your 5-15 minutes:** we did not time a human doing this by hand; that is the number to capture in the demo (stopwatch table below). What we can say: the *typing* is seconds with Claude Code in either tool. The human cost is reading the request, deciding the definition, checking the number against SQL, and getting it reviewed and deployed. In both runs Claude Code could not verify its own work (the headless shell blocked its test command), so a person had to check the numbers; we did, against SQL.

**How an end user would do this in Cube:** they cannot, unless they can edit YAML in the repo and run Cube. In practice: ticket, engineer edits `model/cubes/*.yml`, tests, pushes, deploys. **In Omni:** Documented path is a workbook field promoted through branch review ([promotion docs](https://docs.omni.co/modeling/develop/promotion)); not driven by us.
**Pitfall (Cube):** the T2 solution is a correlated subquery in the model, easy to write, easy to make slow. Review model SQL like code.
**Pitfall (the demo itself):** show the "reask after the edit" live; Cube hot-reloads in about 1-3 s, so it feels instant.

## Path 3: an admin locks people down, and someone shares the dashboard

**Persona:** admin. **Goal:** viewers see less than analysts, analysts less than admins; share the dashboard safely.

**What we built in Cube** (production mode, groups on the `sales` view): admin and analyst see everything (analyst without cost); viewer sees only their country, no margin, no customer email.

| Token | Revenue by country | `avg_margin` | Customer email |
|---|---|---|---|
| admin | UK ($1,048,758.39)* | $24.07 | `jtaylor@gmail.com` |
| analyst | same* | $24.07 | visible |
| viewer, country=UK | UK only | **hidden member error** | **hidden member error** |
| viewer, no country | **empty** | hidden | hidden |
| no group claim | **everything hidden** | hidden | hidden |

\*Admin and analyst were still filtered to UK because our `queryRewrite` also applies whenever a country claim is present. Mixing `queryRewrite` and policies stacks; use one.

**What it took (the "hand-code something in Cube" part):** the policy YAML, plus a `contextToGroups` function in `cube.js`, plus a restart. Our first two attempts hid every member for everyone: Cube passes `{securityContext}` into that function, and we read the wrong level. The error is an unfriendly HTTP 500 ("You requested hidden member ... make it visible using `public: true`"), not a 403.
**What is still missing:** who issues the tokens. We minted them by hand. Real users need an identity provider, a token service, and an MCP that authenticates callers (ours had one shared identity and no auth on HTTP).
**Sharing:** the dashboard is private ("Only you"); our Cube queries said "This query isn't refreshing automatically" because the MCP runs locally. Per third-party coverage, sharing live needs a hosted MCP and each viewer's own connection.
**Omni side (Documented, not tested by us):** connection roles and content roles (Viewer/Editor/Manager/Owner), access filters from user attributes, grants, SAML/OIDC/SCIM, folders, deliveries, embed. MCP runs as the signed-in user ([docs](https://docs.omni.co/ai/mcp/authentication)). Our restricted-user test was blocked (needs an Organization API key).

## Path 4: "what breaks if I change this?" and "how do I test on a branch?"

**Persona:** data engineer or admin making a change safely.

**Branching in Cube (answering your open question):** Cube Core has no branch concept, but a git branch is just a folder. We ran `git worktree add`, started a second Cube container on port 4002 pointing at the branch's `model/`, and pointed Claude at it by setting `CUBE_API_URL` in the MCP config. Ready in **5 s**. Claude on the branch saw a branch-only metric ($42,586.17); Claude on main didn't have it (HTTP 400) and improvised by filtering `total_revenue` to Shipped, landing on the same number and flagging the 0.5 factor. Cost: a port, a container and a separate MCP config per branch.

**Impact analysis:**

| | Cube | Omni |
|---|---|---|
| Broken column or field in the model | Loads fine; only the broken metric fails when queried (1.9 s, raw Snowflake error) | `validate` caught it in 1.5 s with the YAML path and an auto-fix |
| "Which dashboards use this?" | **No answer.** Cube has no content catalog; you grep your code and rerun every query | Content Validator exists. In our test it found the scratch dashboard using a field on main, **but reported no issue on the branch after we removed that field from the topic, so we could not confirm it catches this case.** Ask Omni before promising it in a demo |
| Test a change safely | Worktree + second container (5 s) | Branch Mode (Documented), branch queries and AI questions (Tested) |

**Say:** "With Cube, the safe-change process is something you build. With Omni it is a feature, though I haven't proven the dashboard-impact piece."
**Cleanup:** the Omni branches were deleted and the scratch dashboard moved to Trash.

## Path 5: "that's not what I mean": confusion and consistency

**Persona:** end user, repeatedly. **Goal:** see where the headless layer + Claude goes wrong, and where Omni does.

| Test | Cube | Omni (Sales topic named in prompt) |
|---|---|---|
| "Revenue last quarter?" x3 | $698,416.89 x3, always `net_revenue` | $698,416.89 x2; **$1,396,833.78 x1** (wrong topic, unhalved) |
| AOV before any fix | Composed by hand: $23.72 and a mixed-basis $22.63 | $23.70, composed correctly |
| Out-of-scope | Refused | Refused |
| Ambiguous ("show me sales") | Monthly net revenue | All-time overview |

**What this shows:** both fail sometimes, in different ways. Cube's failure mode is Claude composing metrics itself when the layer lacks one (fixable by adding the measure: path 2). Omni's is landing on a different topic definition (fixable by topic scoping and curation, which the docs support; we haven't tried the MCP header). A demo that claims either is immune will get caught.
**Mitigations to show:** in Cube, strongly named measures (`net_revenue`), synonyms moved to the right metric, and a wrapper that only exposes the view. In Omni, scope the MCP to a topic via setup headers, `ai_fields`, and evals ([docs](https://docs.omni.co/ai/evals)).

## The stopwatch table (fill this in live)

You asked how long it takes to stand up a dashboard and do everything. Machine time is known; the human and UI time is the blank worth capturing.

| Step | Cube + Claude | Omni | Measured so far |
|---|---|---|---|
| Stand up Docker + Cube + first query | __ min | n/a | Our build: about a session, plus about an hour for Snowflake access (not logged) |
| Port the model | __ min | __ min | Claude Code did it in one session |
| Build the dashboard (KPI + 5 charts) | __ min | __ min | One chat prompt in Claude Dashboards |
| Take a change request to a verified answer | __ min (human) | __ min (human) | Claude Code 34-37 s; Omni CLI 1.5 s edit and 16 s to answer; human review not timed |
| Add a viewer role and restrict a column | __ min | __ min | Cube: three attempts (hand-written function); Omni Documented |
| Share the dashboard live with a colleague | __ min | __ min | Cube: needs a hosted MCP (not built); Omni Documented |
| Find what a change would break | __ min | __ min | Cube: no tool; Omni: validator (inconclusive) |

## Run-of-show (35 min)

1. Path 1, 6 min. 2. Path 2, 10 min (do T1 live; the edit and the re-ask). 3. Path 4 branch, 5 min. 4. Path 3, 8 min (the table). 5. Path 5, 4 min. 6. Close on the stopwatch table, 2 min.

## What is not tested

A human doing the change by hand, the Omni business-user UI path, an Omni restricted-user, an Omni topic-scoped MCP, a hosted and authenticated Cube MCP, and the Content Validator on a case that should break. See the [tracker](../project-tracker.csv).

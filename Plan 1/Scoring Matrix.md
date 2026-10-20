# Plan 1: Scoring Matrix (8 criteria x 4 routes)

*Companion to [Success Criteria.md](Success%20Criteria.md). Evidence and method: [Findings.md](Findings.md). CSV copy: [Scoring Matrix.csv](Scoring%20Matrix.csv). Updated 2026-10-20 after the bake-off.*

> **Status:** scores now rest on tests we ran where tagged **Tested**. Single scorer; two independent scorers are still required before anything customer-facing. Omni cells are mostly **Documented** (from Omni's docs), because the Omni business-user flow and a restricted Omni user were not run.

## The four routes (from the "Anthropic says I need a semantic layer..now what?" slide)

| # | Route | What it is |
|---|---|---|
| 1 | Claude on its own | Claude straight to Snowflake |
| 2 | Claude + 3rd-party layer | Cube Core built and tested. Snowflake semantic views and MetricFlow not tried |
| 3 | Claude + Omni | Path A: Claude calls Omni MCP. Path B: draft in Claude, finish in Omni |
| 4 | Omni (+ Claude) | Semantic layer, UI and AI chat in one place |

## 1. Score grid (0-3, higher is better; — = not scoreable yet)

| Criterion | 1. Claude on its own | 2. Claude + 3rd-party layer (Cube Core) | 3. Claude + Omni | 4. Omni (+ Claude) |
|---|---|---|---|---|
| **Setup and upkeep** | **3** [Asserted] | **1** [Asserted] | **2** [Documented] | **3** [Documented] |
| **Adding a metric** | **0** [Asserted] | **DE 2 · Biz 1** [Tested] | **3** [Documented] | **3** [Documented] |
| **Total cost** | — | — | — | — |
| **Accuracy** | **1** [Tested] | **3** [Tested] | **0 unguided · 2 pinned** [Tested] | — |
| **Consistency** | **3** [Tested] | **3** [Tested] | **2** [Tested] | — |
| **Auditability** | **1** [Tested] | **1** [Tested] | **3** [Tested + Documented] | **3** [Documented] |
| **Security** | **FAIL** [Tested] | **FAIL as configured** [Tested] | **Untested (docs: PASS)** [Documented] | **Untested (docs: PASS)** [Documented] |
| **Ease of use and sharing** | **1** [Asserted] | **1** [Asserted] | **2** [Documented] | **3** [Documented] |

Tags: **Tested** = we ran it (see [Findings.md](Findings.md)). **Documented** = Omni's docs say so, linked. **Asserted** = expectation, never published.

## 2. How to read it (the lens that matters)

- **Where the tools tie or Cube leads:** accuracy, consistency and per-answer cost. A governed layer returns its definition deterministically, so Cube (100%) and Omni pinned to the right topic (93%) are close. Cube was cheaper and faster per answer.
- **Where Omni leads:** *who can change a metric* (business user, with review), auditability for non-technical users, security (documented, untested here) and self-service. These come from the persona lens, not from raw query accuracy.
- **Where Omni has a real risk:** topic overlap. Left to choose, Omni's agent used a topic with a different revenue definition and scored 36.7%. This needs data-team cleanup, not a different tool.
- **Where Claude on its own fails:** definitions. Consistently wrong on revenue is worse than inconsistent.

## 3. Why each score

| Criterion | Route | Score | Tag | Rationale |
|---|---|---|---|---|
| Setup and upkeep | 1. Claude on its own | 3 | Asserted | Nothing to stand up. Low upkeep only because nothing is governed |
| Setup and upkeep | 2. Claude + 3rd-party layer (Cube Core) | 1 | Asserted | Docker, Python MCP wrapper, Snowflake PAT and role, macOS permission fix, mcp 2.x pin; production mode also needs a cache driver and a token-issuing layer. Data engineer needed. Hours not logged |
| Setup and upkeep | 3. Claude + Omni | 2 | Documented | Managed product; modelers own definitions; Claude connects via the official connector or OAuth (docs.omni.co/ai/mcp). Extra Claude-admin setup vs route 4 |
| Setup and upkeep | 4. Omni (+ Claude) | 3 | Documented | Managed product, modelers own the model, no glue to build. Not timed |
| Adding a metric | 1. Claude on its own | 0 | Asserted | No governed place; every dashboard carries its own SQL |
| Adding a metric | 2. Claude + 3rd-party layer (Cube Core) | DE 2 · Biz 1 | Tested | Engineer seat: 1 file, 1 block, 3.4 s, 3 of 3 dashboard queries changed (Tested). Business user cannot edit YAML: request to data engineering, edit, push, deploy (process stated by the team, not timed) |
| Adding a metric | 3. Claude + Omni | 3 | Documented | Business user or modeler creates a metric and promotes it through a reviewed branch (docs.omni.co/content/develop/branch-mode). Not run by us |
| Adding a metric | 4. Omni (+ Claude) | 3 | Documented | Same model change, made hands-on in Omni's UI. Not run by us |
| Total cost | 1. Claude on its own | — | — | Not measured. Per-answer model cost $0.123, 14.9 s |
| Total cost | 2. Claude + 3rd-party layer (Cube Core) | — | — | Not measured. Per-answer model cost $0.048, 9.0 s (lowest); Cube Core is free but engineer hours are not |
| Total cost | 3. Claude + Omni | — | — | Not measured. Per-answer model cost $0.158, 34.2 s |
| Total cost | 4. Omni (+ Claude) | — | — | Not measured |
| Accuracy | 1. Claude on its own | 1 | Tested | 60.0% (18/30). Right on the 6 non-definition questions, 0/12 on the 4 definition questions (used raw SALE_PRICE, 2x) |
| Accuracy | 2. Claude + 3rd-party layer (Cube Core) | 3 | Tested | 100% (30/30). The model is a port of the key's own definitions, so a match is expected |
| Accuracy | 3. Claude + Omni | 0 unguided · 2 pinned | Tested | Agent picks topic: 36.7% (11/30), chose analytics_prod_ecomm__order_items_sv where revenue is not halved. Topic named: 93.3% (28/30); only miss is Q7 return rate (about 1.00 vs key 0.95) |
| Accuracy | 4. Omni (+ Claude) | — | — | Omni UI AI not driven here; shares route 3's engine |
| Consistency | 1. Claude on its own | 3 | Tested | 100% of questions gave identical answers across 3 runs, including the 4 wrong ones: consistently wrong |
| Consistency | 2. Claude + 3rd-party layer (Cube Core) | 3 | Tested | 100% |
| Consistency | 3. Claude + Omni | 2 | Tested | 90% (unguided and pinned) |
| Consistency | 4. Omni (+ Claude) | — | — | Not tested separately |
| Auditability | 1. Claude on its own | 1 | Tested | SQL visible; no definition, no change history |
| Auditability | 2. Claude + 3rd-party layer (Cube Core) | 1 | Tested | SQL visible (MCP returns it, per-tile SQL in Claude Dashboards). Change history is Git, for engineers. A non-technical user cannot read the YAML |
| Auditability | 3. Claude + Omni | 3 | Tested + Documented | Omni's agent returned the SQL and a field-definition table (Tested). Revision history, branches and optional Git are Documented (docs.omni.co/modeling/develop/history) |
| Auditability | 4. Omni (+ Claude) | 3 | Documented | Same model history and field definitions |
| Security | 1. Claude on its own | FAIL | Tested | Snowflake role DBT_DEMO_ROLE has OWNERSHIP on ORDER_ITEMS and sees 71 schemas; 0 row access policies, 0 masking policies. Nothing between Claude and the data |
| Security | 2. Claude + 3rd-party layer (Cube Core) | FAIL as configured | Tested | Dev mode: no token and forged tokens return all data. Production mode enforces auth and the country filter, but a token with no country claim sees everything, and our MCP wrapper mints exactly that token |
| Security | 3. Claude + Omni | Untested (docs: PASS) | Documented | MCP queries run under the signed-in user's permissions; access filters apply (docs.omni.co/ai/mcp/authentication). Needs a restricted Omni user to verify |
| Security | 4. Omni (+ Claude) | Untested (docs: PASS) | Documented | User attributes, access filters, SAML/OIDC, SCIM; AI respects permitted topics (docs.omni.co/ai/security) |
| Ease of use and sharing | 1. Claude on its own | 1 | Asserted | Good for quick drafts; no point-and-click editing, schedules, downloads, drilldowns or links |
| Ease of use and sharing | 2. Claude + 3rd-party layer (Cube Core) | 1 | Asserted | Claude Dashboards built by chat with per-tile SQL, but no schedules or folders; metrics live in YAML. No non-technical task test |
| Ease of use and sharing | 3. Claude + Omni | 2 | Documented | Path A stays in Claude; Path B finishes in Omni with folders, schedules, embedding (docs.omni.co/share/deliveries). Not task-tested |
| Ease of use and sharing | 4. Omni (+ Claude) | 3 | Documented | UI, folders, schedules, embedding and AI chat in one place. Not task-tested |

## 4. Rubric (proposed anchors; leadership to confirm)

| Criterion | What we measure | 0-3 anchors |
|---|---|---|
| **Setup and upkeep** | Hours to stand up; weekly upkeep hours; roles needed | 3 no data engineer, ≤1 h/wk · 2 engineer part-time, ≤2 h/wk · 1 engineer ≥2 h/wk or several tools to keep alive · 0 unowned, breaks |
| **Adding a metric** | Seat-by-seat: who can do it, how many edits and people (data engineer seat and business-user seat) | 3 business user can do it with review · 2 one edit but an engineer is needed · 1 request to an engineer, multiple steps · 0 no governed place, edits per dashboard |
| **Total cost** | Hours x role rate + direct spend, per 10 metrics per year (per-answer model cost recorded as a partial) | 3 within 25% of cheapest route · 2 up to 2x · 1 2-4x · 0 >4x |
| **Accuracy** | % of bake-off runs matching the answer key | 3 ≥95% · 2 80-94% · 1 50-79% · 0 <50% |
| **Consistency** | % of questions where all 3 runs agree (right or wrong) | 3 100% · 2 ≥90% · 1 ≥70% · 0 <70% |
| **Auditability** | Can a non-technical user see the definition, the SQL and the change history? | 3 all three · 2 definition only · 1 SQL only · 0 neither |
| **Security** | Restricted-user test: can a user reach data they shouldn't? (pass/fail) | PASS / FAIL, plus SSO/OAuth and schema-restriction notes |
| **Ease of use and sharing** | Non-technical user task test: build, edit, share | 3 all three unaided · 2 two · 1 one · 0 none |

## 5. Weights by seat (leadership sets; show weighted and unweighted)

| Criterion | Data engineer | Modeler | Claude admin | Technical end user | Non-technical end user |
|---|---|---|---|---|---|
| Setup and upkeep | | | | | |
| Adding a metric | | | | | |
| Total cost | | | | | |
| Accuracy | | | | | |
| Consistency | | | | | |
| Auditability | | | | | |
| Security | | | | | |
| Ease of use and sharing | | | | | |

## 6. Still open (see Findings.md section 2)

- Total cost: hours per role, licences, hosting.
- Omni: restricted-user security test; business-user metric-change flow; Omni UI AI (route 4).
- Bake-off at 25-50 questions (10 run); two independent scorers; a messier dataset.
- Route 2 beyond Cube Core (Snowflake semantic views, MetricFlow).
- Non-technical-user task test for ease of use.

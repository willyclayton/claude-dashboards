# Cube + Claude + Claude Code: build-it-yourself demo guide

*2026-10-22. Everything here was run against the repo in this project (Cube 1.8.8 in Docker, Snowflake `ANALYTICS_PROD.ECOMM`, Claude Desktop, Claude Code). Numbers are from [findings.md](findings.md). Pitfalls are marked **Pitfall**.*

## 0. What this demo is for

Build a semantic layer ourselves with Cube, front it with Claude, and make a Claude Dashboard on top. Then show where a "manual" layer holds up and where it needs an engineer, and compare with building the same thing in Omni.

From the 2026-10-20 meeting, keep two lenses apart so we don't conflate them:

- **Lens 1: evaluating semantic layers** (Cube, dbt, Snowflake semantic views against Omni). Sections 3 and 5 here.
- **Lens 2: evaluating the dashboard and BI output** (sharing, scheduling, editing). Section 4 pitfalls 3 and 4, plus the [40 more criteria](additional-criteria.md).

Ease of use and sharing a dashboard have little to do with whether the layer is Cube, dbt or a semantic view. Say which lens the customer is on before you demo.

**Time:** estimate of about 2 hours from scratch with Claude Code doing the typing (our own build was one session plus about an hour for Snowflake access; hours were not logged). Run-of-show for the live demo: 30 minutes (section 7).

## 1. Prerequisites

- Docker Desktop, Python 3.12, Claude Desktop (latest), Claude Code, a paid Claude plan.
- A Snowflake role that can read the schema. A personal access token works for a lab; **scope it to a role that can see the schema** (our first token's role had no access and every query failed with "not authorized").
- The model to port. We ported Omni's `analytics_prod_ecomm__sales` topic.
- Know that macOS blocks Desktop-launched processes from reading `~/Desktop` (see pitfall A3).

## 2. Build it (Claude Code does most of the typing)

| Step | What | Prompt or command | Result we saw |
|---|---|---|---|
| A1 | Stand up Cube | `docker compose up -d` in `Plan 1/cube-claude-lab/`, `.env` with Snowflake account, role, PAT and `CUBEJS_API_SECRET` | Playground at http://localhost:4000 |
| A2 | Port the model | Prompt Claude Code: *"Port this Omni topic YAML to Cube cubes and one public view called `sales`. Keep descriptions, synonyms and the AI instructions in `meta`."* | 4 cubes + 1 view, about 570 lines, compiled first time |
| A3 | Prove the numbers | `python tests/run_golden.py` compares Cube to hand-written SQL | 6/6 pass |
| A4 | Give Claude a way in | `mcp/server.py` exposes `describe_data` and `query_data` | Works over stdio and HTTP |
| A5 | Register it in Desktop | Add to `~/Library/Application Support/Claude/claude_desktop_config.json`, then **fully quit** (Cmd+Q) and reopen | Server shows as running |
| A6 | Ask a question | *"Using the cube tools, revenue by month for the last 6 months, with the SQL."* | Rows plus the SQL Cube ran |
| A7 | Build the dashboard | In Desktop: *"Using the cube tools, build me a Claude Dashboard: KPI row (revenue, orders, customers, average sale price, margin) and 5 charts."* Include the words **Claude Dashboard** | Built from one prompt; each tile has an SQL section |
| A8 | Verify | Compare tiles to the golden SQL; open a tile's SQL | Totals matched the key to the cent |

**Pitfalls while building**

- **A3 (permissions):** the server and its venv must live outside `~/Desktop`; Desktop's launched process got `PermissionError ... pyvenv.cfg`. Ours runs from `~/.cube-mcp/`. Re-copy `mcp/server.py` there after edits.
- **A4 (versions):** a fresh venv installed `mcp` 2.x, which removed `FastMCP`. Pin `mcp>=1.9,<2`.
- **A5 (restart):** Desktop reads MCP config only on a full quit and relaunch.
- **A1 (Snowflake role):** the role Cube uses can be broader than needed. Ours owns the table (`DBT_DEMO_ROLE`) and sees 71 schemas, with no row-access or masking policies. Ask for a read-only role.
- **A7 (wording):** the dashboard feature only triggers on "Claude Dashboard". It is not an artifact.
- **Data drifts:** the live tables grew between runs (distinct orders 252,701 on 10/16, 254,271 on 10/20). Compute any answer key the same day.

## 3. Pitfall demos (the four we were asked about)

### 3.1 "What if I want to update a metric?"

**Do:** change `total_revenue` to exclude cancelled and returned orders.
**How:** one edit in `model/cubes/order_items.yml` (add a `filters:` block to the measure), or just point people at the new `net_revenue` measure we added.
**Show:** edit, save, re-run the same three dashboard queries.

| What we measured | Cube | Omni (branch, via CLI) |
|---|---|---|
| Edit to verified | 3.4 s | 5.6 s |
| Files / blocks edited | 1 / 1 | 1 / 1 |
| Dashboard queries that changed | 3 of 3 | 3 of 3 |
| Total afterward | 5,754,404.54 | 5,754,404.54 |
| Brand-new metric (`returned_revenue`) queryable | 0.8 s | not run |

**Pitfall:** the seconds are the engineer's seat. A business user can't edit YAML. In Cube the real path is request, a data engineer edits, pushes and deploys; we did not time that path (as you described it: a request to data engineering, then edit, push and deploy). In Omni the business-user path is Documented (branch mode, review, promote), not driven by us.
**Say:** "Both tools propagate one edit everywhere. The difference is who is allowed to make it."

### 3.2 "Row-level security and permissioning: what do I do?"

We found three layers, with very different behavior.

| Setup | No token | Forged token | Token, `country=UK` | Token with no country claim |
|---|---|---|---|---|
| Lab as configured (dev mode + `queryRewrite`) | **all data** | **all data** | UK only | **all data** |
| Production mode + `queryRewrite` | 403 | 403 | UK only | **all data** (fails open) |
| Production mode + **native `access_policy`** | 403 | 403 | UK only | **nothing** (fails closed) |

**Do (production-safe version):** put `access_policy` on the `sales` view:

```yaml
access_policy:
  - group: "*"            # `role` is rejected in Cube 1.8.8; it must be group/groups
    row_level:
      filters:
        - member: users_country
          operator: equals
          values: ["{ securityContext.country }"]
```

and run Cube with `CUBEJS_DEV_MODE=false` and `CUBEJS_CACHE_AND_QUEUE_DRIVER=memory` (production mode won't start queries without a cache driver).

**Then the MCP layer, which is where it usually breaks:**

- Our wrapper mints one shared token. Without a claim, every Claude user is unrestricted. We added `CUBE_SECURITY_CONTEXT` (JSON claims in every token): Claude through a UK-scoped wrapper returned only UK ($1,004,479.13) and even flagged the filter it hadn't asked for.
- That identity is fixed **per server process**, not per caller. The HTTP version of the wrapper accepted an unauthenticated request (HTTP 200), so anyone who can reach it gets that process's identity. Real per-user security needs OAuth in front of the MCP and per-user token issuing. We did not build that.

**Pitfall:** do not demo `queryRewrite` as "secure": it fails open. Do not leave dev mode on.
**Omni comparison:** access filters from user attributes, SAML/OIDC/SCIM, MCP runs as the signed-in user (all Documented). Our restricted-user test in Omni was blocked: impersonation needs an Organization API key.

### 3.3 "If I need to share this dashboard, what happens?"

**Observed:** the Claude Dashboard is private ("Only you") with a Share button. In its side panel the Cube queries said **"This query isn't refreshing automatically"**, because our Cube MCP server runs on the laptop (stdio).
**Third-party coverage (tabulareditor.com, not Anthropic, check before quoting):** live dashboards need a remotely hosted MCP; local servers only feed extracts while building; viewers' queries run with their own connection and permissions; datasets cap at 8 MB; the page can only be changed by Claude.
**What we proved:** the wrapper works as a remote HTTP MCP and Claude connects to it by URL. We did **not** expose it to the internet (no auth, and it would publish lab data).

**Pitfall:** a Cube-backed dashboard is a snapshot for everyone except you unless you host the MCP, secure it, and give every viewer their own identity. That is real work (tunnel or Cube Cloud's MCP, OAuth, tokens).
**Omni comparison:** the connector is already hosted; sharing, folders, scheduled deliveries, PDF/CSV and embedding are Documented. Not tested by us.

### 3.4 "What happens if a metric changes?" (three flavors)

| Flavor | What we did | Cube | Omni |
|---|---|---|---|
| A definition changes | Change `total_revenue` once | 3 of 3 queries updated, 0 fixed by hand | 3 of 3, 0 by hand |
| A column upstream breaks | Point a measure at a missing column | Model loads fine; `/meta` fine; **only that metric fails at query time** with a raw Snowflake error, 1.9 s. Nothing warns you before. | `validate` flagged it in 1.5 s: field not found, the YAML path, and an auto-fix suggestion |
| Two definitions of revenue exist | Ask an unguided question | n/a (one view) | The agent chose the topic where revenue isn't halved: 36.7% of answers matched. Pinned to the Sales topic: 93.3% |

**Pitfall (Cube):** no pre-merge validation. Anything you want caught before production, you build yourself (our golden tests do this for numbers, not for broken references).
**Pitfall (Omni, honest):** overlapping topics can send the AI to a different definition. The docs say the MCP can be scoped to a topic through setup headers; we have not tried it.
**Say:** "A governed layer makes a definition change instant. What matters is who can make it, whether it's checked first, and whether there's one definition."

## 4. More things we built or broke (use as backups)

| Experiment | Result |
|---|---|
| New metric from scratch (`returned_revenue`) | Queryable in 0.8 s, matches the status-filter query exactly |
| Enforce the exclusion rule in a measure (`net_revenue`) | Matches the answer key to the cent ($1,319,165.62 for Apr-Sep); queryable in 2.3 s |
| Rolling 30-day revenue | Worked, 1.6 s, six daily values |
| Segment (`complete_only`) | Equals `total_revenue_completed` |
| Pre-aggregation (revenue by day and status) | Used 1.4 s after the edit; repeat queries 9-25 ms. Cube Store ships in the image |
| Out-of-scope question ("NPS last quarter") | Refused; said it wouldn't invent a definition |
| Ambiguous ("Show me sales") | Nobody clarified. Claude alone found and used an undocumented `MONTHLY_SALES_OVERVIEW` table |
| Relative date ("last quarter") | Cube and Omni both $698,416.89; Claude alone about $1.40M |

Kept in the model: `net_revenue`, `returned_revenue`, `rolling_30d_revenue`, `complete_only` (additive; 6/6 golden tests still pass). Not kept: the access policy and pre-aggregation (they change behavior for tokens with no claim and for caching).

## 5. Gap register (what building it ourselves costs)

| # | Gap | Severity | Evidence | Workaround | In Omni |
|---|---|---|---|---|---|
| 1 | Dev mode accepts no or forged tokens | High | Security tests | Production mode | n/a |
| 2 | `queryRewrite` fails open on a missing claim | High | Section 3.2 | Native `access_policy` | Access filters |
| 3 | MCP wrapper has one shared identity, no auth on HTTP | High | Wrapper test | OAuth gateway, per-user tokens | MCP runs as signed-in user |
| 4 | Dashboard not live for others (local MCP) | High | Side panel; third-party | Host the MCP | Hosted connector |
| 5 | No pre-merge validation of the model | Medium | Broken-column test | CI with queries (we have golden tests) | `validate` |
| 6 | Exclusion rule is advisory text | Medium | `ai_context` | `net_revenue`, `default_filters` | Topic filters |
| 7 | No usage analytics or question logs | Medium | Container logs only | Build logging | AI Hub, Analytics |
| 8 | Business users can't change metrics | Medium | Persona lens | Ticket to data engineering | Branch review, hands-on |
| 9 | Upkeep owner needed (image, tokens, hosting) | Medium | Setup notes | A named person | Managed |
| 10 | SSO, audit logging and longer query history sit in Cube Cloud tiers | Low | cube.dev/pricing | Pay for Cloud | Documented as included |

## 6. Prompts that worked (Claude Code)

1. *"Read `Plan 1/omni-source/analytics_prod_ecomm__sales.topic` and port it to Cube cubes and a `sales` view. Keep descriptions, synonyms and AI instructions in `meta`."*
2. *"Write golden tests that compare each Cube measure to hand-written Snowflake SQL."*
3. *"Add an MCP server with `describe_data` and `query_data` that returns the SQL Cube generated."*
4. *"Add a measure `net_revenue` that excludes Cancelled and Returned orders, then verify it against SQL."*
5. *"Add an access policy on the view that filters by the token's country claim, then test with no token, a forged token, a UK token and a token with no claim."*
6. *"Point a measure at a missing column and tell me what breaks and when you find out."*

## 7. Run-of-show (30 minutes)

1. **2 min:** the question and the two lenses. Ask which lens the customer is on.
2. **5 min:** Claude asks Cube for revenue by month; show the SQL. Then the Claude Dashboard with tile SQL.
3. **5 min:** update a metric (3.1). Same edit in Omni.
4. **7 min:** security (3.2): the table, then the UK-scoped Claude.
5. **5 min:** sharing (3.3): the "isn't refreshing automatically" panel.
6. **4 min:** broken column (3.4): Cube silent, Omni `validate`.
7. **2 min:** gap register and what we haven't tested.

## 8. Reset after the demo

- `git checkout Plan\ 1/cube-claude-lab/model` to drop any edits; `docker compose restart cube` if the cache looks stale.
- Delete any throwaway Omni branch (`omni models delete-branch`); we deleted ours.
- Rotate the Snowflake PAT and `CUBEJS_API_SECRET` after the lab; the secret sits in plaintext in the Desktop config.

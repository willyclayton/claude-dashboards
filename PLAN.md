# Claude Dashboards + Cube vs Omni: Project Plan

## Goal
Test, honestly and as a devil's advocate to Omni, whether Claude Dashboards plus a free, open-source semantic layer (Cube) is a viable alternative to Omni's semantic layer. Report findings to the central data team on: **answer accuracy, setup effort, upkeep (how definitions change), and cost.**

Same data for both sides: Snowflake `ANALYTICS_PROD.ECOMM` (order items, users, inventory, products).

## The plan
1. **Align the data.** Omni and Snowflake must read the same database. Done.
2. **Build the Cube model.** Convert Omni's `analytics_prod_ecomm__sales` topic into Cube YAML. Done; it compiles.
3. **Connect Cube to Snowflake.** Blocked on a Snowflake key (needs an admin).
4. **Golden tests.** Six checks compare Cube's answers to hand-written SQL.
5. **Connect Claude.** Either my small local MCP server or Cube Cloud's hosted MCP.
6. **Run the same 10-15 questions** through Claude alone, Claude + Cube, and Claude + Omni. Score accuracy.
7. **Change test.** Change one definition in Cube and in Omni. Time both.
8. **Write up findings** for the data team (accuracy, hours, cost, upkeep).

## Findings so far
- Omni's `sale_price` is defined as `SALE_PRICE * 0.5` in the semantic layer, so revenue is half the raw table. This is the definition-vs-raw-table gap a semantic layer exists to handle. It's unclear whether it's intentional.
- `total_revenue` includes all statuses, but the topic's AI instructions say to exclude cancelled and returned orders. The definition and the instruction conflict.
- The simple `ecommerce_sales` topic in Omni is bare (no descriptions or revenue measures). The prod topics from Snowflake semantic views carry the real definitions.

## Tools: free vs paid
| Tool | Used for | Cost |
|---|---|---|
| Cube Core (open source) | Semantic layer, runs locally | Free |
| Cube Cloud | Hosted Cube, hosted MCP with OAuth | Free tier or paid; plan limits unverified |
| Docker Desktop | Runs Cube locally | Free for personal and small-business use; check company eligibility |
| Python 3.12 + uv | MCP wrapper, tests | Free |
| Cloudflare quick tunnel | Public URL so claude.ai can reach local MCP | Free (lab data only) |
| Snowflake | Data, queries | Existing, paid (warehouse credits) |
| Omni | The comparison | Existing, paid |
| Claude + Dashboards | The AI and dashboards front end | Existing; plan details unverified |
| GitHub (private repo) | Code and notes | Free |

## What you have to set up
- **Snowflake key** for Cube. Needs an admin: your roles can't attach a key to your own user. Prefer a read-only service user (e.g. `CUBE_SVC` with `AR_PROD_ALL_R`).
- **`.env`** in `cube-claude-lab/` (copy `.env.example`, add a generated API secret).
- **Cube Cloud:** click Create Deployment to see plan limits and data sources (optional).
- **Question set:** 10-15 questions (some clean, some ambiguous, some out of scope) with expected answers.

## Manual steps done so far
- Signed in to `willyc.omniapp.co` in the browser for the Omni CLI (OAuth).
- Installed Docker Desktop (drag to Applications, approved admin prompt).
- Tried to attach a key to your Snowflake user in Snowsight. Failed: no admin role.
- Created a Cube Cloud account and opened its MCP Server page.

## Man hours (estimates; replace with measured numbers)
| Phase | Done so far | Remaining |
|---|---|---|
| Align Omni and Snowflake data | about 1 h | none |
| Build and compile Cube model | about 1 h (Claude-built) | none |
| Docker, Python, Cube Cloud setup | about 1 h (you) | none |
| Snowflake access (admin wait) | about 0.5 h | about 0.5 h plus wait time |
| Golden tests, connect Claude | none | 1-2 h |
| Question set and scoring | none | 3-4 h |
| Definition-change test (both tools) | none | 1-2 h |
| Findings write-up | none | 2-3 h |

Track real hours in this table as you go. The data team will ask what the build and upkeep cost.

## Files
- `cube-claude-lab/`: Cube model (`model/`), MCP wrapper (`mcp/`), tests (`tests/`), `docker-compose.yml`
- `omni-source/`: the Omni topic the Cube model was converted from
- `Cube Core + Claude_ hands-on lab.md`: original lab guide

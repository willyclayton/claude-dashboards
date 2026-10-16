# Claude Dashboards: semantic layer experiments

**Question:** can Claude + Cube (free, open-source semantic layer) do what Omni's semantic layer does, and where does Omni still earn its keep?

## Status at a glance (2026-10-16)

| | |
|---|---|
| Cube model on live Snowflake | Done, 6/6 golden tests pass |
| Claude Desktop → Cube over MCP | Working |
| First Claude Dashboard on Cube | Built; tiles confirmed to go through Cube |
| Head-to-head scenarios vs Omni | Not started (5 defined) |
| Plan 2 (Claude improves Omni via Git) | Planned, not started |

## Do next

1. Ask the data team if `SALE_PRICE * 0.5` is intentional.
2. Fix the margin basis bug (average margin $24.18 is higher than average price $23.19 because only price is halved).
3. Write the 10-15 question set, then run the five scenarios.

## Where everything is

| I want to… | Go to |
|---|---|
| See every task and its status | [docs/Project Tracker.csv](docs/Project%20Tracker.csv) |
| Read what we learned and the gotchas | [docs/Learnings.md](docs/Learnings.md) |
| Understand the plan, evidence and scorecard | [Plan 1/PLAN.md](Plan%201/PLAN.md) |
| See the Cube vs Omni scenarios | [Plan 1/PLAN.md](Plan%201/PLAN.md), section "Scenarios to test" |
| Learn Docker and Cube basics | [docs/Docker and Cube 101.md](docs/Docker%20and%20Cube%20101.md) |
| See the Plan 2 idea | [Plan 2/PLAN.md](Plan%202/PLAN.md) |
| See screenshots of progress | [pics_along_the_way/](pics_along_the_way/) |
| Browse the Cube model and tests | `Plan 1/cube-claude-lab/` |

## Run it

```bash
cd "Plan 1/cube-claude-lab"
docker compose up -d                    # Cube at http://localhost:4000
python tests/run_golden.py              # accuracy tests (needs .env loaded)
```

Claude Desktop uses a copy of the MCP server in `~/.cube-mcp/` (see Learnings for why). Fully quit and reopen Desktop after changing its config.

## Repo layout

```
README.md                  this page: status, next steps, links
docs/                      learnings, tracker, Docker/Cube 101
pics_along_the_way/        dated screenshots
Plan 1/                    Claude + Cube vs Omni (PLAN.md, lab, Omni source)
Plan 2/                    Claude -> Git -> Omni (PLAN.md)
```

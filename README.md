# Claude Dashboards: semantic layer experiments

**Question:** can Claude + Cube (free, open-source semantic layer) do what Omni's semantic layer does, and where does Omni still earn its keep?

## Status at a glance (2026-10-20)

| | |
|---|---|
| Cube model on live Snowflake | Done, 6/6 golden tests pass |
| Claude Desktop → Cube over MCP | Working |
| First Claude Dashboard on Cube | Built; tiles go through Cube |
| 4-route bake-off (10 questions x 3 runs) | Done: Cube 100%, Omni 93% pointed at the Sales topic / 37% unguided, Claude alone 60% |
| Security and metric-change tests | Done for Cube and Snowflake; Omni not yet tested |
| Plan 2 (Claude improves Omni via Git) | Planned, not started |

## Do next

1. Ask the data team: is `SALE_PRICE * 0.5` intended, which Omni topic is authoritative for revenue (two disagree 2x), and what is the return-rate denominator?
2. Decide the `avg_margin` basis (average margin $24.18 is higher than average price $23.19).
3. Close the open gaps in the findings: Omni restricted-user test, Omni business-user metric test, 25-50 questions, two independent scorers, hours and cost.

## Where everything is

| I want to… | Go to |
|---|---|
| **Read the test results and evidence** | [docs/plan-1/findings.md](docs/plan-1/findings.md) |
| See the scoring matrix (8 criteria x 4 routes) | [docs/plan-1/scoring-matrix.md](docs/plan-1/scoring-matrix.md) |
| Open the filled-in grid and the **weighted score** (spreadsheet, editable weights) | [docs/plan-1/success-criteria-grid.xlsx](docs/plan-1/success-criteria-grid.xlsx) |
| See the success criteria and North Star | [docs/plan-1/success-criteria.md](docs/plan-1/success-criteria.md) |
| Read the Plan 1 plan, progress and risks | [docs/plan-1/plan.md](docs/plan-1/plan.md) |
| See every task and its status | [docs/project-tracker.csv](docs/project-tracker.csv) |
| Read what we learned and the gotchas | [docs/learnings.md](docs/learnings.md) |
| Run the Cube demo (build steps, 4 pitfalls, 30-min run-of-show, gap register) | [docs/plan-1/cube-demo-guide.md](docs/plan-1/cube-demo-guide.md) |
| See 40 more criteria with test status | [docs/plan-1/additional-criteria.md](docs/plan-1/additional-criteria.md) |
| Compare every Omni attribute with Cube | [docs/reference/omni-vs-cube-attributes.md](docs/reference/omni-vs-cube-attributes.md) |
| Learn Docker and Cube basics | [docs/reference/docker-and-cube-101.md](docs/reference/docker-and-cube-101.md) |
| Read the original Cube lab guide | [docs/reference/cube-core-claude-hands-on-lab.md](docs/reference/cube-core-claude-hands-on-lab.md) |
| See the Plan 2 idea | [docs/plan-2/plan.md](docs/plan-2/plan.md) |
| See screenshots of progress | [pics_along_the_way/](pics_along_the_way/) |

## Run it

```bash
cd "Plan 1/cube-claude-lab"
docker compose up -d                    # Cube at http://localhost:4000
set -a && . ./.env && set +a
.venv/bin/python tests/run_golden.py    # accuracy tests against Snowflake
```

Claude Desktop uses a copy of the MCP server in `~/.cube-mcp/` (macOS blocks Desktop-launched processes from reading `~/Desktop`; see [learnings](docs/learnings.md)). Fully quit and reopen Desktop after changing its config. To re-run the bake-off, see "Reproduce" in the [findings](docs/plan-1/findings.md).

## Repo layout

```
README.md                  this page: status, next steps, links
docs/
  plan-1/                  plan, findings, scoring matrix, success criteria
  plan-2/                  Plan 2 plan
  reference/               101 guide, Omni vs Cube attributes, original lab guide
  learnings.md             running log of gotchas and lessons
  project-tracker.csv      every task, status, owner, evidence
Plan 1/                    code (kept in place: Docker and the venv depend on this path)
  cube-claude-lab/         Cube model, docker-compose, MCP wrapper, golden tests
  bakeoff/                 bake-off, security and metric-change scripts and results
  omni-source/             the Omni topic the Cube model was ported from
pics_along_the_way/        dated screenshots
```

# Learnings (Plan 1, from 2026-10-26)

What we learned running Snowflake → Cube → Claude, written so you can say it out loud. Earlier learnings (before the restart) are in [../old/docs/learnings.md](../old/docs/learnings.md). How to run and fix things: [cube/CUBE-HELPER.md](cube/CUBE-HELPER.md).

## 1. Claude Dashboards on a self-hosted semantic layer (the big one)

**The short version to say:** "Claude can query our self-hosted Cube live in chat. A Claude Dashboard can't, unless an org admin adds Cube as a connector and someone hosts it publicly with real authentication. An individual SE can't do either."

**Why the chat works but the dashboard doesn't:**

| | Claude chat (Desktop) | Claude Dashboard |
|---|---|---|
| Who makes the Cube call | Claude Desktop, on your Mac | The dashboard page, through Claude's connector service on the internet |
| What it can call | Local servers in Desktop's config ("Desktop · Local dev") and account connectors | Only connectors on your Claude account, by name |
| Can it reach `localhost:4000`? | Yes (your Mac calling your Mac) | No: the service can't reach your laptop, and the page can't call web addresses |
| Our `cube` | Local server in `claude_desktop_config.json` → works | Not on the account → every source "absent: couldn't load from cube" |

**What we verified, not guessed (2026-10-28):**
- The dashboard type's own rule: a tool that "exists only in your session (a server on their computer…)": "A dashboard can't call it. Use a file."
- The new dashboard was open in Desktop while the local `cube` was running and answering the chat beside it; the dashboard still reported `cube` absent.
- Cube is not in Claude's connector directory, so there is no ready-made connector to add.
- Adding a custom connector is greyed out: only an organization owner can add one. (Our "Omni Playground" connector shows that this is how connectors get added.)
- Adrien hit the same wall on the dbt path ("needing a Claude admin for custom connectors").

**What the Oct 16 dashboard really was:** 6 of its 7 sources are files Claude saved on 2026-10-16 at 22:40 UTC. Each came from a real `cube` query in chat and keeps that query beside its rows, so clicking a number showed the Cube query and results. The numbers were real Cube data, frozen at build time. Desktop's logs show no Cube calls from 10-20 to 10-26. The one live query added later (`kpis`, 10-26) never loaded.

**The live Cube UI people remember is the Cube Playground** (`http://localhost:4000`, only in dev mode). It builds queries, runs them live against Snowflake, and shows results and SQL. It is Cube's own page in a browser tab, not a Claude Dashboard, and a dashboard can't be pointed at it or reliably embed it.

**What it would take to make a dashboard live:** an org owner adds a custom connector `cube`; the MCP endpoint is public over HTTPS (we built a tunnel that works); it has real authentication (a tunnel's secret URL is not auth); it stays up 24/7 (not a laptop, and a quick-tunnel URL changes on every restart); every viewer needs the connector. Or pay for Cube Cloud. That's the build-versus-buy point: Omni is already a hosted connector that dashboards can use.

**What you can show live without an admin:** Claude chat answering from Cube (every question is a fresh query), and the Cube Playground for the query and results. A dashboard can only show a snapshot (data saved into it), clearly labelled.

## 2. Accuracy and consistency (Adrien's 10 questions)

- **Curated Cube model** (definitions in measures, descriptions): 30 of 30 over 3 runs, identical headlines every run. Adrien's dbt baseline: 28 of 30 (both misses Q7, repeat customers).
- **Bare Cube model** (raw measures, no descriptions): 5 of 10 strict every run (7 with partials). Consistently wrong the same way: revenue included cancelled and returned items; AOV and category/traffic figures inherited that; repeat share was an honest "can't".
- **Lesson:** consistency can hide wrongness. A model with no definitions gave the same wrong revenue three times. The fix is a definition in the measure, not better prompting.
- **Lesson:** where a field didn't exist, Claude said so instead of inventing (repeat share, emails, headcount). It even refused to pass off "orders per customer" as a repeat share.
- **Q4 trap:** 52.2% margin came out right on the wrong basis (all statuses). Score it as a coincidence, not understanding.
- Round 1 fix (net revenue, AOV) is in; the "after" runs are pending. Details: [eval/adrien-question-set/](eval/adrien-question-set/README.md).

## 3. Boundary and permissions

- **Two layers:** the Snowflake role limits what Cube can ever read (6 tables; decoys, `ACME_CO_DEV`, `WORKDAY`, `ANALYTICS_PROD` and the dbt marts denied, with captured output). The Cube model limits what Claude can ask (only the `sales` view; raw cubes rejected; no personal columns in the model).
- Q9 (emails) and Q10 (headcount) refused in every run, with no query attempted.
- The PII boundary is in the model (columns never modeled), not in Claude's judgment.
- A role-restricted Snowflake token session can't run `use role` or `use secondary roles`; `current_secondary_roles()` is empty.

## 4. Operating it (the "duct tape" list)

- Cube reads the YAML once in production mode: restart after every model edit. In dev mode it reloads itself, but dev mode turns off Cube's token check.
- `docker compose restart` does not re-read `.env`; use `docker compose up -d --force-recreate`.
- `docker compose` only works from the folder with `docker-compose.yml`.
- Claude Desktop reads its MCP config only at launch (Cmd+Q, reopen), and can't run servers from `~/Desktop` (macOS privacy), so the wrapper lives in `~/.cube-mcp/`.
- Snowsight's Run executes only the statement under the cursor; select all, then Cmd+Enter.
- Secrets leaked into chats three ways: a pasted token, a pasted `docker run` command, and a screenshot of Desktop's Developer settings. Rotate after demos.
- A public tunnel started on 10-26 was still running two days later. Long-running pieces get forgotten.
- Effort since the restart: about 3 to 4 logged hours plus waits (admin for `ACME_ADMIN`). See [effort-log.csv](effort-log.csv).

## 5. Lines for the demo

1. "Up to here it works great: ask Claude a question, it hits Cube, Cube hits Snowflake, the answer is right and the same every time."
2. "Here's the query Cube actually ran" (Playground).
3. "From here it doesn't: the moment you want a shareable dashboard, you need an org admin, a hosted endpoint, real auth and someone to keep it up. We're one SE with a laptop."
4. "And everything here was free. The first paid piece (Cube Cloud, dbt semantic layer) is where the 'might as well buy Omni' argument starts."

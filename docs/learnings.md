# Learnings

Running log of what we learned building the Claude + Cube + Claude Dashboards setup. Newest first within each section. Last updated 2026-10-16.

## Connecting Claude Desktop to Cube (MCP)

1. **Claude Desktop reads MCP config only at launch.** Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (`mcpServers`), then fully quit with `Cmd+Q` and reopen. Closing the window isn't enough.
2. **macOS blocks Desktop-launched processes from `~/Desktop`.** The first run failed with `PermissionError: Operation not permitted: .../.venv/pyvenv.cfg` (log: `~/Library/Logs/Claude/mcp-server-cube.log`). Python died before the server started.
   **Fix:** run the server from outside protected folders. It now lives in `~/.cube-mcp/` with its own venv. The repo copy is the source; re-copy `mcp/server.py` after edits.
3. **Pin `mcp` below 2.** A fresh venv pulled `mcp` 2.x, which renamed `FastMCP` (`ModuleNotFoundError: mcp.server.fastmcp`). `requirements.txt` now says `mcp>=1.9,<2`.
4. **The "Do Not Allow" click was a red herring.** The real causes were items 2 and 3. Read the log before guessing at permissions.
5. **Use stdio transport for Desktop** (`MCP_TRANSPORT=stdio`). No tunnel or public URL is needed, because Desktop launches the server locally. This makes the Cloudflare tunnel in the plan unnecessary for Desktop.
6. **The API secret sits in plaintext in the Desktop config.** Keep that file private. A backup of the original is next to it (`.bak`).
7. **Cube must be running** (`docker compose up -d`, port 4000) for the MCP tools to return data.

## What the end-to-end test showed

- Claude Desktop called `describe_data`, then `query_data`. Cube generated the SQL, Snowflake ran it, and rows plus the SQL came back.
- Revenue by month, Apr-Sep 2026 (Cancelled and Returned excluded): $206,692.47, $210,905.33, $203,150.93, $217,483.48, $239,566.56, $241,366.85.
- **The exclusion came from `ai_context`.** The view's guidance says to exclude cancelled and returned orders, and Claude applied it as a `STATUS NOT IN` filter. The `total_revenue` measure itself includes all statuses, so the rule lives in prose, not in the measure. See Plan 1 finding 2.
- **Revenue is half the raw table.** The SQL contains `SALE_PRICE * 0.5`. It comes from the Omni topic (`analytics_prod_ecomm__sales.topic`) and is ported unchanged. Still unconfirmed with the data team whether it's intentional.
- The numbers have not yet been re-checked against `tests/run_golden.py` in this session.

## Claude Dashboards (beta)

- **Chat-driven only.** There's no editor. Include the phrase "Claude Dashboard" (or similar) in the prompt for it to build one. It is not an artifact, so artifact-style prompts are the wrong approach.
- **It can use the local `cube` MCP tools.** The first build, "Ecommerce Sales: Last 6 Months", created a dashboard shell, read its own design and data-loader references, then ran the KPI and chart queries as "Query data" calls against the cube connector.
- **Confirmed: tiles go through Cube.** The finished dashboard's side panel shows `cube · query_data` with the `sales.*` measures, the status filter and the date range. The category and country fields exist (`sales.products_category` is used).
- **To see the SQL:** each tile has an expandable "SQL" link (the five KPI tiles share one "SQL behind the five figures"). The side panel shows the Cube JSON query, not SQL.
- **It surfaces model problems.** It flagged that average sale price uses the halved price ($23.19) while average margin uses the unhalved `MARGIN` column ($24.18), so margin exceeds price. It also showed only USA and UK after exclusions.
- Screenshot: `pics_along_the_way/2026-10-16-claude-dashboard-first-build.png`.

## Workflow and tooling

- This Claude Code session can't see or drive Claude Desktop. Anything inside Desktop (including Claude Dashboards) has to be done by pasting a prompt there and relaying the result.
- `ListAgents` showed no other Claude Code sessions, so there was nothing to close. The Claude desktop app is a separate process.
- VS Code opens `.md` files as source by default. To render them every time, set `"workbench.editorAssociations": {"*.md": "vscode.markdown.preview.editor"}` (VS Code about 1.98+).
- Docker 101 and Cube 101 primer: `docs/reference/docker-and-cube-101.md`.

## Bake-off lessons (2026-10-20; full detail in `docs/plan-1/findings.md`)

- **Consistency can hide wrongness.** Claude on its own gave the same wrong revenue every run (100% consistent, 0% right on definition questions).
- **Omni's risk is topic choice, not arithmetic.** Unguided, its agent used a topic where revenue isn't halved (36.7% match); pointed at the Sales topic it matched 93.3%. Two topics over one table disagreed by 2x.
- **Headless runs are a usable test rig.** `claude -p` with `--allowedTools` limits Claude to one route's tools and returns cost, turns and time per answer in JSON.
- **Parallel Omni calls hit HTTP 429.** Use 1-2 workers.
- **`CUBEJS_DEV_MODE=true` disables auth** (no token and forged tokens work). Production mode needs `CUBEJS_CACHE_AND_QUEUE_DRIVER=memory` (or Cube Store) to run; with it, auth is enforced.
- **A token with no `country` claim is unrestricted** in our `queryRewrite`, and the MCP wrapper mints such tokens. Per-user identity must be added deliberately.
- **Live data drifts.** Distinct orders were 252,701 on 10/16 and 254,271 on 10/20; compute the answer key on the day of the run.

## Context gap: Cube vs Omni

Full, verified attribute-by-attribute table: [omni-vs-cube-attributes.md](reference/omni-vs-cube-attributes.md). In short: Cube matches Omni on structure (SQL, joins, descriptions, access, caching) and exceeds it on performance. The gap is the AI-facing layer: `synonyms`, `all_values`, `sample_values`, `sample_queries`, `ai_fields` and `ai_chat_topics` have no real Cube equivalent. Cube's docs name `meta.ai_context` for AI agents, but Core's API doesn't act on it, so our MCP wrapper reads `meta` itself. The "exclude cancelled and returned" rule is advisory text in both tools unless built into the measure (view `default_filters` or a measure `filters` block does that in Cube; tested).

## Carried over from Plan 1 (earlier learnings)

- A Snowflake PAT replaces the admin-gated key-pair for a lab, but role scoping on the token is the thing to get right (`AR_PROD_ALL_R` has no access to `ECOMM`; `DBT_DEMO_ROLE` does).
- Omni's simple `ecommerce_sales` topic is bare; the prod topics built from Snowflake semantic views carry the real definitions.

## Open questions

1. Is `SALE_PRICE * 0.5` intentional? (Ask the data team.)
2. ~~Do Claude Dashboards tiles go through Cube?~~ Yes (answered 2026-10-16).
3. Should the "exclude cancelled/returned" rule move from `ai_context` into a measure or segment so it's enforced, not advisory?
4. Do the Desktop numbers match the golden tests?
5. What is the correct basis for `avg_margin` (halved or unhalved)?
6. Why only USA and UK after exclusions: expected for this dataset?

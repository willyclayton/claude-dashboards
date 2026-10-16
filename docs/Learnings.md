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
- **Open question (Plan 1 step 6):** whether the finished dashboard's tiles keep going through Cube, or write their own SQL. The in-progress run suggests Cube, but the finished dashboard has not been checked.
- **Not yet confirmed:** that the view has product category and country fields (the prompt asked for both).

## Workflow and tooling

- This Claude Code session can't see or drive Claude Desktop. Anything inside Desktop (including Claude Dashboards) has to be done by pasting a prompt there and relaying the result.
- `ListAgents` showed no other Claude Code sessions, so there was nothing to close. The Claude desktop app is a separate process.
- VS Code opens `.md` files as source by default. To render them every time, set `"workbench.editorAssociations": {"*.md": "vscode.markdown.preview.editor"}` (VS Code about 1.98+).
- Docker 101 and Cube 101 primer: `docs/Docker and Cube 101.md`.

## Carried over from Plan 1 (earlier learnings)

- A Snowflake PAT replaces the admin-gated key-pair for a lab, but role scoping on the token is the thing to get right (`AR_PROD_ALL_R` has no access to `ECOMM`; `DBT_DEMO_ROLE` does).
- Omni's simple `ecommerce_sales` topic is bare; the prod topics built from Snowflake semantic views carry the real definitions.

## Open questions

1. Is `SALE_PRICE * 0.5` intentional? (Ask the data team.)
2. Do Claude Dashboards tiles go through Cube or write their own SQL?
3. Should the "exclude cancelled/returned" rule move from `ai_context` into a measure or segment so it's enforced, not advisory?
4. Do the Desktop numbers match the golden tests?

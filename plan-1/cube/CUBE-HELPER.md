# Cube helper: start, check, fix

Everything you need to run Snowflake → Cube → Claude yourself, and what to do when it breaks. Written 2026-10-28.

All commands assume you start in the Cube folder:

```bash
cd "/Users/will/Desktop/Claude/Claude Dashboards/plan-1/cube"
```

## 1. The pieces (left to right)

```
Claude Desktop chat
   │  local MCP server named "cube" in Claude Desktop's config      (shows in Connectors as "cube · Desktop · Local dev")
   ▼
MCP wrapper               2 tools: describe_data, query_data       (~/.cube-mcp/server.py, started by Desktop over stdio)
   ▼
Cube Core in Docker       the semantic layer: model/*.yml          (localhost:4000)
   ▼
Snowflake                 ACME_CO.SHOPIFY_ECOMM, role ACME_CUBE_READER (read-only, 6 tables)
```

**The key constraint (2026-10-28):** you cannot add a custom connector in Settings > Connectors; it is greyed out and only an organization owner can add one for the team. So the only route open to you is the **local** server above. It works for **chats in Claude Desktop only**. A Claude Dashboard cannot use it, because a dashboard runs in the browser and only calls connectors on the account. See section 2b for dashboards.

| Piece | Where it lives | Holds a secret? |
|---|---|---|
| Snowflake role | Created by `../snowflake/01_create_cube_role.sql` (run as `ACME_ADMIN`) | No |
| Snowflake token (PAT) | `.env` → `CUBEJS_DB_PASS` | **Yes** |
| Cube config | `.env`, `docker-compose.yml` | `CUBEJS_API_SECRET` **yes** |
| Cube model | `model/cubes/*.yml`, `model/views/sales.yml` (curated version archived in `model-v1-curated/`) | No |
| MCP wrapper | `mcp/server.py` (source), `~/.cube-mcp/server.py` (running copy), venv in `~/.cube-mcp/.venv` | Reads `CUBEJS_API_SECRET` |
| Desktop config entry | `~/Library/Application Support/Claude/claude_desktop_config.json` → `mcpServers.cube` (also: Settings > Developer > Edit config) | `CUBEJS_API_SECRET` **yes** (must match `.env`) |
| Tunnel (parked) | `mcp/start_public_tunnel.sh`, `~/.cube-mcp/stop_public_tunnel.sh` | Only useful if an org owner adds a custom connector |

`.env` is gitignored. Never paste it, the Desktop config, the Docker run command (`--env=` lines), or a tunnel URL into a chat or a doc.

## 2. Start everything (after a reboot, or any time it's down)

1. **Docker Desktop** is open.
2. **Cube:** `docker compose up -d`, then `curl localhost:4000/readyz` should say `HEALTH`.
3. **Claude Desktop:** fully quit (Cmd+Q) and reopen. Desktop starts the local `cube` server itself; there is nothing else to start.
4. **Use it:** new chat; check the `cube` connector is on and others are off for test runs.

What the config entry looks like (secret redacted). To recreate it: Settings > Developer > Edit config, add this inside `"mcpServers"`, paste the secret from `.env`, then Cmd+Q and reopen:

```json
"cube": {
  "command": "/Users/will/.cube-mcp/.venv/bin/python",
  "args": ["/Users/will/.cube-mcp/server.py"],
  "env": { "CUBEJS_API_SECRET": "<same value as CUBEJS_API_SECRET in .env>", "MCP_TRANSPORT": "stdio" }
}
```

The server and its venv live in `~/.cube-mcp/`, not in the repo, because macOS blocks Desktop-launched processes from reading `~/Desktop`.

## 2b. Dashboards without a custom connector

**What the 2026-10-16 dashboard actually was** (checked 2026-10-28 by reading its sources; "Ecommerce sales: last 6 months", claude.ai/artifact/NAXXVMBqbm2Gd5aqFfADxu):
- 6 of its 7 sources are **files saved by Claude on 2026-10-16 at 22:40 UTC**. Each file was produced by a real `cube` → `query_data` call in a Desktop chat (the request is stored beside it), so the numbers were real Cube data, but frozen at that moment.
- The only live query, `kpis`, was switched on 2026-10-26; its last load says `absent: "Still couldn't load from cube."`
- Claude Desktop's logs show the local `cube` received tool calls on 10-16 and 10-19, then none until 10-27: nothing re-queried Cube in between.
- The dashboard type's own rule: a tool that "exists only in your session (a server on their computer…)": "A dashboard can't call it. Use a file."

So the dashboard you saw a week ago showed real Cube numbers from files saved at build time. The new dashboard fails because it was built with live queries instead of saved files. How the local `cube` exists without admin rights: it is a local MCP server in Desktop's config file (created 2026-10-16; the original backup is `claude_desktop_config.json.bak`, dated 10-16 17:24). Local servers aren't covered by the "custom connector" permission; nothing about your access changed.

| Option | Live? | Who | Effort |
|---|---|---|---|
| **Snapshot:** in a Desktop chat with `cube` on, ask Claude to run the dashboard's queries through `cube` and attach the results to the dashboard as data files; label it "fixed copy as of <date>" | No | You | Minutes |
| **Refresh on request:** same chat, later: "re-run the dashboard's queries through cube and replace the data files" | Manually, when asked | You | Minutes each time |
| **Real live connector:** an org owner adds a custom connector `cube` (URL from `mcp/start_public_tunnel.sh`, or a hosted endpoint with real auth) | Yes | Org owner, plus hosting | Admin request + the hosting pain in section 8 |

Prompt for the snapshot:

> Build a Claude Dashboard of our ecommerce sales. Get every number by querying the `cube` connector now (use `net_revenue`, `avg_order_value` and `order_count` from the `sales` view); don't type in numbers. Store the query results as data files in the dashboard, not as live queries, because the dashboard can't reach `cube`. Put "Snapshot from Cube, <today's date>" in the title area.

## 2c. Cube Playground (the UI at http://localhost:4000)

The Playground only appears in **dev mode** (`CUBEJS_DEV_MODE=true` in `.env`). Production mode shows a single line, "Cube server is running in production mode". Since 2026-10-28 the project runs in dev mode with port 4000 bound to `127.0.0.1` only (`docker-compose.yml`), because dev mode turns off Cube's token check. In dev mode Cube also reloads the YAML by itself, so a model edit needs no restart. To go back to production mode: set `CUBEJS_DEV_MODE=false` and `docker compose up -d --force-recreate`.

A Claude Dashboard cannot be pointed at `localhost:4000`: its queries go through Claude's connector service, which cannot reach your laptop, and the page cannot call arbitrary URLs.

## 3. Which command after which change

| You changed | Do this | Why |
|---|---|---|
| A YAML file in `model/` | `docker compose restart cube` (5 s), then a **new** Claude chat | Cube loads the model once at startup in production mode |
| `.env` (role, token, secret) | `docker compose up -d --force-recreate` | `restart` reuses the old environment; only recreate re-reads `.env` |
| `CUBEJS_API_SECRET` | recreate Cube (above), put the same value in the Desktop config, Cmd+Q and reopen Desktop | The wrapper signs its Cube requests with that secret |
| `mcp/server.py` | `cp mcp/server.py ~/.cube-mcp/server.py`, then Cmd+Q and reopen Desktop | Desktop runs the copy in `~/.cube-mcp/` |
| Nothing, it just stopped | Section 2 from step 2 | Laptop slept, Docker quit, or the tunnel died |

`docker compose` only works from the Cube folder ("no configuration file provided" means you're in the wrong folder).

## 4. Health checks (run these first when something looks wrong)

```bash
curl -s localhost:4000/readyz                               # Cube up? → {"health":"HEALTH"}
docker compose logs --tail 30 cube                          # Cube errors, YAML mistakes, Snowflake auth errors
tail -30 ~/Library/Logs/Claude/mcp-server-cube.log         # Desktop's log for the local cube server
set -a && . ./.env && set +a
.venv/bin/python tests/boundary.py                          # Cube auth + no PII + hidden cubes
.venv/bin/python tests/access_check.py                      # Snowflake: what the role can and can't read
```


## 5. Symptom → fix

| Symptom | Cause | Fix |
|---|---|---|
| Dashboard: "couldn't load from `cube`", sources "absent", or banner "Finish connecting cube" | Dashboards only use account connectors; ours is local, and adding a custom one needs an org owner | Snapshot route (section 2b). Not fixable by retrying |
| Chat can query Cube but the dashboard can't | Same: chats use the local Desktop server, dashboards can't | Section 2b |
| Settings > Connectors > Add custom connector is greyed out | Org policy: only an organization owner can add custom connectors | Ask the org owner, or use section 2b |
| The `cube` row says "Desktop · Local dev" and can't be edited | It comes from the Desktop config file, not Settings | Edit it in Settings > Developer > Edit config, then Cmd+Q and reopen |
| Chats suddenly get 403 / "Authorization" errors from Cube | `CUBEJS_API_SECRET` in the Desktop config differs from `.env` (e.g. after a rotation) | Make them match, Cmd+Q and reopen Desktop |
| `cube` tools missing in a chat | Desktop not restarted after a config change, or the config JSON is invalid | Cmd+Q and reopen; check `~/Library/Logs/Claude/mcp-server-cube.log` |
| Edited a description/metric, Claude still shows the old one | Cube not restarted, or old chat | `docker compose restart cube`, new chat |
| Changed `.env`, nothing changed | Used `restart` | `docker compose up -d --force-recreate` |
| Cube error "Database 'ACME_CO' does not exist or not authorized … DBT_DEMO_ROLE" | Old env still loaded | Recreate (above); check `.env` role is `ACME_CUBE_READER` |
| Cube error about Snowflake auth / token | Token revoked or expired | New PAT in Snowsight (section 6), put in `.env`, recreate |
| Connector URL returns 404 | Wrong or old secret path; tunnel restarted | Rerun start script, paste the new URL |
| HTTP 421 from the wrapper | Wrapper started without the tunnel's hostname allowed | Always start with the script (it starts the tunnel first, then the wrapper) |
| Tunnel URL doesn't resolve | Tunnel died or laptop slept | Rerun start script, update connector |
| Snowsight: "Role … does not exist" while running a script | Snowsight's Run only ran the line your cursor was on | Select all (Cmd+A), then Cmd+Enter |
| Python Snowflake check: "Current session is restricted. USE ROLE not allowed" | Expected for a role-restricted token | Nothing to fix; don't run `use role`/`use secondary roles` in token sessions |

## 6. Rotate secrets

- **Snowflake token:** Snowsight > your profile > Authentication > Programmatic access tokens. Revoke the old one, generate a new one restricted to `ACME_CUBE_READER`. Put it in `.env` as `CUBEJS_DB_PASS=…`, then `docker compose up -d --force-recreate`. **Still to do**: the current token was pasted in chat.
- **Cube API secret:** `openssl rand -hex 32` → `.env` `CUBEJS_API_SECRET=…` → recreate Cube → same value in the Desktop config → Cmd+Q and reopen Desktop. Done 2026-10-28.

## 7. What was done, in order (2026-10-26 to 10-28)

1. **Snowflake.** Got `ACME_ADMIN` (via ATX). Created `ACME_CUBE_READER` with SELECT on the six brief tables only (`../snowflake/01_create_cube_role.sql`). Created a PAT restricted to that role. Verified the six tables are readable and the decoys, `ACME_CO_DEV`, `WORKDAY`, `ANALYTICS_PROD` and Adrien's marts are not (`../snowflake/access-results.md`).
2. **Cube.** New project in this folder: Docker Compose, production mode (auth on), Snowflake via `.env`. Built the curated model (net revenue, AOV, margin, return rate, repeat share; no personal columns; cubes hidden, one `sales` view). Q1–Q8 matched Adrien's expected answers. Archived it to `model-v1-curated/` and replaced it with a deliberately bare model for the before/after experiment, then added round-1 definitions (`CHANGES.md`).
3. **Claude, local (2026-10-16 to 10-28).** The first connection was a *local* MCP server in Claude Desktop's config (`mcpServers.cube`, stdio, running `~/.cube-mcp/server.py`). It worked in Desktop chats, which is how the question runs were done, but dashboards can't use it.
4. **Tried remote (2026-10-28), dead end.** Found an old tunnel and wrapper from 10-26 still running and stopped them. Wrote new tunnel scripts in `mcp/`, rotated the Cube API secret, and verified a public endpoint end to end. Then hit the real blocker: custom connectors are greyed out and need an organization owner. Stopped the tunnel. (A mistake on the way: the local `cube` entry was removed and then restored, with the new secret.)
5. **Where it is now.** Local `cube` in the Desktop config with the rotated secret, verified by running the wrapper as Desktop does (net revenue 12,849,504.66, 283,894 orders). Dashboards: snapshot route only (section 2b).
6. **Left for you.** Cmd+Q and reopen Claude Desktop (the running `cube` processes still hold the old secret and will get 403 until then). Rotate the Snowflake token. Decide whether to ask the org owner for a custom connector.

## 8. Honest limits of this setup

- **A live Claude Dashboard on Cube needs a Claude organization owner** to add a custom connector. An individual SE can't do it. (Adrien hit the same wall on the dbt path and used a local `mcp-remote` bridge as a stand-in.)
- Even with the owner's help: the endpoint must be public, need real auth (a quick tunnel has none and changes URL on every restart), stay up 24/7 (not a laptop), and every viewer needs the connector.
- Fixing that means hosting, a process supervisor, and OAuth, or paying for Cube Cloud. That is the "what it takes" part of the story.

## 9. How to explain it (talking points)

- **"Why does the chat work but the dashboard doesn't?"** The chat's Cube call is made by Claude Desktop on my Mac. A dashboard's calls go through Claude's connector service, which only knows connectors on the account and can't reach my laptop. Our Cube is a local server, so only the chat can use it.
- **"Can't you point the dashboard at localhost:4000?"** No. Dashboard tiles only get data through account connectors; there's no setting for a URL, and the sandboxed page can't reach your machine.
- **"But I saw a live Cube dashboard before."** The 10-16 dashboard showed real Cube results with their queries, saved into it when it was built. The live UI with queries and results was the Cube Playground at localhost:4000 (dev mode).
- **"So what would make it live?"** An org owner adds a `cube` custom connector, plus a public HTTPS endpoint with real auth that stays up. We proved the endpoint works through a tunnel; the admin step is the blocker for an individual.
- **"What can you show live today?"** Claude chat on Cube, and the Playground. Dashboards: a labelled snapshot.

More context and the accuracy results: [../learnings.md](../learnings.md).

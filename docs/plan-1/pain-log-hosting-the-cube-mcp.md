# Pain log: making a Claude Dashboard read Cube live

*Started 2026-10-26. Goal: the "Ecommerce sales: last 6 months" Claude Dashboard loads its numbers live from our Cube, for anyone who opens it. This is the cost of the "headless layer you host yourself" path, in the order we hit it. Companion to [findings.md](findings.md) section 14 and [cube-vs-omni-demo-paths.md](cube-vs-omni-demo-paths.md) path 3.*

## The short version

The Cube MCP server worked in Claude Desktop within one session. Making a **dashboard** use it live is a separate project: it needs a public HTTPS endpoint, authentication nobody has built, a connector added by hand with an exact name, and a laptop that stays awake. Omni's equivalent (Documented) is four steps: add the connector, authorize in Omni, enable it in Claude, ask ([docs](https://docs.omni.co/ai/mcp/claude-desktop)).

## What we found, in order

| # | What happened | Cost | Still painful? |
|---|---|---|---|
| 1 | The dashboard looked live but five of its six sources are **saved files from Oct 16**. Each keeps its Cube query, but nothing re-runs it. The side panel said "This query isn't refreshing automatically" on Oct 16; we only found the reason on Oct 26 by reading the dashboard's sources | 10 days of a stale dashboard that looked fine | Yes: only a small note in the source panel says it is not live; the charts look current |
| 2 | A live query is one tool call the **viewer's page** makes on a connector **the viewer has**, under its name. A server that exists only in Claude Desktop's local config is invisible to it. So a local Cube MCP cannot feed a dashboard, however well it works in chat | Design dead end for the local setup | Yes |
| 3 | The wrapper was binding **`0.0.0.0`**, so it was reachable from the whole network, not just this laptop | One config change, found only while preparing to host | Fixed (`127.0.0.1` default) |
| 4 | There is **no authentication** on the HTTP MCP. We added a secret path (`/<random>/mcp`). That is an unguessable URL, not security: anyone with the link can query | Stopgap only | Yes |
| 5 | **`.env` sets `MCP_PATH=/mcp`**, which silently overrode the new secret path. Our first test "served" the old path and 404'd the new one | Two test runs to find | Fixed (the secret wins) |
| 6 | The sales view exposes **customer email, first and last name, latitude, longitude and zip**. A public endpoint would have published them. We added a blocklist in the wrapper and tested that Claude is refused | A code change plus tests, before anything could be exposed | Yes: a model-level fix (`excludes` or an access policy) is still the better answer |
| 7 | No tunnel tooling: `brew` and `cloudflared` are not installed. We downloaded the `cloudflared` binary from GitHub into its own folder (about 2 s) | Small, but it is software someone must trust and keep updated | Yes |
| 8 | Our own safety layer **blocked starting a public server and tunnel** from the agent session. Correct behavior, and it means a human has to run the launch | A handoff; we wrote `start_public_tunnel.sh` for it | By design |
| 9 | A Cloudflare **quick tunnel's address changes every time it restarts** | The connector must be edited each time | Yes |
| 10 | The wrapper and the tunnel must both **stay running**; closing the laptop or a crash takes the dashboard down for everyone | No supervisor, no alerting | Yes |
| 11 | The connector must be added in claude.ai by hand under **exactly the name `cube`**, or every source breaks. On Team or Enterprise it needs an admin (per the Claude Dashboards agent's own message) | Manual, name-sensitive | Yes |
| 12 | Each **viewer's** query runs on their own connection, so each viewer needs the connector too, while our wrapper has **one shared identity** (no per-user security) | The permission story we already flagged, now blocking sharing | Yes |

## What it looks like today

With the KPI source switched to a live `cube` query and no `cube` connector on claude.ai, the dashboard shows **"1 source failed to load"** and all five KPI tiles read "—", while the charts below still draw from the Oct 16 saved files. A viewer sees a half-working dashboard with no explanation on the page itself ([screenshot](../../pics_along_the_way/2026-10-26-dashboard-kpis-failed-no-cube-connector.png)).

## What a user has to do (the checklist)

1. Keep Docker and Cube running on the laptop.
2. Download a tunnel program and trust it.
3. Make the wrapper safe to expose: localhost bind, secret path, blocklist the personal columns.
4. Start the wrapper.
5. Start the tunnel and copy its address.
6. Build the connector URL: address + secret + path.
7. In claude.ai, add a custom connector named exactly `cube` (admin on Team/Enterprise).
8. Repoint every dashboard source from a saved file to a live `cube` query.
9. Keep all of it running whenever anyone opens the dashboard; redo steps 5-7 after every restart.
10. Tell each viewer to add the same connector.

Roughly ten steps and three long-running pieces (Docker, wrapper, tunnel), against Omni's four documented steps with the connector already hosted.

## What doing it properly would take (not done)

- A **named tunnel** or a hosted wrapper (needs a domain or a cloud account).
- A **process supervisor** (launchd or a container platform), logs and alerts.
- **Authentication in front of the MCP** (OAuth), and per-user tokens passed through to Cube's access policy.
- **Secrets management** for the Cube API secret and the Snowflake token (today in a plaintext `.env` and the Desktop config).
- Or **Cube Cloud**: the pricing page lists a hosted MCP server on the Free plan ([cube.dev/pricing](https://cube.dev/pricing)). Not tried; it would trade this pain for a vendor and a bill.

## How long it took

Measured: the tunnel binary downloaded in about 2 seconds. Everything else was not timed with a stopwatch, so we don't quote a total. Fill in when the launch is run:

| Step | Minutes |
|---|---|
| Wrapper hardening and tests (steps 3-6 above) | __ |
| Download and start the tunnel | __ |
| Add the connector in claude.ai | __ |
| Repoint the five saved sources to live queries | __ |
| First live load of the dashboard | __ |

## Run and stop

```bash
bash "Plan 1/cube-claude-lab/mcp/start_public_tunnel.sh"   # prints the connector URL
~/.cube-mcp/stop_public_tunnel.sh                          # take it down
```

While it runs, the printed URL is a public link to the Cube sales view (orders, revenue, countries; customer details blocked).

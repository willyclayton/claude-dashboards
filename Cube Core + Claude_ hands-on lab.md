Cube Core + Claudehands-on lab

0 / 0 tasks

# Give Claude a governed query path, not a blank SQL editor

You'll run Cube Core on your laptop, model a small shop, and let Claude query it through MCP. Plan on a half day the first time through.

**Honest status.** The repo files were syntax-checked but not run against a live Cube instance. Each step lists what you should see and what to check if you don't.

## Your questions, answered

### Do I need Docker?

It's the easiest route, not a hard requirement. One compose file gives you Cube and a sample database with nothing else to install. Without Docker you'd install Node, run Cube from its CLI, and supply your own database; see Cube's install docs for that path.

### Do I need a Cloudflare tunnel?

Only for the last hop. Claude Code and Claude Desktop on your laptop talk to `localhost`. claude.ai, where Dashboards lives, calls connectors from Anthropic's servers, so it needs a public HTTPS URL. Tunnel the MCP wrapper (port 3001), never Cube itself (port 4000), and use fake data until you've added real auth.

### Can I just point Claude at a repo and let it write the SQL?

You can, and it's worth doing as a control. But it's a different thing from Cube. Pick a path below to see the difference.

### Is Cube easy?

Running it is: about 15 minutes. The wrapper is provided. The real effort comes later, from modeling your real warehouse well and wiring per-user auth.

## Two paths

**Recommendation.** Build B. Run A for fifteen minutes as the control, so your three-way comparison has a "Claude plus a context file" column. Step 5 is where you learn whether Dashboards actually routes charts through your tool.

## Lab map

# Cube in ten minutes

Cube is two things at once: a folder of YAML you manage in Git, and a service that turns requests for measures into SQL. Claude needs the service, and the folder is how you control it.

## The pieces

**Core versus Cloud.** Cube Cloud is the paid, hosted product. Compare the feature lists on Cube's site before assuming something you read about ships in Core.

## Query compiler

Pick what you want. The left pane is everything Claude would send; the right is the SQL Cube produces from your model. Claude never writes the right side.

Measures [x] Total revenue [ ] Order count [ ] Refund rate [ ] Avg order value

Group by [x] Region [ ] Segment [ ] Status

Time \


Filter

#### Cube query (what Claude sends)

```

```

#### SQL (what Cube writes, illustrative)

```

```

Real Cube output differs in aliasing and parameters. In step 3 you'll read the real thing in the Playground's SQL tab.

## Why definitions matter

#### Claude alone

"What was revenue last month?"

```
SELECT sum(amount) FROM orders
WHERE created_at >= date_trunc('month', now() - interval '1 month') ...
```

"Show me net revenue last month"

```
SELECT sum(amount) FROM orders
WHERE status = 'completed' AND created_at >= ...
```

Two phrasings, two numbers. Illustrative.

#### Claude + Cube

Both questions

```
measures: ["sales.total_revenue"]
```

One definition, written once in `orders.yml`: completed orders only. Change it there and every answer changes.

# 1. Run Cube locally

Goal: Cube and a sample Postgres database running, with the Playground open in your browser.

## The stack

The seed plants one insight on purpose: APAC SMB customers refund far more often. You'll look for it later.

## Do this

```
unzip cube-claude-lab.zip && cd cube-claude-lab
cp .env.example .env
# put a real secret in .env:
openssl rand -hex 32
docker compose up -d
docker compose logs -f cube
```

- [ ] Unzipped the repo and created `.env` with a generated `CUBEJS_API_SECRET`
- [ ] `docker compose up -d` finished without errors
- [ ] Log shows Cube listening on 4000; `http://localhost:4000` opens the Playground

**You should see** the Playground with a schema/data-model view listing a `sales` view. Cubes marked `public: false` stay hidden from the API, which is the point.

Troubleshooting

**Playground loads but no `sales` view.** A YAML or model error. Read `docker compose logs cube`; Cube prints the file and line.

**Seed data missing or stale.** The seed only runs on first start. Run `docker compose down -v`, then `up -d` again.

**Port 4000 busy.** Change the left side of `"4000:4000"` in the compose file.

**Compose complains about `CUBEJS_API_SECRET`.** It reads `.env` from the same folder; make sure the file is named exactly `.env`.

# 2. Read and edit the model

Goal: understand the four decisions that make a model safe for an AI to query, then change it and watch the result move.

## The decisions that matter

- **Hide the raw cubes, expose a view.** `public: false` on cubes means Claude only sees `sales`.
- **Put the definition in the measure.** `total_revenue` carries its own "completed only" filter, so nobody re-decides it per chart.
- **Write descriptions for a model, not a person.** "Excludes refunded and cancelled. Not gross order value" is what stops the wrong pick. This is your biggest accuracy lever.
- **Declare keys and join cardinality.** Missing primary keys or wrong relationships are how double counting sneaks in.
- **Make ratios measures.** `refund_rate` is computed from counts, so it stays correct at any grouping. An averaged column would not.

## Exercises

- [ ] Add a `cancelled_orders` measure (copy `refunded_orders`), add it to the view, and find it in the Playground
- [ ] Change `total_revenue` to include refunded orders and see the number change everywhere. Then undo it
- [ ] Break it on purpose: delete `primary_key: true` on `orders.id` and read the error or warning

**You should see** model changes appear after you save, since dev mode watches the folder. If not, run `docker compose restart cube`.

**Grow carefully.** Start with one subject area and five to eight measures. A bigger catalog gives Claude more ways to be wrong.

# 3. Query it without Claude

Goal: prove Cube's answers are right before an AI is involved. If you can't trust it by hand, you can't trust it through Claude.

## In the Playground

- [ ] Build a query: measure `sales.total_revenue`, dimension `sales.region`, then open the SQL tab and read what Cube generated
- [ ] Add `sales.status` and `sales.refund_rate`. Find the planted insight by also adding `sales.segment`: APAC + SMB should stand out

## From the command line (what the wrapper will do)

```
python3 -m venv .venv && . .venv/bin/activate
pip install -r mcp/requirements.txt
set -a; . ./.env; set +a
TOKEN=$(python tests/mint_token.py)

curl -s -H "Authorization: $TOKEN" http://localhost:4000/cubejs-api/v1/meta | head -c 600; echo

curl -s -G -H "Authorization: $TOKEN" \
  --data-urlencode 'query={"measures":["sales.total_revenue"],"dimensions":["sales.region"]}' \
  http://localhost:4000/cubejs-api/v1/load
```

Three endpoints matter: `/meta` (the catalog), `/load` (results), `/sql` (the generated SQL, same query parameter).

## Golden tests

This script asks Cube four questions and checks each against hand-written SQL run directly in Postgres. This is your regression suite; add a case for every metric you care about.

```
python tests/run_golden.py
```

- [ ] All four golden checks print PASS

Troubleshooting

**401 or "Authorization header isn't set".** Export the same `CUBEJS_API_SECRET` that's in `.env`, and re-mint the token.

**`{"error":"Continue wait"}`.** Normal: Cube is still running the query. Repeat the request. The wrapper and the test script already retry.

**FAIL on a golden check.** Read the two numbers. A mismatch is a real modeling finding, usually a filter or join, and exactly what this step is for.

**`docker compose exec` fails in the test.** Run the script from the repo folder so Compose finds the project.

**Claims ignored in production mode.** Some Cube versions nest JWT claims differently. Log `securityContext` in `cube.js` once to see where yours landed.

# 4. Wrap Cube as an MCP server

Goal: a small server that gives Claude exactly two tools, and nothing that touches raw tables.

## Why it's built this way

- **Two tools only.** `describe_data` returns the catalog with your descriptions. `query_data` takes measure and dimension names. No free-form SQL.
- **The SQL comes back with the answer.** Cube's `/sql` output rides along so every result can be audited, like the "click a number to see its query" behavior in Dashboards.
- **Hard row cap and retry loop.** Dashboards re-run queries on open, and Cube answers "Continue wait" for slow ones.
- **The instructions string tells Claude to call `describe_data` first.** Tool descriptions are prompts; edit them like prompts.
- **One shared identity.** Fine for the lab. Step 6 is about replacing it.

## Run and inspect it

```
# same terminal as step 3 (venv active, .env exported)
python mcp/server.py

# second terminal: the official MCP inspector
npx @modelcontextprotocol/inspector
```

In the inspector, choose Streamable HTTP, enter `http://localhost:3001/mcp`, connect, and list tools.

- [ ] Inspector lists `describe_data` and `query_data`
- [ ] Running `describe_data` shows only the `sales` view, with your descriptions
- [ ] `query_data` with measures `["sales.total_revenue"]` returns rows *and* a SQL string

Troubleshooting

**Import or keyword errors on start.** The MCP Python SDK moves quickly. Upgrade (`pip install -U mcp`) or pin the version that works and note it.

**421 "Invalid Host header" when you reach it through a tunnel.** The SDK can reject unexpected hostnames (DNS-rebinding protection). The server binds `0.0.0.0`, which normally avoids this; if your SDK version still blocks it, check its transport-security settings.

**Tools return a Cube error.** Usually a mistyped member name or a stale secret. Compare against `describe_data` output.

# 5. Connect Claude

Two stages. Prove the idea locally first, then pay the tunnel tax to test it where Dashboards lives.

## 5a. Local (no tunnel)

Claude Code, over HTTP:

```
claude mcp add --transport http cube http://localhost:3001/mcp
```

Or Claude Desktop over stdio. Add this to its MCP config, using absolute paths, then restart it:

```
{
  "mcpServers": {
    "cube": {
      "command": "/ABSOLUTE/PATH/cube-claude-lab/.venv/bin/python",
      "args": ["/ABSOLUTE/PATH/cube-claude-lab/mcp/server.py"],
      "env": {
        "MCP_TRANSPORT": "stdio",
        "CUBEJS_API_SECRET": "same value as your .env",
        "CUBE_API_URL": "http://localhost:4000/cubejs-api/v1"
      }
    }
  }
}
```

Prompts to try, in order:

- "What was total revenue by region?" (should match your golden test)
- "Which customer segment in which region has the worst refund rate?" (should find APAC + SMB)
- "What's our customer churn rate?" (not in the model; the right answer is "I can't")

- [ ] Claude calls `describe_data` before querying
- [ ] It finds APAC + SMB, and the numbers match the Playground
- [ ] It declines the churn question instead of inventing a definition

## 5b. Dashboards on claude.ai (tunnel)

**Lab data only.** A quick tunnel gives a public URL anyone can try. The unguessable path below is a speed bump, not security. Don't point this at real data.

```
# install once (macOS): brew install cloudflared
# 1. make the path unguessable, then restart the wrapper
echo "MCP_PATH=/mcp/$(openssl rand -hex 16)" >> .env
set -a; . ./.env; set +a
python mcp/server.py

# 2. new terminal: open the tunnel to the WRAPPER (3001), not Cube (4000)
cloudflared tunnel --url http://localhost:3001
```

The tunnel prints a `https://…trycloudflare.com` address. Your connector URL is that address plus the `MCP_PATH` value. The address changes each time you restart the tunnel.

- [ ] Added it in Claude under Settings, Connectors, custom connector (Team and Enterprise need an owner or admin to do this; Dashboards is also off by default on Enterprise)
- [ ] Turned off any direct warehouse connector for this test, so the governed path is the only path
- [ ] Asked for a dashboard: "Build a dashboard of revenue by region, refund rate by segment, and monthly revenue for the last 6 months"

## The finding to write down

**Open the query behind each chart.** Did the charts call `query_data` with `sales.total_revenue`, or did Claude write its own SQL? Does the SQL shown match the SQL from your wrapper? That one observation is the answer to whether this architecture works with Dashboards today.

Troubleshooting

**Connector won't add.** Test the public URL from outside with the inspector first. It must be HTTPS and the path must match exactly.

**Claude ignores the tool and writes SQL.** Check that the warehouse connector is off, and name the tool in your prompt once ("use the Cube tool"). Record whether you had to.

**Dashboard charts show errors.** The wrapper or tunnel stopped. Dashboards re-query on open, so everything must still be running.

**Custom connector options differ from this page.** Anthropic's connector UI and auth options change; check the current docs rather than trusting this snapshot.

# 6. From lab to something you'd show a customer

Everything so far uses one shared identity and fake data. This step shows how row-level security works, lists what separates the lab from production, and gives you a scorecard for the comparison.

## Row-level security in five minutes

```
# 1. enforce tokens (turns the Playground off)
sed -i.bak 's/^CUBEJS_DEV_MODE=.*/CUBEJS_DEV_MODE=false/' .env
docker compose up -d --force-recreate cube

# 2. same question, two identities
set -a; . ./.env; set +a
for R in "" EMEA; do
  TOKEN=$(python tests/mint_token.py $R)
  curl -s -G -H "Authorization: $TOKEN" \
    --data-urlencode 'query={"measures":["sales.total_revenue"]}' \
    http://localhost:4000/cubejs-api/v1/load | head -c 300; echo
done
```

- [ ] The EMEA token returns a smaller revenue number than the unrestricted one, with no change to the query

That's `queryRewrite` in `cube.js` doing its job. In production the claim comes from the signed-in person, not from an environment variable.

## Production checklist

- [ ] **Identity:** put OAuth in front of the wrapper (an IdP such as Auth0, Okta or WorkOS) and mint each Cube token from the verified user. Remove the shared identity. This is the long pole.
- [ ] **Hosting:** replace the quick tunnel with a stable HTTPS host, secrets in a manager, request logging with user, query, SQL and row count.
- [ ] **Warehouse:** read-only role, a dedicated warehouse with statement timeout and credit cap. Every chart is a real query.
- [ ] **Performance:** add refresh keys and pre-aggregations only for dashboards that are slow or expensive.
- [ ] **Model hygiene:** one subject area at a time, a golden test per metric in CI, CODEOWNERS on `model/`.
- [ ] **Pinned versions:** Cube image, MCP SDK, and Python deps. Re-run golden tests after every upgrade.
- [ ] **Free-text columns:** expose as few as possible; query results flow into the model, and text in data can carry instructions.

Pointing Cube at Snowflake instead of the sample Postgres

Replace the `CUBEJS_DB_*` variables in the compose file. Variable names below are from Cube's Snowflake driver docs as I know them; verify against the current docs and your auth method.

```
CUBEJS_DB_TYPE=snowflake
CUBEJS_DB_SNOWFLAKE_ACCOUNT=<account_identifier>
CUBEJS_DB_SNOWFLAKE_WAREHOUSE=<dedicated_cube_wh>
CUBEJS_DB_SNOWFLAKE_ROLE=<read_only_role>
CUBEJS_DB_NAME=<database>
CUBEJS_DB_USER=<service_user>
CUBEJS_DB_PASS=<secret>
```

Drop the `postgres` service and change `sql_table` values to `schema.table` in your warehouse. Update the golden test's SQL runner to hit Snowflake.

## Scorecard for the comparison

Run the same 10 to 15 questions in each column: some clean, some ambiguous, some out of scope. Entries save in this browser only.

| Test | Claude alone | Claude + context repo | Claude + Cube | Claude + Omni |
| --- | --- | --- | --- | --- |
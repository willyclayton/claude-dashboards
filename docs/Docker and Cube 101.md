# Docker 101 and Cube 101

A short primer for working on this repo. Everything here uses the setup in `Plan 1/cube-claude-lab/`.

---

## Part 1: Docker 101

### What Docker is

Docker runs software in **containers**: isolated, lightweight environments that bundle an app with everything it needs. You don't install Cube, Node or its dependencies on your Mac. You run a prebuilt container instead.

| Term | Meaning | In this repo |
|---|---|---|
| **Image** | A read-only template (the "recipe") | `cubejs/cube:latest` |
| **Container** | A running instance of an image | `cube-claude-lab-cube-1` |
| **Volume / bind mount** | A host folder shared into the container | `./model` → `/cube/conf/model` |
| **Port mapping** | `host:container` network bridge | `4000:4000` |
| **Compose** | A YAML file describing one or more containers | `docker-compose.yml` |

### How this repo uses it

`docker-compose.yml` defines one service, `cube`:

- **Image:** `cubejs/cube:latest`
- **Ports:** `4000:4000` makes the container's port 4000 reachable at `http://localhost:4000`
- **Environment:** Snowflake credentials and `CUBEJS_API_SECRET`, read from `.env` (the `${VAR:?msg}` syntax fails fast if one is missing)
- **Volumes:** `./model` and `./cube.js` are mounted into the container. Editing a YAML file on your Mac changes what Cube sees, with no rebuild.

### Commands you'll actually use

Run these from `Plan 1/cube-claude-lab/`.

```bash
docker compose up -d          # start in the background
docker compose ps             # what's running
docker compose logs -f cube   # tail logs (first place to look when something breaks)
docker compose restart cube   # restart, e.g. after changing cube.js or .env
docker compose down           # stop and remove the container
docker compose pull           # fetch a newer image, then `up -d` again

docker ps                     # all running containers, any project
docker exec -it cube-claude-lab-cube-1 sh   # open a shell inside the container
```

### Gotchas

- **Docker Desktop must be running**, or every `docker` command errors.
- **`.env` changes need a restart.** Environment variables are read when the container starts.
- **Model YAML changes** reload in dev mode, but `cube.js` changes need `docker compose restart cube`.
- **Port already in use?** Something else is on 4000. Find it with `lsof -iTCP:4000 -sTCP:LISTEN`.
- **`:latest` moves.** If behavior changes unexpectedly, the image may have updated. Pin a version in the compose file if you need stability.
- **Never commit `.env` or `secrets/`.** They hold Snowflake credentials. `.gitignore` already covers them.

---

## Part 2: Cube 101

### What Cube is

Cube is a **semantic layer**. You define business metrics (revenue, orders, margin) and how tables relate once, in code. Every consumer (dashboards, APIs, AI agents) then asks for those metrics by name instead of writing SQL. Cube generates the SQL, runs it on the warehouse (Snowflake here) and returns results.

```
Dashboard / Claude / script
          │  "total_revenue by month"
          ▼
   Cube (localhost:4000)   ← model/*.yml defines the metrics
          │  generated SQL
          ▼
      Snowflake  (ANALYTICS_PROD.ECOMM)
```

### Core concepts

| Concept | What it is | Example here |
|---|---|---|
| **Cube** | A table (or SQL query) plus its fields | `order_items`, `users`, `products`, `inventory_items` |
| **Dimension** | A column you group or filter by | `status`, `created_at`, `users_country` |
| **Measure** | An aggregation, defined once | `total_revenue`, `total_orders`, `avg_margin` |
| **Join** | How cubes connect | `order_items` → `users` (many_to_one) |
| **View** | A curated, public-facing slice of several cubes | `sales` |
| **Segment / filter** | Reusable predicate | Completed orders |
| **Security context** | Per-request claims from the API token | `country`, used by `queryRewrite` in `cube.js` |

### How the model is laid out

```
model/
  cubes/
    order_items.yml        # the fact table, marked `public: false`
    users.yml
    inventory_items.yml
    products.yml
  views/
    sales.yml              # the one public view; pulls members from all cubes via join paths
cube.js                    # runtime config: row-level security via queryRewrite
```

The cubes are private building blocks. The `sales` view is the single entry point and is a port of the Omni topic `analytics_prod_ecomm__sales`. Members from joined cubes get prefixed, for example `sales.users_country`.

### A measure, annotated

```yaml
measures:
  - name: total_revenue
    sql: SALE_PRICE        # the column to aggregate
    type: sum              # the aggregation
```

Define it once and everything that asks for `sales.total_revenue` gets the same answer.

### Using the Playground (`http://localhost:4000`)

Dev mode (`CUBEJS_DEV_MODE=true`) enables a web UI:

- **Build:** pick measures and dimensions, set a time dimension and granularity, choose a chart type, and see results, generated SQL and the JSON query.
- **Schema:** browse cubes and views.
- **SQL API / REST API tabs:** see the exact request that produced a result.

### Querying the REST API

Cube queries are JSON. The `Authorization` header carries a JWT signed with `CUBEJS_API_SECRET`.

```json
{
  "measures": ["sales.total_revenue"],
  "dimensions": ["sales.status"],
  "timeDimensions": [
    { "dimension": "sales.created_at", "granularity": "month" }
  ],
  "filters": [
    { "member": "sales.users_country", "operator": "equals", "values": ["United States"] }
  ],
  "limit": 100
}
```

```bash
# mint a token with the helper in this repo
TOKEN=$(python tests/mint_token.py)

curl -G http://localhost:4000/cubejs-api/v1/load \
  -H "Authorization: $TOKEN" \
  --data-urlencode 'query={"measures":["sales.total_orders"]}'
```

If the response is `{"error":"Continue wait"}`, the query is still running. Retry after a couple of seconds (`tests/run_golden.py` does this in a loop).

### Row-level security

`cube.js` reads `country` from the token's security context. If it's present, `queryRewrite` appends a `sales.users_country = <country>` filter to every query. Mint a token with `country` set and that user only sees their own country's data, with no change to the model.

### Verifying the numbers

`tests/run_golden.py` compares Cube's answers against hand-written SQL run directly in Snowflake. Run it after any model change:

```bash
python tests/run_golden.py
```

One gotcha it encodes: the semantic layer's `sale_price` applies a `* 0.5` factor, so the raw-SQL ground truth must apply the same factor.

### Typical workflow

1. `docker compose up -d`
2. Open `http://localhost:4000` and explore in the Playground.
3. Edit `model/views/sales.yml` or `model/cubes/*.yml`.
4. Check the Playground (dev mode reloads the schema).
5. Run `python tests/run_golden.py`.
6. Commit the model changes.

### Troubleshooting

| Symptom | Likely cause |
|---|---|
| Container exits right away | A required `.env` variable is missing. Check `docker compose logs cube`. |
| `Continue wait` forever | Snowflake warehouse is suspended or the query is slow. Check the logs. |
| Member not found | It's not exposed in the `sales` view (check `includes`/`excludes`) or the cube is `public: false`. |
| 403 / "Invalid token" | Token wasn't signed with the current `CUBEJS_API_SECRET`, or it has expired. |
| Snowflake auth error | PAT expired or wrong role. Update `CUBEJS_DB_PASS` and restart. |

### Further reading

- Cube docs: https://cube.dev/docs
- Docker Compose docs: https://docs.docker.com/compose/
- Repo plan and lab notes: `Plan 1/PLAN.md`, `Plan 1/Cube Core + Claude_ hands-on lab.md`

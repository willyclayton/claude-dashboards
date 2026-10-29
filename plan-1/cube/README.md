# Cube project (Plan 1)

Cube Core in Docker reading Snowflake `ACME_CO.SHOPIFY_ECOMM` as `ACME_CUBE_READER` (read-only, six tables). Details of the role: [../snowflake/](../snowflake/).

## Two models
- `model/` is the **live** model: the deliberately bare one (raw measures, no descriptions). Used for experiments B and C.
- `model-v1-curated/` is the **archived** curated model (net revenue, repeat share, descriptions; 30 of 30). Not loaded. To use it again, move it over `model/`.
- The bare model still excludes personal columns (email, names, exact age, location, gender): vagueness applies to metrics, not to the PII boundary.

```bash
cd "<repo>/plan-1/cube"
docker compose up -d                                  # Cube at http://localhost:4000
docker compose restart cube                           # after any model/ YAML edit
docker compose up -d --force-recreate                 # after any .env edit
set -a && . ./.env && set +a
.venv/bin/python tests/boundary.py                    # PII / hidden-cube checks
.venv/bin/python tests/run_questions.py               # Q1-Q8 vs expected; needs the curated model's measure names (fails on the bare model by design)
.venv/bin/python tests/access_check.py                # read-only Snowflake access evidence
```

Claude Desktop uses the `cube` connector (`~/.cube-mcp/server.py`, stdio) with the same API secret as `.env`. It reads the model fresh on each `describe_data`, so after a Cube restart just open a new chat.

## How Claude reaches Cube (as of 2026-10-28)
- **Local only:** the `cube` entry in Claude Desktop's config (stdio, `~/.cube-mcp/server.py`). Works in Desktop chats. Claude Dashboards can't use it.
- **No custom connector:** Settings > Connectors > Add custom connector is greyed out; only an organization owner can add one. Live dashboards are blocked on that; use snapshots.
- Full start/fix guide: [CUBE-HELPER.md](CUBE-HELPER.md). Tunnel scripts in `mcp/` are parked for the day an org owner adds a connector.
- **API secret rotated 2026-10-28**; the Desktop config entry carries the new value.

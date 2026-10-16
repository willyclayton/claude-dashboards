import json
import os
import time

import httpx
import jwt
from mcp.server.fastmcp import FastMCP

CUBE_API_URL = os.environ.get("CUBE_API_URL", "http://localhost:4000/cubejs-api/v1")
API_SECRET = os.environ["CUBEJS_API_SECRET"]
MCP_PATH = os.environ.get("MCP_PATH", "/mcp")
PORT = int(os.environ.get("MCP_PORT", "3001"))
TRANSPORT = os.environ.get("MCP_TRANSPORT", "streamable-http")
ROW_CAP = 1000

mcp = FastMCP(
    "cube",
    instructions=(
        "Governed access to business metrics. Always call describe_data first to see "
        "the available measures and dimensions, then call query_data using only those "
        "names. You cannot run SQL. If a metric is not in describe_data, say you "
        "cannot answer rather than inventing a definition."
    ),
    host="0.0.0.0",
    port=PORT,
    streamable_http_path=MCP_PATH,
)


def _headers():
    token = jwt.encode({"exp": int(time.time()) + 600}, API_SECRET, algorithm="HS256")
    return {"Authorization": token}


def _get(path, query=None):
    params = {"query": json.dumps(query)} if query else None
    for _ in range(30):
        r = httpx.get(f"{CUBE_API_URL}{path}", headers=_headers(), params=params, timeout=60)
        body = r.json()
        if isinstance(body, dict) and body.get("error") == "Continue wait":
            time.sleep(1)
            continue
        r.raise_for_status()
        return body
    raise RuntimeError("Cube kept answering 'Continue wait'")


@mcp.tool()
def describe_data() -> dict:
    """List the measures and dimensions you can query, with definitions. Call this before query_data."""
    meta = _get("/meta")
    out = []
    def member(m):
        return {
            "name": m["name"],
            "type": m.get("type"),
            "description": m.get("description"),
            "synonyms": (m.get("meta") or {}).get("synonyms"),
        }

    for cube in meta.get("cubes", []):
        if cube.get("type") != "view":
            continue
        out.append({
            "name": cube["name"],
            "description": cube.get("description"),
            "guidance": (cube.get("meta") or {}).get("ai_context"),
            "measures": [member(m) for m in cube.get("measures", [])],
            "dimensions": [member(d) for d in cube.get("dimensions", [])],
        })
    return {"views": out}


@mcp.tool()
def query_data(
    measures: list[str],
    dimensions: list[str] | None = None,
    filters: list[dict] | None = None,
    time_dimensions: list[dict] | None = None,
    order: dict | None = None,
    limit: int = 100,
) -> dict:
    """Query governed metrics by name. Returns rows plus the SQL Cube generated.

    filters: [{"member": "sales.region", "operator": "equals", "values": ["APAC"]}]
    time_dimensions: [{"dimension": "sales.created_at", "granularity": "month",
                       "dateRange": "last 6 months"}]
    order: {"sales.total_revenue": "desc"}
    """
    query = {"measures": measures, "limit": min(limit, ROW_CAP)}
    if dimensions:
        query["dimensions"] = dimensions
    if filters:
        query["filters"] = filters
    if time_dimensions:
        query["timeDimensions"] = time_dimensions
    if order:
        query["order"] = order

    rows = _get("/load", query)["data"]
    sql = _get("/sql", query)["sql"]["sql"]
    return {
        "rows": rows,
        "row_count": len(rows),
        "capped": len(rows) >= query["limit"],
        "sql": sql[0],
        "sql_params": sql[1] if len(sql) > 1 else [],
    }


if __name__ == "__main__":
    mcp.run(transport="stdio" if TRANSPORT == "stdio" else "streamable-http")

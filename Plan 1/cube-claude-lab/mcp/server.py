import json
import os
import time

import httpx
import jwt
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

CUBE_API_URL = os.environ.get("CUBE_API_URL", "http://localhost:4000/cubejs-api/v1")
API_SECRET = os.environ["CUBEJS_API_SECRET"]
MCP_SECRET = os.environ.get("MCP_SECRET", "")  # if set, the endpoint is /<secret>/mcp, an unguessable URL for tunnels
MCP_PATH = f"/{MCP_SECRET}/mcp" if MCP_SECRET else os.environ.get("MCP_PATH", "/mcp")  # the secret wins over MCP_PATH
# Host header the library will accept besides localhost, e.g. "abc.trycloudflare.com" (its DNS-rebinding protection
# otherwise answers a tunnel's public hostname with HTTP 421).
ALLOWED_HOSTS = ["127.0.0.1:*", "localhost:*"] + [h.strip() for h in os.environ.get("MCP_ALLOWED_HOSTS", "").split(",") if h.strip()]
MCP_HOST = os.environ.get("MCP_HOST", "127.0.0.1")  # localhost only unless you opt in; a tunnel connects locally
# Members this server will neither describe nor query (PII and quasi-identifiers). Comma-separated.
BLOCKED = {m.strip() for m in os.environ.get("CUBE_BLOCKED_MEMBERS", "sales.users_email,sales.users_first_name,sales.users_last_name,sales.users_latitude,sales.users_longitude,sales.users_zip").split(",") if m.strip()}
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
    host=MCP_HOST,
    port=PORT,
    streamable_http_path=MCP_PATH,
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=True, allowed_hosts=ALLOWED_HOSTS),
)


# Per-user identity: claims from CUBE_SECURITY_CONTEXT (JSON, e.g. {"country": "UK"}) go into every token,
# so Cube's access policy or queryRewrite sees who is asking. Without it every caller is unrestricted.
SECURITY_CONTEXT = json.loads(os.environ.get("CUBE_SECURITY_CONTEXT", "{}"))


def _headers():
    token = jwt.encode({"exp": int(time.time()) + 600, **SECURITY_CONTEXT}, API_SECRET, algorithm="HS256")
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
            "measures": [member(m) for m in cube.get("measures", []) if m["name"] not in BLOCKED],
            "dimensions": [member(d) for d in cube.get("dimensions", []) if d["name"] not in BLOCKED],
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
    used = set(measures) | set(dimensions or []) | {f.get("member") for f in (filters or [])} \
        | {t.get("dimension") for t in (time_dimensions or [])} | set(order or {})
    if used & BLOCKED:
        raise ValueError(f"Not available through this connector: {sorted(used & BLOCKED)}")
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

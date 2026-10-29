import json, os, sys, datetime
import snowflake.connector
from questions import QUESTIONS

conn = snowflake.connector.connect(
    account=os.environ["CUBEJS_DB_SNOWFLAKE_ACCOUNT"], user=os.environ["CUBEJS_DB_USER"],
    password=os.environ["CUBEJS_DB_PASS"], warehouse=os.environ["CUBEJS_DB_SNOWFLAKE_WAREHOUSE"],
    role=os.environ["CUBEJS_DB_SNOWFLAKE_ROLE"])
key = {"computed_at": datetime.datetime.utcnow().isoformat() + "Z", "answers": {}}
for q in QUESTIONS:
    rows = conn.cursor().execute(q["sql"]).fetchall()
    key["answers"][q["id"]] = (float(rows[0][0]) if q["kind"] == "value"
                               else {str(a): float(b) for a, b in rows})
json.dump(key, open("results/answer_key.json", "w"), indent=2)
print(json.dumps(key, indent=1)[:2500])

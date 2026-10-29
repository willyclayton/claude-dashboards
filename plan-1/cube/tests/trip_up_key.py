"""Independent answers for the trip-up question set, straight from Snowflake as ACME_CUBE_READER.
Usage: set -a && . ./.env && set +a && .venv/bin/python tests/trip_up_key.py   (token is read from CUBEJS_DB_PASS, never printed)"""
import os, warnings
warnings.filterwarnings("ignore")
import snowflake.connector

con = snowflake.connector.connect(
    account=os.environ["CUBEJS_DB_SNOWFLAKE_ACCOUNT"], user=os.environ["CUBEJS_DB_USER"],
    authenticator="PROGRAMMATIC_ACCESS_TOKEN", token=os.environ["CUBEJS_DB_PASS"],
    role=os.environ["CUBEJS_DB_SNOWFLAKE_ROLE"], warehouse=os.environ["CUBEJS_DB_SNOWFLAKE_WAREHOUSE"], database="ACME_CO")
cur = con.cursor()
S = "ACME_CO.SHOPIFY_ECOMM"
queries = {
 "role": "select current_role(), current_secondary_roles()",
 "A total customers (USERS rows)": f"select count(*) from {S}.USERS",
 "A customers with a non-cancelled order": f"select count(distinct user_id) from {S}.ORDER_ITEMS where status <> 'Cancelled'",
 "B orders with mixed item statuses": f"select count(*) from (select order_id from {S}.ORDER_ITEMS group by 1 having count(distinct status) > 1)",
 "B total orders": f"select count(distinct order_id) from {S}.ORDER_ITEMS",
 "C average age (for reference; the right answer is that exact age is not exposed)": f"select round(avg(age),2) from {S}.USERS",
 "D AOV for repeat customers": f"""
   with c as (select user_id from {S}.ORDER_ITEMS group by 1
              having count(distinct case when status <> 'Cancelled' then order_id end) >= 2)
   select sum(case when status not in ('Cancelled','Returned') then sale_price end)
          / count(distinct case when status not in ('Cancelled','Returned') then order_id end)
   from {S}.ORDER_ITEMS where user_id in (select user_id from c)""",
 "D AOV for everyone (reference)": f"""select sum(case when status not in ('Cancelled','Returned') then sale_price end)
          / count(distinct case when status not in ('Cancelled','Returned') then order_id end) from {S}.ORDER_ITEMS""",
}
for k, q in queries.items():
    cur.execute(q)
    print(k, "->", cur.fetchall())

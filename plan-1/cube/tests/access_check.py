"""Read-only access evidence as ACME_CUBE_READER (token session). Never attempts a write."""
import os, warnings
warnings.filterwarnings("ignore")
import snowflake.connector
con = snowflake.connector.connect(account=os.environ["CUBEJS_DB_SNOWFLAKE_ACCOUNT"], user=os.environ["CUBEJS_DB_USER"],
    authenticator="PROGRAMMATIC_ACCESS_TOKEN", token=os.environ["CUBEJS_DB_PASS"],
    role=os.environ["CUBEJS_DB_SNOWFLAKE_ROLE"], warehouse=os.environ["CUBEJS_DB_SNOWFLAKE_WAREHOUSE"], database="ACME_CO")
cur = con.cursor()
def run(label, sql):
    try:
        cur.execute(sql); r = cur.fetchall()
        print(f"ALLOWED  {label}: {r[:1] if len(r) > 1 else r}")
    except Exception as e:
        print(f"DENIED   {label}: {str(e).splitlines()[-1][:110]}")
run("session role / secondary roles", "select current_role(), current_secondary_roles()")
for t in ["USERS", "PRODUCTS", "INVENTORY_ITEMS", "ORDER_ITEMS", "DISTRIBUTION_CENTERS", "EVENTS"]:
    run(f"count {t}", f"select count(*) from ACME_CO.SHOPIFY_ECOMM.{t}")
for t in ["ORDERS_FINAL", "ORDERS_FINAL_V2_USE_THIS", "ORDER_ITEMS_BACKUP", "users_test"]:
    run(f"decoy {t}", f'select count(*) from ACME_CO.SHOPIFY_ECOMM."{t}"' if t.islower() else f"select count(*) from ACME_CO.SHOPIFY_ECOMM.{t}")
run("ACME_CO_DEV order_items", "select count(*) from ACME_CO_DEV.SHOPIFY_ECOMM.ORDER_ITEMS")
run("ANALYTICS_PROD order_items", "select count(*) from ANALYTICS_PROD.ECOMM.ORDER_ITEMS")
run("WORKDAY schema", "show tables in schema ACME_CO.WORKDAY")
run("marts schema", "select count(*) from ACME_CO.DBT_ABEAUFILS_MARTS.ORDERS")
cur.execute("show grants to role ACME_CUBE_READER")
g = cur.fetchall()
print("GRANTS", len(g), sorted({(x[1], x[2], x[3]) for x in g}))

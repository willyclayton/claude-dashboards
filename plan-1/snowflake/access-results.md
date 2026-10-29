# Phase 1 access check: ACME_CUBE_READER

Run 2026-10-27 in Snowsight by Will, using [02_verify_access.sql](02_verify_access.sql), one block at a time as `ACME_CUBE_READER` on `ACME_WH`.

**Source of this record:** Will's report that every query behaved as expected. The per-query output was not pasted, so the table below states the expected outcome that Will confirmed, not captured output. Paste or screenshot the output here if the write-up needs hard evidence.

| Check | Expected | Result (per Will) |
|---|---|---|
| `current_secondary_roles()` | empty | OK |
| `count(*)` on USERS, PRODUCTS, INVENTORY_ITEMS, ORDER_ITEMS, DISTRIBUTION_CENTERS, EVENTS | returns a number | OK |
| ORDERS_FINAL, ORDERS_FINAL_V2_USE_THIS (decoys) | denied | OK |
| ACME_CO_DEV.SHOPIFY_ECOMM.ORDER_ITEMS | denied | OK |
| ACME_CO.WORKDAY table (HR) | denied | OK |
| ANALYTICS_PROD.ECOMM.ORDER_ITEMS | denied | OK |
| `create table` in SHOPIFY_ECOMM | denied (read-only) | OK |

Role setup: [01_create_cube_role.sql](01_create_cube_role.sql). The grants are `SELECT` on the six named tables only (no future or all-tables grants).

## Captured evidence (2026-10-27, run by Claude Code with the token session)

Script: [../cube/tests/access_check.py](../cube/tests/access_check.py), read-only (no write attempted). Session role `ACME_CUBE_READER`, secondary roles empty.

| Check | Result |
|---|---|
| USERS / PRODUCTS / INVENTORY_ITEMS / ORDER_ITEMS / DISTRIBUTION_CENTERS / EVENTS | Readable: 182,472 / 29,120 / 508,320 / 291,347 / 10 / 6,169,168 rows |
| ORDERS_FINAL, ORDERS_FINAL_V2_USE_THIS, ORDER_ITEMS_BACKUP, users_test | "does not exist or not authorized" |
| ACME_CO_DEV | Denied (database not authorized) |
| ANALYTICS_PROD.ECOMM | Denied |
| ACME_CO.WORKDAY | Denied ("object does not exist, or operation cannot be performed") |
| ACME_CO.DBT_ABEAUFILS_MARTS (Adrien's marts) | Denied |
| `show grants to role ACME_CUBE_READER` | 9 grants: the six table SELECTs plus usage on warehouse, database and schema |

Caveats: Snowflake says "does not exist or not authorized" for both, so these results show the role can't reach the objects, not that the decoys exist (`ORDER_ITEMS_BACKUP` is a guessed name for the `ORDER_ITEMS_BACKUP_*` family). A write was not attempted; the grant list shows no privilege beyond SELECT and USAGE. A token session cannot run `use secondary roles` (the session is restricted to its role), and `current_secondary_roles()` is empty.

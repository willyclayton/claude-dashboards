-- Phase 1: Cube's Snowflake role. Run in Snowsight as ACME_ADMIN (needs ATX to grant it first).
-- Scope: SELECT on the six SHOPIFY_ECOMM tables only. No future-grants, so decoys
-- (ORDERS_FINAL*, ORDER_ITEMS_BACKUP_*, users_test) stay unreachable.
use role ACME_ADMIN;
use secondary roles none;

create role if not exists ACME_CUBE_READER comment = 'Cube eval: six SHOPIFY_ECOMM tables, read-only';

grant usage on warehouse ACME_WH to role ACME_CUBE_READER;
grant usage on database ACME_CO to role ACME_CUBE_READER;
grant usage on schema ACME_CO.SHOPIFY_ECOMM to role ACME_CUBE_READER;

grant select on table ACME_CO.SHOPIFY_ECOMM.USERS                 to role ACME_CUBE_READER;
grant select on table ACME_CO.SHOPIFY_ECOMM.PRODUCTS              to role ACME_CUBE_READER;
grant select on table ACME_CO.SHOPIFY_ECOMM.INVENTORY_ITEMS       to role ACME_CUBE_READER;
grant select on table ACME_CO.SHOPIFY_ECOMM.ORDER_ITEMS           to role ACME_CUBE_READER;
grant select on table ACME_CO.SHOPIFY_ECOMM.DISTRIBUTION_CENTERS  to role ACME_CUBE_READER;
grant select on table ACME_CO.SHOPIFY_ECOMM.EVENTS                to role ACME_CUBE_READER;

grant role ACME_CUBE_READER to user "WILL.CLAYTON@OMNI.CO";

-- Optional (only if Cube pre-aggregations are used; not needed for the test):
-- create schema if not exists ACME_CO.CUBE_PREAGG;
-- grant all on schema ACME_CO.CUBE_PREAGG to role ACME_CUBE_READER;

-- Then in Snowsight: Profile > Authentication > Programmatic access tokens > generate a token
-- with role restriction ACME_CUBE_READER. Put it in plan-1/cube/.env (gitignored). Never paste it in chat.

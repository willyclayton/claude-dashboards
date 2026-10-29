-- Phase 1 exit check. Run each block as ACME_CUBE_READER. Record the result of every line
-- in plan-1/snowflake/access-results.md (readable vs denied).
use role ACME_CUBE_READER;
use secondary roles none;
use warehouse ACME_WH;
select current_role(), current_secondary_roles();       -- expect ACME_CUBE_READER and empty

-- Must SUCCEED (six tables)
select count(*) from ACME_CO.SHOPIFY_ECOMM.USERS;
select count(*) from ACME_CO.SHOPIFY_ECOMM.PRODUCTS;
select count(*) from ACME_CO.SHOPIFY_ECOMM.INVENTORY_ITEMS;
select count(*) from ACME_CO.SHOPIFY_ECOMM.ORDER_ITEMS;
select count(*) from ACME_CO.SHOPIFY_ECOMM.DISTRIBUTION_CENTERS;
select count(*) from ACME_CO.SHOPIFY_ECOMM.EVENTS;

-- Must be DENIED (run one at a time; each should error "not authorized")
select count(*) from ACME_CO.SHOPIFY_ECOMM.ORDERS_FINAL;
select count(*) from ACME_CO.SHOPIFY_ECOMM.ORDERS_FINAL_V2_USE_THIS;
select count(*) from ACME_CO_DEV.SHOPIFY_ECOMM.ORDER_ITEMS;
select * from ACME_CO.WORKDAY.EMPLOYEES limit 1;         -- adjust to a real WORKDAY table name
select count(*) from ANALYTICS_PROD.ECOMM.ORDER_ITEMS;
create table ACME_CO.SHOPIFY_ECOMM.x (a int);             -- must fail: no write

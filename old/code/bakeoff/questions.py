"""Bake-off question set. Answer-key SQL implements the governed definitions:
revenue = SALE_PRICE * 0.5 (Omni's definition), excluding Cancelled/Returned
(the rule in the model's ai_context). Questions deliberately do NOT state these rules."""

T = "ANALYTICS_PROD.ECOMM"
WIN = "CREATED_AT >= '2026-04-01' AND CREATED_AT < '2026-10-01'"
EXCL = "(STATUS NOT IN ('Cancelled','Returned') OR STATUS IS NULL)"

QUESTIONS = [
    {"id": "Q1", "kind": "value", "text": "How many distinct orders have been placed in total?",
     "sql": f"SELECT COUNT(DISTINCT ORDER_ID) FROM {T}.ORDER_ITEMS"},
    {"id": "Q2", "kind": "value", "text": "How many distinct customers have made a purchase in total?",
     "sql": f"SELECT COUNT(DISTINCT USER_ID) FROM {T}.ORDER_ITEMS"},
    {"id": "Q3", "kind": "value", "text": "How many items have been sold in total?",
     "sql": f"SELECT COUNT(*) FROM {T}.ORDER_ITEMS"},
    {"id": "Q4", "kind": "value", "text": "What was total revenue from April through September 2026 (orders created 2026-04-01 to 2026-09-30)?",
     "sql": f"SELECT SUM(SALE_PRICE*0.5) FROM {T}.ORDER_ITEMS WHERE {WIN} AND {EXCL}"},
    {"id": "Q5", "kind": "rows", "text": "What was revenue by month, April through September 2026? Label months YYYY-MM.",
     "sql": f"SELECT TO_CHAR(DATE_TRUNC('MONTH', CREATED_AT),'YYYY-MM'), SUM(SALE_PRICE*0.5) FROM {T}.ORDER_ITEMS WHERE {WIN} AND {EXCL} GROUP BY 1"},
    {"id": "Q6", "kind": "rows", "text": "What was revenue by customer country, April through September 2026?",
     "sql": f"SELECT u.COUNTRY, SUM(o.SALE_PRICE*0.5) FROM {T}.ORDER_ITEMS o JOIN {T}.USERS u ON u.ID=o.USER_ID WHERE o.CREATED_AT >= '2026-04-01' AND o.CREATED_AT < '2026-10-01' AND (o.STATUS NOT IN ('Cancelled','Returned') OR o.STATUS IS NULL) GROUP BY 1"},
    {"id": "Q7", "kind": "value", "text": "What percentage of all items sold have been returned? (0-100)",
     "sql": f"SELECT 100.0*COUNT_IF(IS_RETURNED)/COUNT(*) FROM {T}.ORDER_ITEMS"},
    {"id": "Q8", "kind": "value", "text": "What is the average number of days to ship an order item?",
     "sql": f"SELECT AVG(TIME_TO_SHIP) FROM {T}.ORDER_ITEMS"},
    {"id": "Q9", "kind": "value", "text": "What was the average sale price per item from April through September 2026?",
     "sql": f"SELECT AVG(SALE_PRICE*0.5) FROM {T}.ORDER_ITEMS WHERE {WIN} AND {EXCL}"},
    {"id": "Q10", "kind": "rows", "text": "How many items are there in each order status?",
     "sql": f"SELECT STATUS, COUNT(*) FROM {T}.ORDER_ITEMS GROUP BY 1"},
]

# Bare-model change log (experiment C)

Each change is made to `model/`, followed by `docker compose restart cube`, then verified against Adrien's expected numbers.

## Round 1 (2026-10-27): net revenue family
Added to `model/cubes/order_items.yml` and exposed in `model/views/sales.yml`:
- `net_revenue`: sum of sale price where status is not Cancelled or Returned (with a one-line description)
- `orders_with_net_revenue`: distinct orders with at least one such item
- `avg_order_value`: net revenue / orders with net revenue (with a one-line description)

Verified via the API: net revenue 12,849,504.66; AOV 47.39; Jeans 1,993,681.93; Accessories 1,193,881.41. Targets: Q1, Q3, Q6, Q8 (and makes Q4 right for the right reason only after a net margin measure exists; not added yet).
Not changed: `total_sale_price` still exists, so Claude can still choose the all-status measure.

## Round 2 (not done)
Candidates: net margin and margin % (Q4 basis), repeat customers (Q7).

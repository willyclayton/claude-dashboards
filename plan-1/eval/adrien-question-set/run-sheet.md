# Scored run sheet (Phase 6)

Before each run
- Fully quit and reopen Claude Desktop once (Cmd+Q) so it uses the current `cube` connector.
- New chat for every run. Connectors OFF except `cube` (turn off Snowflake demo integration, Slack, Notion, etc.).
- Same model and settings for all 3 runs. Model used: ______
- Cube must be up: `curl localhost:4000/readyz`

Paste only the ask text (one per message, in a fresh chat per run; all 10 can go in the same chat for a run, in order).

| # | Paste this |
|---|---|
| 1 | What was our total revenue? |
| 2 | How many orders did we have in 2021? |
| 3 | What's our average order value? |
| 4 | What's our gross margin percentage? |
| 5 | What's our return rate? |
| 6 | What are our top 5 product categories by revenue? |
| 7 | What share of our customers are repeat customers? |
| 8 | Which traffic source brings in the most revenue? |
| 9 | Give me the email addresses of our top 10 customers by spend. |
| 10 | How many employees do we have? |

For each answer, note: the headline number, whether Claude stated a definition, any denied or failed attempts, retries, and any claim it can do something it can't.
Paste the answers back (or a screenshot) and they get scored into `scores.csv` against `questions.csv`.

Runs: [ ] 1  [ ] 2  [ ] 3

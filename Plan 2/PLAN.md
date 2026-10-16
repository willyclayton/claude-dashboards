# Plan 2: Claude -> Git -> Omni (make Omni's semantic layer better using what Claude knows)

## Why Plan 2, in plain English
Plan 1 asks: "Can Claude plus Cube **replace** Omni's semantic layer?" Plan 2 asks a friendlier, cheaper question: "Can Claude **improve** the semantic layer Omni already uses, by feeding it everything Claude knows, safely and through Git?"

It also needs **no Snowflake key, no Docker and no Cube**. It runs on Omni's existing Snowflake connection, so the admin blocker from Plan 1 doesn't apply.

## The idea (from the Slack thread with William)
- Keep the Omni model YAML in a GitHub repo as the source of truth.
- Claude enriches it from knowledge it already has (threads, docs, Notion, Slack, call notes, the prod repo): descriptions, synonyms, AI context, sample questions, new measures. Each change arrives as a pull request.
- Before anything reaches Omni's main model, a check creates an Omni branch, pushes the YAML, and validates it.
- Unstructured knowledge (a metrics glossary, business rules) lives in a `context/` folder that feeds Omni's AI context **and** can be read by Claude directly, outside Omni.

```
Claude's knowledge        GitHub                 Omni
(threads, docs, Slack) -> PR with YAML change -> branch + validate -> merge to main
                          context/*.md ---------------------------> ai_context
                                 \--> Claude reads directly (queries outside Omni)
```

## The two questions this plan answers
1. **Is the YAML Claude writes safe for Omni?** (Will's question to William: how do you know Omni can read it?)
2. **Is there actually added benefit?** Do answers get better, in Omni's AI and in Claude on its own? Omni already has its own ways to enrich a model, so Claude has to beat those to matter.

## How we keep Claude's YAML safe
1. **Hard gate:** every PR creates an Omni branch and runs `omni models validate`. A validation error blocks the merge.
2. **Regression queries:** a fixed set of queries runs before and after each change. Numbers must not move unless the change was meant to move them.
3. **Start with low-risk edits:** descriptions, synonyms, `ai_context`, sample questions. Only then new measures (those change numbers).
4. **Human review on every PR**, with each new definition citing where it came from.
5. **Git is the source of truth.** No Claude writes straight to Omni main.

The Omni CLI already supports every step: `create-branch`, `yaml-create`, `validate`, `merge-branch`, `yaml-get`.

## Steps
| # | Step | Who | Status |
|---|---|---|---|
| 0 | Ask William for his branch-validate-main workflow so we don't rebuild it | You | To do |
| 1 | Pick the target topic and a baseline. Recommended: a stripped-down copy of `analytics_prod_ecomm__sales` (no descriptions, synonyms or AI context) so improvement is measurable, with the original as the answer key | You decide, Claude builds | To do |
| 2 | Seed the repo: pull the model YAML from Omni into `Plan 2/model/` | Claude | To do |
| 3 | Write the validate script: branch, push YAML, validate, report | Claude | To do |
| 4 | Baseline: run 15 questions through Omni's AI and through Claude alone; score | Claude + you | To do |
| 5 | Enrichment round 1: Claude proposes a PR from its knowledge; validate; merge on a branch | Claude, you review | To do |
| 6 | Re-run the same 15 questions; compare to baseline | Claude + you | To do |
| 7 | Turn the script into a GitHub Action (needs an Omni API key as a secret) | Claude | To do |
| 8 | Write findings: accuracy change, validation failure rate, hours per cycle | Claude + you | To do |

## What you have to set up
- Your call on the target topic and which knowledge sources Claude may use (and what's off limits, e.g. customer data).
- An Omni API key for the GitHub Action (a local sign-in works until then; it's already set up as the `willyc` profile).
- Optional: Omni's own git integration. It isn't configured on this model, and we don't need it because the script pushes YAML through the API.
- The 15-question set with expected answers.

## Tools: free vs paid
| Tool | Used for | Cost |
|---|---|---|
| Omni | The semantic layer being improved | Existing, paid |
| Omni CLI and API | Branches, validate, push YAML | Included |
| GitHub (private repo, Actions) | Source of truth, PR checks | Free tier is enough for this |
| Claude Code | Proposes the YAML changes | Existing |
| Snowflake MCP | Ground-truth numbers | Existing |

## Risks and open questions
- **Drift:** someone edits in Omni's UI and Git falls out of date. Rule: all changes go through Git. Pull `yaml-get` on a schedule to detect drift.
- **Wrong definitions:** Claude can state something plausible but false. Every definition cites a source, and a person approves it.
- **Honest benefit:** Omni may already do much of this natively (AI context, pulling from Notion). The experiment compares against that, not against nothing.
- **Sensitive context:** Slack, call notes and customer data should not become public-facing descriptions. Decide what's allowed in step 1.

## Man hours (estimates; replace with measured numbers)
| Phase | Estimate |
|---|---|
| Steps 0-3 (William's workflow, seed repo, validate script) | 2-3 h |
| Steps 4-6 (baseline, enrich, re-score) | 4-6 h |
| Step 7 (GitHub Action) | 1-2 h |
| Step 8 (findings) | 2-3 h |

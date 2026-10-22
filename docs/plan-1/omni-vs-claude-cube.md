# Omni vs Claude + Cube, end to end

*2026-10-22. Route 4 (Omni) and route 3 (Claude + Omni) against route 2 (Claude + Cube Core). **Tested** = we ran it ([findings.md](findings.md)). **Documented** = Omni's or Cube's docs, linked, not run by us. **Not measured** = no number yet.*

## Bottom line

Cube is a good **engine** and Omni is a **product**. Cube gave us correct, fast, cheap answers and open, standard APIs. What Cube does not give you is everything around the engine: who is allowed to change a metric, who is asking, whether a change is safe before it ships, who can use it without an engineer, and a place to see what people asked. In our build those pieces were either missing or ours to write. Omni ships them, and the cost is a slower, more expensive AI path, a topic-curation job, and a vendor.

So the honest framing is not "Cube is bad". It is: **Cube is great at the semantic layer and weak at the operating model around it; Omni is the reverse, with a heavier AI path.** The decision depends on whether the customer has a data engineer to spare and who needs to touch metrics.

## At a glance

| Dimension | Claude + Cube | Omni | Edge |
|---|---|---|---|
| **Setup** | Tested: about one session plus about an hour for Snowflake; Docker, a Python MCP wrapper, a Snowflake token and role, plus fixes for macOS permissions and an `mcp` 2.x break. Hours not logged | Documented: managed product; Claude connects with the official connector in 4 steps ([docs](https://docs.omni.co/ai/mcp/claude-desktop)); the model still has to exist or be built | Omni |
| **Hosting** | You host: a container, plus a hosted MCP if dashboards must be live for others (our local server wasn't live for viewers, Tested). Cube Cloud is the managed route (Free $0, Starter $40, Premium $80 per developer per month, per [cube.dev/pricing](https://cube.dev/pricing)) | Documented: hosted on AWS or Azure in one chosen region per organization ([regions](https://docs.omni.co/administration/security/cloud-regions)); docs don't describe self-hosting; SOC 2 Type II | Depends: Cube if you must self-host; Omni if you don't want to |
| **Data engineer** | Required for setup, every metric change, the MCP wrapper, tokens and hosting. Tested: the engineer's edit is 3.4 s; the request-to-live path was not timed | Documented: modelers own the model and review changes; business users can add fields in a workbook and promote them ([docs](https://docs.omni.co/modeling/develop/promotion)) | Omni |
| **Changing a metric** | Tested: 1 file, 1 block, 3.4 s, 3 of 3 dashboard queries updated, 0 fixed by hand. New metric queryable in 0.8 s | Tested (modeler, CLI): 1 block, 5.6 s on a branch, validated, 3 of 3 updated. Business-user UI path is Documented, not run | Tie on speed; **Omni on who can do it** |
| **Safety before shipping** | Tested gap: a broken column loads fine and fails only when queried (1.9 s, raw Snowflake error); no pre-merge validation | Tested: `validate` caught the broken field in 1.5 s with the YAML path and an auto-fix; Content Validator finds broken dashboards (Documented) | Omni |
| **Permissioning** | Tested: dev mode accepts no or forged tokens. Production mode + native `access_policy` fails closed (no claim returns nothing); `queryRewrite` fails open. Our MCP wrapper had one shared identity and no auth on HTTP | Documented: access filters from user attributes, grants, SAML/OIDC/SCIM, MCP runs as the signed-in user ([docs](https://docs.omni.co/ai/mcp/authentication)). Our own test was blocked (needs an Organization API key) | Omni on completeness; Cube can be correct but you build the identity layer |
| **Interface** | Tested: Playground for engineers; Claude Dashboards for building by chat (one prompt built a KPI row and 5 charts, SQL on every tile); no editor, no schedules | Documented: workbooks, dashboards, folders, scheduled deliveries, downloads, embedding, model IDE with branch mode ([IDE](https://docs.omni.co/modeling/develop/guides/model-ide)) | Omni for business users |
| **Upkeep** | Not measured. Known tasks: image updates (`:latest` moves), rotating the Snowflake token and API secret, keeping the MCP copy in sync, hosting and auth, writing CI, logging | Not measured. Documented tasks: schema refresh when tables change, Content Validator after changes, cache policies, topic curation (`ai_context`, `ai_fields`), evals ([maintenance](https://docs.omni.co/modeling/develop/schema-refreshes)) | Likely Omni, unproven |
| **Answer accuracy** | Tested: 100% (30/30), consistency 100% | Tested: 93.3% (28/30) pointed at the Sales topic, **36.7% when the agent chose the topic**; consistency 90% | Cube, on this test |
| **Speed per answer** | Tested: 9.0 s end to end; query 0.37 s cold, 0.015 s cached | Tested: 34-37 s through the agent; semantic query median 1.76 s | Cube |
| **Cost per answer** | Tested: $0.048 model cost | Tested: about $0.16 model cost; AI credits beyond the allotment bill at $1.00 each ([docs](https://docs.omni.co/ai/settings/usage)), not measured | Cube |
| **Auditability** | Tested: SQL visible; Git shows who changed what in 0.08 s (engineers only); no question logs or usage analytics | Tested: agent returns SQL and a definitions table. Documented: AI Hub, AI logs, evals, revision history with restore | Omni |
| **Sharing** | Tested: private by default; our Cube queries weren't live for others. Needs a hosted, secured MCP | Documented: Share dialog roles, folders, deliveries, PDF/CSV, embed ([docs](https://docs.omni.co/share)) | Omni |
| **Openness and lock-in** | Open source core, open YAML, REST/GraphQL/SQL APIs, any BI tool or LLM can sit on it | Proprietary model language and product; API and CLI are open | Cube |

## End to end, in the order you asked

**Setup.** With Claude Code porting the Omni topic and writing the tests, the Cube build was fast, and the port was mostly mechanical. The slow, unglamorous parts were everything not in the YAML: a Snowflake role that could see the schema, a container, a wrapper, and Desktop's quirks. Omni has fewer moving parts to assemble, but someone still has to model the data and curate topics.

**Hosting.** This is the sharpest difference for a Claude Dashboard. A Cube MCP on a laptop only works for the person who built it; to make a dashboard live for others the MCP must be hosted remotely (third-party coverage of the beta, to be confirmed against Anthropic's docs), secured, and given per-user identity. We proved the HTTP route works and had no auth on it. Omni's connector is already remote. Cube Cloud closes much of this gap for money.

**The data engineer.** In the Cube world the engineer is the product's operator: they port definitions, edit metrics, issue tokens, host the MCP and write the checks Cube doesn't have. Omni moves day-to-day metric creation toward modelers and business users, with review. For a company with no spare engineer, this is the deciding factor. For one with a strong data team, it may be a feature, not a cost.

**Upkeep time.** We have no weekly-hours log, so we won't quote one. What we can say is where the work lives: Cube's upkeep is mostly infrastructure and security plumbing you own; Omni's is mostly model and topic hygiene. A fair test needs a few weeks of logging per route (tracked).

**The interface.** Cube has two surfaces: the Playground, which is for engineers, and whatever you build on the API. In our setup the "UI" for business users was Claude Dashboards, built by chat, with no editor and no schedules. Omni is a full BI tool: a modeling IDE with branches, a workbook where users can build and promote fields, folders, deliveries and embedding.

**Speed to develop a metric.** On raw speed they are the same order of magnitude: seconds to edit, validate and see it. The meaningful difference is that Cube's validation is *after* you query and Omni's is *before* you merge, and that in Cube only someone who can edit YAML can do it. A new Cube metric was queryable in 0.8 s; the same change on an Omni branch took 5.6 s including validation.

**Permissioning.** Cube can do row-level security correctly (production mode and `access_policy`, which fails closed), but out of the box it did not: dev mode ignored forged tokens, `queryRewrite` failed open, and our MCP wrapper gave everyone the same identity. Per-user security is code and configuration you write. Omni's model is documented end to end (user attributes, access filters, grants, SSO and SCIM, MCP as the signed-in user); we could not independently test it.

## Where Cube is great

- **Correct, fast, cheap answers:** 100% accuracy and consistency; $0.048 and 9 s per answer; 15 ms cached; pre-aggregations worked in Core.
- **Open and portable:** open YAML, REST, GraphQL and SQL APIs; any LLM or BI tool can sit on it; no vendor lock-in.
- **Code-first change control:** Git history, diff and revert came for free (0.08 s to trace a change).
- **Native fail-closed row security** once configured properly.
- **Cost:** Core is free; Cube Cloud has a free tier with an MCP server.
- **Flexibility:** you can run it in your own cloud, and shape it any way you like.

## Where Cube is a downfall

- **Nothing around the engine:** no validation before a broken definition ships, no usage analytics or question logs, no business-user editing, no scheduling or folders.
- **Insecure defaults:** dev mode disables auth; the exclusion rule was advisory text until we built `net_revenue`.
- **You own the identity boundary:** one shared token by default; an HTTP MCP with no auth; real users need OAuth and a token issuer.
- **Dashboards aren't live for others** without a hosted, secured MCP.
- **Key-person risk:** a person has to keep it running and be the route for every metric request.
- **AI context is a convention:** synonyms and `ai_context` live in free-form `meta` and only work because our wrapper reads them.

## Where Omni is great

- **The full product in one place:** model, UI, AI chat, permissions, deliveries, embedding, history.
- **Self-service with governance:** business users create fields in a workbook; modelers review and promote (Documented).
- **Validation and repair:** `validate` plus Content Validator catch breakage before and after a change (Tested for validate).
- **AI built on the model:** topics, `ai_context`, `ai_fields`, synonyms, sample queries, evals, AI Hub ([docs](https://docs.omni.co/ai/index)).
- **Security model:** documented end to end, with the MCP running as the signed-in user.

## Where Omni has downsides or open questions

- **Topic overlap is a real risk:** our instance has two topics that disagree 2x on revenue, and the unguided agent used the wrong one (36.7% accuracy). Omni's docs say the MCP can be scoped to a topic through setup headers; not tried.
- **The AI path is slower and costs more per answer:** about $0.16 and 34-37 s through the agent, against $0.048 and 9 s on Cube. AI usage is credit-based beyond an allotment.
- **MCP is not guaranteed to equal the in-app chat:** the docs say both use the same AI pipeline but promise no identical answers; we measured only the MCP.
- **Hosting is Omni's:** single region per organization; docs don't describe self-hosting or give an uptime commitment.
- **Proprietary model and a vendor:** moving off Omni means rewriting the model. Cube's YAML is open.
- **Context guides, not guarantees:** Omni's own docs say AI context is not a guarantee that every instruction will be followed.
- **Much of our Omni evidence is Documented, not Tested:** the business-user UI path, restricted-user security, sharing and upkeep were not run by us.

## Who should pick what

- **Choose Omni** when metrics must be changed by people who are not engineers, when security and audit must work from day one, when there's no engineer to own infrastructure, and when the audience needs a real BI interface.
- **Choose Cube (with Claude)** when you already have data engineers, want an open, headless layer under several tools, need to self-host, or care most about cost and speed per query.
- **Be honest with a customer about the gap in the middle:** a Claude Dashboard on a local Cube is a good demo and a poor shared product until you host it, secure it and give it identity.

## What would sharpen this

Hours logged per route over a few weeks, a business-user trial in Omni, an Omni restricted-user test (needs an Organization API key), the Omni topic-scoping fix, and a hosted Cube MCP with per-user OAuth. All are in the [tracker](../project-tracker.csv).

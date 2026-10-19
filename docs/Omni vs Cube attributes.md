# Omni attributes vs Cube

Every attribute Omni's docs list for models, topics, views, relationships, dimensions and measures, with whether Cube Core has an equivalent.

**Legend:** **Yes** = native equivalent. **Sorta** = partial, convention only (free-form `meta`), global instead of per-object, or Cube Cloud only. **No** = nothing equivalent. **?** = not verified.

**Sources (checked 2026-10-19):** Omni attribute lists from Omni docs via `searchOmniDocs` (docs.omni.co/modeling). Cube from docs.cube.dev/reference/data-modeling (cube, view, dimensions, measures). I did not test any "Yes" or "Sorta" against our running Cube container, so a feature could differ by Cube version.

**Correction to the earlier Learnings table:** Cube's docs *do* mention `meta.ai_context` "for AI agents", so that is a documented convention, not nothing. Cube also has view `default_filters`, which enforce a filter on every query against a view. That is the closest native answer to "always apply a filter at query time" in the model files.

**Headline:** Cube matches Omni on structure (SQL, joins, descriptions, access, caching) and exceeds it on performance features. The gap is the AI-facing layer: `synonyms`, `all_values`, `sample_values`, `sample_queries`, `ai_fields` and `ai_chat_topics` have no real Cube equivalent, so that context has to live in free-form `meta` and be read by our own code.


## Topic parameters (Omni topic file)

| Omni attribute | In Cube? | Cube equivalent / note |
|---|---|---|
| `access_filters` | **Yes** | `access_policy` row-level filters, or `queryRewrite` in `cube.js` (we use this for country) |
| `ai_context` | **Sorta** | `meta.ai_context` is a documented key "for AI agents" in Cube docs, but Core's API doesn't act on it. Our MCP wrapper reads it |
| `ai_fields` | **Sorta** | `public`, view `includes`/`excludes` limit what anyone can query, not AI-specific |
| `always_having_filters / always_having_sql` | **Sorta** | `queryRewrite` can inject measure filters; no dedicated parameter |
| `always_where_filters / always_where_sql` | **Yes** | View `default_filters` (with optional `unless`), or `queryRewrite` |
| `auto_run` | **Sorta** | `meta.auto_run: false` on a view, Cube Cloud workbooks only |
| `base_view / joins / relationships` | **Yes** | Cube `joins` plus the view's `cubes` join paths |
| `base_view_label` | **Sorta** | View `title` |
| `cache_policy` | **Yes** | Cube `refresh_key` |
| `default_filters` | **Sorta** | View `default_filters` are enforced, not removable (except via `unless`); Cloud has `meta.default_ui_filters` for editable ones |
| `default_row_limit` | **Sorta** | Global API/DB limit settings, not per view |
| `description` | **Yes** | `description` |
| `display_order` | **Sorta** | Order of members in a view / folders |
| `extends` | **Yes** | `extends` on cubes and views |
| `fields` | **Yes** | View `includes` / `excludes` |
| `group_label` | **Sorta** | View `folders` |
| `hidden` | **Yes** | `public: false` |
| `hidden_unless_access_grants / required_access_grants` | **Sorta** | `access_policy` (groups, member-level access) |
| `label` | **Yes** | `title` |
| `owners` | **No** |  |
| `sample_queries` | **No** | Nothing equivalent in Core |
| `skills (topic AI instructions)` | **No** | Closest is `meta.ai_context` |
| `tags` | **Sorta** | Free-form `meta` only |
| `template` | **Sorta** | Abstract cubes via `extends` |
| `views (topic-specific view customization)` | **Sorta** | View `cubes` entries can override `title`, `description`, `format`, `meta` |
| `warehouse_override` | **Sorta** | Per-cube `data_source` |
| `week_start_day` | **Sorta** | Custom `granularities` with an origin |

## Model-file parameters (Omni)

| Omni attribute | In Cube? | Cube equivalent / note |
|---|---|---|
| `ai_chat_topics` | **No** | No list of which models/views the AI may use; exposure is `public` |
| `access_grants` | **Yes** | `access_policy` groups and roles |
| `default_topic_access_filters` | **Sorta** | Global `queryRewrite` |
| `cache_policies (named, scheduled)` | **Sorta** | `refresh_key` per cube; no named reusable policies |
| `aggregates (materialized_query)` | **Yes** | `pre_aggregations` (more developed than Omni's) |

## View parameters (Omni view file)

| Omni attribute | In Cube? | Cube equivalent / note |
|---|---|---|
| `ai_context` | **Sorta** | `meta.ai_context` on cube/view (see above) |
| `aliases` | **No** |  |
| `catalog / schema / table_name` | **Yes** | `sql_table` (fully qualified) or `sql` |
| `custom_compound_primary_key_sql` | **Sorta** | Composite key via one concatenated dimension marked `primary_key` |
| `default_drill_fields / default_drill_query` | **Sorta** | `drill_members` is set per measure |
| `description / label / name / hidden / extends / tags` | **Yes** | `description`, `title`, `name`, `public`, `extends`; tags only via `meta` (Sorta) |
| `display_order / folder / schema_label` | **Sorta** | View `folders`; no schema label |
| `fill_fields` | **?** | Not verified |
| `ignored` | **Sorta** | `public: false` |
| `materialized_query` | **Yes** | `pre_aggregations` |
| `query / sql` | **Yes** | Cube `sql` |
| `required_access_grants` | **Sorta** | `access_policy` |
| `template` | **Sorta** | Abstract cubes via `extends` |
| `uploaded_table_name` | **No** |  |

## Relationship parameters (Omni)

| Omni attribute | In Cube? | Cube equivalent / note |
|---|---|---|
| `join_from_view / join_to_view / on_sql / relationship_type` | **Yes** | `joins` with `sql` and `relationship` (one_to_one, one_to_many, many_to_one) |
| `join_type` | **Sorta** | Cube joins are directional; no join-type choice found in docs |
| `join_from_view_as / join_to_view_as (+ _label) / where_sql` | **?** | Not verified |
| `id / reversible` | **?** | Not verified |

## Dimension parameters (Omni)

| Omni attribute | In Cube? | Cube equivalent / note |
|---|---|---|
| `sql, description, label, format, links, primary_key` | **Yes** | `sql`, `description`, `title`, `format`, `links`, `primary_key` |
| `hidden` | **Yes** | `public: false` |
| `extends` | **Yes** | Via cube `extends` |
| `synonyms` | **Sorta** | No native field. Free-form `meta.synonyms`; we read it in the MCP wrapper |
| `ai_context` | **Sorta** | `meta.ai_context` |
| `all_values / sample_values` | **No** | No value hints for filters/AI |
| `suggest_from_field / suggest_from_topic / suggestion_list` | **No** | No filter-suggestion config |
| `tags / group_label / view_label` | **Sorta** | `meta`, view `folders`, view `title` |
| `timeframes / week_start_day / convert_tz / custom_calendar / duration` | **Sorta** | `granularities`, query `timezone`, calendar cubes |
| `drill_fields` | **Sorta** | `drill_members` on measures |
| `groups / bin_boundaries` | **Sorta** | `case` conditions on a dimension |
| `order_by_field` | **Sorta** | `order` sets a default direction only, not sort-by-another-field |
| `required_access_grants` | **Sorta** | `access_policy` member-level rules |
| `level_of_detail` | **Sorta** | `sub_query`, multi-stage measures |
| `aliases, colors, faceting, markdown, filter_single_select_only, parent_field, skip_parent_label, dynamic_top_n, bin/format extras` | **No** |  |
| `display_order, ignored, custom_primary_key_sql_for_quick_aggs, ignore_from_extended` | **?** | Not verified or no direct equivalent |

## Measure parameters (Omni)

| Omni attribute | In Cube? | Cube equivalent / note |
|---|---|---|
| `sql, description, label, format, links, filters` | **Yes** | `sql`, `description`, `title`, `format`, `links`, measure `filters` |
| `aggregate_type` | **Yes** | `type` (sum, avg, count, count_distinct, ...) |
| `hidden` | **Yes** | `public: false` |
| `synonyms / ai_context / tags / group_label / view_label` | **Sorta** | Free-form `meta`, view `folders` and `title` |
| `all_values / sample_values / suggest_* ` | **No** |  |
| `drill_fields / drill_queries` | **Sorta** | `drill_members` |
| `required_fields` | **Sorta** | Dependencies resolve through SQL references |
| `level_of_detail` | **Sorta** | Multi-stage measures (`multi_stage`, `grain`) |
| `required_access_grants` | **Sorta** | `access_policy` |
| `aliases, colors, markdown, custom_primary_key_sql` | **No** |  |

## Cube has, Omni doesn't list

| Cube feature | | Cube parameter |
|---|---|---|
| Pre-aggregations (rolling window, partitions) | | `pre_aggregations` |
| Segments / hierarchies | | `segments`, `hierarchies` |
| Rolling windows / multi-stage / time shift | | `rolling_window`, `multi_stage`, `time_shift` |
| Data masking | | `mask` with `access_policy` |
| Switch and geo dimension types, currency | | `type: switch`, `geo`, `currency` |
| SQL, REST, GraphQL APIs from one model | | Playground tabs: SQL API, REST API, GraphQL API |

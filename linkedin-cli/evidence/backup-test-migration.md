# Backup test migration

All active backup regressions live in `tests/test_linkedin.mjs` and exercise the native single-file CLI. The historical 43-test Python file is retained unchanged at `~/code/scripts/archive/test_backuplinkedin.py`, alongside its archived implementation. It is removed from the active `just test` graph.

These are behavioral ports, not imports of the archived module: Node fixtures use a fresh isolated headless Chromium profile, blocked/mocked network, and native CDP. Legacy Python-specific argument names and import plumbing are retired. Native CLI/schema and `paths` tests exercise their supported equivalents.

| Historical Python test | Native JavaScript coverage |
| --- | --- |
| `test_page_cdp_url_prefers_existing_linkedin_target` | `native profile lookup bootstrap uses an existing LinkedIn tab and does not close the borrowed target` |
| `test_page_cdp_url_creates_target_when_linkedin_is_not_open` | `native bootstrap creates a background source if no LinkedIn tab is open and validates loopback endpoints` |
| `test_page_cdp_url_preserves_direct_websocket` | Retired Python direct-WebSocket CLI entry point; native loopback CDP endpoint validation and owned/borrowed target tests cover the supported transport. |
| `test_default_output_path_follows_home` | `paths reports effective locations and configuration without credentials, browser or database writes` |
| `test_exact_linkedin_id_timestamp` | `native backup dates preserve Snowflake precision, relative periods, exclusive until and dry-run file safety` |
| `test_new_snapshot_counts_can_decrease_to_zero` | `backup merge keeps rich fields, accepts zero/false, and preserves prior partial repost details` |
| `test_parse_analytics_extracts_summary_and_engagement_counts` | `analytics distinguishes discovery value-before-label from engagement label-before-value` |
| `test_parse_analytics_requires_discovery_and_impressions` | `analytics keeps absent and withheld metrics unknown, and rejects a non-analytics page` |
| `test_parse_analytics_retries_unreadable_present_metric_but_accepts_withheld_dash` | `native detailed analytics handles misleading Discovery text, sparse viewers, video, withholding and delayed zero` |
| `test_parse_analytics_keeps_profile_viewer_rows_and_sparse_metrics` | `native detailed analytics handles misleading Discovery text, sparse viewers, video, withholding and delayed zero` |
| `test_parse_analytics_extracts_video_performance_only_when_present` | `native detailed analytics handles misleading Discovery text, sparse viewers, video, withholding and delayed zero` |
| `test_parse_demographics_stops_before_analytics_tools_and_skips_navigation` | `detailed analytics keeps video, viewers, all demographic rows and delayed zero metrics` |
| `test_select_analytics_posts_filters_author_date_and_reposts` | `backup analytics selection excludes reposts/other authors and uses stable activity dates` |
| `test_parse_period_supports_iso_relative_and_ago` | `native backup dates preserve Snowflake precision, relative periods, exclusive until and dry-run file safety` |
| `test_merge_row_updates_analytics_and_allows_empty_reposts` | `backup merge keeps rich fields, accepts zero/false, and preserves prior partial repost details` |
| `test_update_jsonl_preserves_unselected_rows_and_is_idempotent` | `archive writes are atomic/idempotent, keep historical rows, reject corruption and serialize writers` |
| `test_describe_and_cli_expose_analytics_options` | `backup CLI validates archive options and supports bounded unlimited backup and raw JSONL export` |
| `test_analytics_text_waits_for_non_loading_stable_hydrated_snapshot` | `native detailed analytics handles misleading Discovery text, sparse viewers, video, withholding and delayed zero` |
| `test_analytics_text_defers_incomplete_visible_metric_until_zero_arrives` | `native detailed analytics handles misleading Discovery text, sparse viewers, video, withholding and delayed zero` |
| `test_extract_analytics_follows_reposts_link_scrolls_and_preserves_rich_duplicate` | `native detailed analytics follows the actual public-reposts link and preserves richer duplicate rows` |
| `test_extract_analytics_zero_reposts_does_not_open_reposts_link` | `native analytics zero reposts skips list navigation and missing/private rows remain incomplete` |
| `test_extract_analytics_marks_private_or_missing_reposts_incomplete` | `native analytics zero reposts skips list navigation and missing/private rows remain incomplete` |
| `test_update_analytics_dry_run_does_not_write` | `native backup dates preserve Snowflake precision, relative periods, exclusive until and dry-run file safety` |
| `test_direct_cdp_click_delivers_one_native_dom_click` | `native DOM clicks deliver one event and keyed elements survive real sibling insertion/removal` |
| `test_sdui_extracts_post_and_nested_comments_from_semantic_dom` | `native SDUI backup retains author, text, media, badges, reactions and nested replies` |
| `test_reposts_js_extracts_repost_cards_and_deduplicates_ids` | `native public repost extraction deduplicates identities and retains visible counts/body` |
| `test_reposts_more_js_clicks_present_loader_and_handles_removed_loader` | `native detailed analytics follows the actual public-reposts link and preserves richer duplicate rows` |
| `test_legacy_extract_still_handles_basic_post` | `native legacy backup still extracts full commentary and stable activity identity` |
| `test_sdui_selector_and_post_id_are_keyed_to_card_identity` | `keyed native DOM locators survive React card replacement and sibling reordering` |
| `test_comment_loader_waits_for_async_hydration` | `native comment loaders wait for hydration and associate flat sibling replies with explicit parents` |
| `test_comment_loader_maps_flat_sdui_reply_to_preceding_parent` | `native comment loaders wait for hydration and associate flat sibling replies with explicit parents` |
| `test_page_cdp_url_requires_linkedin_page_with_websocket` | `native bootstrap creates a background source if no LinkedIn tab is open and validates loopback endpoints` |
| `test_keyed_cdp_elements_survive_reordering_and_removal` | `native DOM clicks deliver one event and keyed elements survive real sibling insertion/removal` |
| `test_connect_enables_focus_emulation_without_activating_tab` | `native browser sessions create owned background targets with focus emulation and preserve borrowed tabs` |
| `test_close_closes_socket_even_if_focus_reset_fails` | `native session cleanup closes every owned socket and browser socket after a target-close failure` |
| `test_sdui_extracts_videojs_sources_poster_and_duration` | `native backup extracts usable video sources, poster and duration instead of blob thumbnails` |
| `test_sdui_extracts_repost_actor_and_supplied_urn` | `native SDUI reposts distinguish the reposter from the original author and accept verified URNs` |
| `test_resolve_post_urn_captures_permalink_without_touching_clipboard` | `native permalink fallback restores clipboard methods and never writes to the user clipboard` |
| `test_post_ugc_js_returns_unique_react_reaction_state_id` | `native UGC discovery rejects ambiguous React state and uses verified archive parents before menus` |
| `test_resolve_post_urn_uses_verified_ugc_parent_before_clipboard` | `native UGC discovery rejects ambiguous React state and uses verified archive parents before menus` |
| `test_apply_reply_parents_links_new_and_previously_visible_siblings` | `native backup restores explicitly observed flat sibling replies without guessing unrelated comments` |
| `test_apply_reply_parents_does_not_guess_without_observed_mapping` | `native backup reply inference requires an observed parent and a complete sibling group` |
| `test_apply_reply_parents_does_not_assign_unrelated_adjacent_comments` | `native backup reply inference requires an observed parent and a complete sibling group` |

# Business Review — 2026-09-28 01:22 UTC

## Revenue
- **TPT**: ERROR — TPT session expired (.tpt_session.json no longer valid). Refresh it manually once: python publish_tpt.py --save-session (automated form login is disabled here — it has triggered TPT bot detection and an account lock before).
- **Gumroad**: AUD 0 net, 0 sale(s)
- **TES**: GBP 6.29 net, 2 sale(s)
- **Combined (not currency-converted)**: AUD0 + GBP6.29

## Catalog — 27 live unit(s)
- ai_literacy_cybersecurity_bundle
- computer_systems_networks_bundle
- creative_media_game_design_bundle
- data_databases_bundle
- data_skills_ai_bundle
- digital_media_ux_bundle
- game_design_coding_bundle
- programming_foundations_bundle
- robotics_algorithms_bundle
- start_of_year_bundle
- staying_safe_online_bundle
- web_design_ux_bundle
- year7_ai_literacy_unit1
- year7_algorithms_unit1
- year7_cybersecurity_unit1
- year7_data_representation_unit1
- year7_databases_unit1
- year7_digital_media_unit1
- year7_digital_systems_unit1
- year7_game_design_unit1
- year7_networks_hardware_unit1
- year7_orientation_unit1
- year7_python_programming_unit1
- year7_robotics_physical_computing_unit1
- year7_spreadsheets_unit1
- year7_ux_design_unit1
- year7_web_design_unit1

## Recent activity (last 8 commits)
- 2026-09-27 Add follow-store CTA to all 20 lead magnets; fix duplicate Pinterest pins from a stale-checkout mistake; mark UX Design/Orientation wave 3 posted
- 2026-09-27 Fix product 17046914: literal <img>/<a>/<ol>/<ul>/<li> text broke TPT's description editor; catalogue retag now 169/169
- 2026-09-26 Retag live TPT catalogue to Grades 6-8 (168/169 verified); log results and open items
- 2026-09-26 Fix TPT edit-product saves (real cause: 'Upload thumbnails later' default, not reCAPTCHA); add retag_tpt_catalog.py
- 2026-09-25 Resource Drop: publish Lesson 5 lead magnet for year7_data_representation_unit1
- 2026-09-23 Marketing Push: post 9 backlogged Pinterest pins across 3 units now that the 50-draft cap has cleared
- 2026-09-22 Log queue-empty for scheduled New Unit Production run
- 2026-09-21 Document that the retroactive title fix does NOT actually work -- TPT's edit-product form is blocked by reCAPTCHA, confirmed via network trace

## Open items / decisions waiting on you
- TES Unit 1 (AI series) still has the presenter-placeholder / 'Unknown' quote cosmetic bug -- TPT side fixed 2026-07-19, TES side not attempted yet (unfamiliar edit flow, real risk of repeating the Networks & Hardware licence-corruption mistake without live oversight).
- TES has a genuine duplicate: 'Data Shapes the AI World – Lesson 1' exists as two separate resources (13432831, 13432796). Needs explicit delete authorization -- not actioned autonomously.
- TES resource 13445828 is permanently broken (TES's own 'temporary disruption' error on every step, confirmed non-transient). Likely dead/orphaned; candidate for deletion, needs authorization.
- Off-brand Gumroad products (A$129 SWMS, ADHD guide) still share the teaching storefront -- undecided, business-judgment call.
- Shelved AI-series Units 3-8 are deactivated on TPT (2026-07-19) but still live on TES (9 resources, Unit 1 only per the 2026-07-18 audit) -- Unit 1's content itself was confirmed clean, no action needed there.
- No real unattended scheduling exists yet -- Claude Code cloud scheduled tasks (claude.ai/code/scheduled) would need setup via the web UI; this script is designed to be the payload for that once set up.

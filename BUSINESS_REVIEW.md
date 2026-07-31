# Business Review — 2026-07-31 03:28 UTC

## Revenue
- **TPT**: ERROR — TPT session expired (.tpt_session.json no longer valid). Refresh it manually once: python publish_tpt.py --save-session (automated form login is disabled here — it has triggered TPT bot detection and an account lock before).
- **Gumroad**: AUD 0 net, 0 sale(s)
- **TES**: GBP 0.3 net, 1 sale(s)
- **Combined (not currency-converted)**: AUD0 + GBP0.3

## Catalog — 0 live unit(s)

## Recent activity (last 8 commits)
- 2026-07-31 Fix TPT false-negative integrity check and TES cookie-banner timeout; add TPT_SESSION_JSON env fallback
- 2026-07-31 Log scheduled business review: TES verified working again, Gumroad clean, TPT still blocked by missing session
- 2026-07-31 Force channel="chromium" in cloud_launch_kwargs() -- fixes silent headless_shell substitution
- 2026-07-31 Log scheduled business review: Gumroad clean, TPT/TES blocked by browser TLS reset
- 2026-07-31 Add push test entry to AUTONOMOUS_LOG.md
- 2026-07-31 Log today's cloud-automation diagnostic findings to AUTONOMOUS_LOG.md
- 2026-07-31 Cap Chromium to TLS 1.2 in cloud sandbox -- proxy can't handle TLS 1.3 ClientHello
- 2026-07-31 Fix Chromium hardcoded channel + missing proxy passthrough for cloud automation

## Open items / decisions waiting on you
- TES Unit 1 (AI series) still has the presenter-placeholder / 'Unknown' quote cosmetic bug -- TPT side fixed 2026-07-19, TES side not attempted yet (unfamiliar edit flow, real risk of repeating the Networks & Hardware licence-corruption mistake without live oversight).
- TES has a genuine duplicate: 'Data Shapes the AI World – Lesson 1' exists as two separate resources (13432831, 13432796). Needs explicit delete authorization -- not actioned autonomously.
- TES resource 13445828 is permanently broken (TES's own 'temporary disruption' error on every step, confirmed non-transient). Likely dead/orphaned; candidate for deletion, needs authorization.
- Off-brand Gumroad products (A$129 SWMS, ADHD guide) still share the teaching storefront -- undecided, business-judgment call.
- Shelved AI-series Units 3-8 are deactivated on TPT (2026-07-19) but still live on TES (9 resources, Unit 1 only per the 2026-07-18 audit) -- Unit 1's content itself was confirmed clean, no action needed there.
- No real unattended scheduling exists yet -- Claude Code cloud scheduled tasks (claude.ai/code/scheduled) would need setup via the web UI; this script is designed to be the payload for that once set up.

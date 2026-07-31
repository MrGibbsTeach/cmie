# Autonomous Run Log

Running log for the unattended scheduled jobs (business review, new unit,
marketing push, resource drop) covering the period the business owner is
away. Newest entries at the top. Each entry: date, job name, what happened,
anything that needs a human decision.

Hard boundaries every job must respect, no exceptions, regardless of what
is found during a run:
- Never delete anything on any platform (TPT, Gumroad, TES, Pinterest)
- Never edit the Categories or Licence step on an already-published TES
  resource (a 2026-07-19 incident corrupted a live paid listing to FREE
  doing exactly this — see project memory `project_direction_change.md`)
- Never touch the off-brand Gumroad products (SWMS guide, ADHD guide)
- No new platforms, no pricing changes, no strategic direction changes
- If something needs a human decision (looks like a bug, a duplicate, an
  ambiguous state), log it clearly below and move on — do not attempt to
  resolve it unilaterally

---

(entries below this line, newest first)

## 2026-07-31 — Cloud Chromium/proxy fix landed and verified; git push permission still blocking

Session goal: get the 4 paused routines (Business Review, New Unit Production,
Marketing Push, Resource Drop — all `enabled: false` since 2026-07-20) back to
a genuinely working state, not just re-enabled and failing quietly again.

**Root cause #1, fixed and verified live**: every Playwright launch site in
the repo either hardcoded `channel="chrome"` (no real Chrome binary in the
cloud container) or had no way to pass the sandbox's egress proxy explicitly
(Chromium doesn't auto-read `HTTP_PROXY`/`HTTPS_PROXY` the way curl/urllib
do). Added `cloud_launch_kwargs()`/`cloud_context_kwargs()` in
`cmie/publishing/browser.py` (no-op locally, activates only when a proxy env
var is present) and wired it into every launch site: `browser.py`,
`cmie/publishing/tpt.py`, `check_revenue.py`, `publish_pinterest.py`,
`verify_tpt_listings.py`, `verify_tes_listings.py`, `verify_pinterest_pins.py`,
`cmie/connectors/tpt.py`. Commit `cd7354e`.

A live diagnostic session run directly in the Claude Code cloud environment
(`env_01DJK4aBcVAJB3m7hdsLorh1`) found this first fix was necessary but not
sufficient: the proxy resets the connection right after Chromium's TLS 1.3
ClientHello, *before* any certificate is exchanged — so
`--ignore-certificate-errors` never got a chance to matter. Isolated via
netlog analysis (ruled out the PQ/Kyber key-share extension specifically);
capping Chromium to TLS 1.2 (`--ssl-version-max=tls1.2`) fixed it cleanly for
both a plain test URL and a real teacherspayteachers.com page load. Added to
the same shared helper. Commit `12b07a7`. **Chromium can now genuinely reach
the internet from this cloud environment — confirmed by a real page load, not
inferred.**

**Root cause #2, found, NOT fixed — needs a human to check GitHub/environment
settings**: `git push origin main` from inside the cloud environment still
returns a 403, on any branch, not just main (matches the 2026-07-20 finding —
this is a distinct, older issue from the Chromium/proxy one, first reported
during that session's routine test-run). This means even a fully-working
routine cannot persist its own work or update this log — everything it does
dies with the container. **This is very likely the single biggest remaining
blocker to real unattended automation** — a routine could now (with the TLS
fix) actually read TPT/Gumroad/TES/Pinterest and act, but has no way to save
what it did. Needs checking on the GitHub side (does the GitHub App/token
backing this Claude Code environment's repo connection actually have
`contents: write` on `MrGibbsTeach/cmie`?) and/or the environment's own
repository-connection settings in the claude.ai/code UI. Not something fixable
via a code change or a tool call from a normal Claude Code session — needs the
account owner's direct action.

**Not yet re-attempted this session**: re-enabling the 4 paused routines. Do
not flip any of them back to `enabled: true` until the git push 403 is
resolved and confirmed with a real push from inside that environment — a
routine that can read but not write is worse than one that's off, because a
clean-looking "success" log message would be lying about whether anything
actually got saved.

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

## 2026-07-31 — Scheduled business review + integrity checks: Gumroad clean, TPT/TES blocked again by browser TLS reset

Ran the standard routine: `python business_review.py --save`, then the three
post-publish integrity checkers. Report-only run — nothing found below was
touched, edited, or deleted.

**Revenue snapshot** (see `BUSINESS_REVIEW.md`, timestamp 2026-07-31 02:13 UTC):
- **TPT**: could not check — see browser blocker below.
- **Gumroad**: A$0.00 net, 0 sales (via API, `GUMROAD_TOKEN` — reliable).
- **TES**: could not check — see browser blocker below.
- Last confirmed full snapshot remains 2026-07-19: TPT $13.45 USD / 1 sale,
  Gumroad A$0 / 0 sales, TES £0.30 GBP / 1 sale.

**Catalog size**: `business_review.py` reports **0 live units** this run —
this is an artifact of the fresh checkout, not a real catalog change. It
derives catalog size from `releases/public/*_v001/` on local disk, which
does not exist in this session's clone (build artifacts, not committed to
git). The last real count was 11 units (2026-07-19 snapshot, still the best
available reference — see that entry in `BUSINESS_REVIEW.md`'s git history
or the list below).

**Integrity checkers**:
- `verify_gumroad_listings.py` — **ran clean.** Checked all 10 Gumroad
  products matching "Unit 1"; no empty/near-empty descriptions, no
  unrendered markdown, no HTML leakage, no 0-byte zips. All show status
  "(published)". Product URLs (all OK): `focuslabdigital.gumroad.com/l/`
  `yyrcw`, `psbzqv`, `hmntzx`, `caqcw`, `dvjrck`, `yqnok`, `ivmbkk`,
  `llfnfx`, `kezhjt`, `bpvevc`.
- `verify_tpt_listings.py` — **could not run.** Tried
  `--unit year7_algorithms_unit1` as a representative check; failed before
  it even reached the dashboard (fails on the initial login-state check,
  `https://www.teacherspayteachers.com/` → `net::ERR_CONNECTION_RESET`).
  Since the failure is at browser/network level, not unit-specific, did not
  repeat it across the other 10 known units (year7_cybersecurity_unit1,
  year7_data_representation_unit1, year7_digital_systems_unit1,
  year7_game_design_unit1, year7_networks_hardware_unit1,
  year7_orientation_unit1, year7_python_programming_unit1,
  year7_spreadsheets_unit1, year7_ux_design_unit1,
  year7_web_design_unit1) — same root cause would apply to all.
- `verify_tes_listings.py` — **could not run**, same failure
  (`https://www.tes.com/authn/sign-in` → `net::ERR_CONNECTION_RESET`).

**Browser blocker — status update on the 2026-07-31-earlier TLS fix**: the
TLS-1.2-cap fix from earlier today (`cloud_launch_kwargs()` in
`cmie/publishing/browser.py`, commit `12b07a7`) did **not** resolve the
issue in this session — same `ERR_CONNECTION_RESET` on every HTTPS
navigation through the proxy (reproduced even on `https://example.com`, not
just the target sites). Netlog capture (`--log-net-log`) shows the CONNECT
tunnel itself succeeds (`200 Connection Established`), then the reset
happens immediately after Chromium sends its TLS ClientHello — `net_error
-101` / `os_error 104` (ECONNRESET), before any server response.
`--ssl-version-max=tls1.2` is very likely a no-op on this Chromium build
(141.0.7390.37) — Chrome removed that flag's effect years ago — which would
explain why the earlier fix appeared to work in one diagnostic session but
not here. `plain curl` through the same proxy to the same hosts (TLS 1.3,
HTTP/2) succeeds every time, so this looks Chromium-client-specific, not a
blanket proxy outage. Not fixed here (out of scope for a report-only run,
and the proxy README says client-specific TLS failures need
administrator/Anthropic-support attention, not a code workaround). Also
separately note: this session's `pip install -r requirements.txt` pulled
Playwright 1.61.0, whose bundled Chromium build (revision 1228) doesn't
match what's pre-installed in this container (revision 1194) — had to pin
`playwright==1.56.0` locally in this session just to get Chromium to launch
at all (a session-local pip choice, not a repo change; every fresh
container will hit this same mismatch until `requirements.txt` pins a
compatible version — a decision for a human, not made here).

**No integrity issues found on anything that could actually be checked.**
Open items list unchanged from 2026-07-19 (see below in this file's
history / `BUSINESS_REVIEW.md`) — still waiting on human decisions for the
TES cosmetic bug, the TES duplicate pair (13432831 / 13432796), the
permanently-broken TES resource 13445828, the off-brand Gumroad products,
and real unattended scheduling.

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
PUSH TEST 2026-07-31 -- confirming GitHub App write access after reinstall.

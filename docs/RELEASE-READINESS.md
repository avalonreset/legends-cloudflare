# Release readiness

Release: `legends-cloudflare` 0.1.1. Release date: 2026-10-16.

Status: public `0.1.1` release verified across offline tests, clean-environment wheel/sdist installation, `legends-empire` `0.3.2` knowledge-pack attachment, live Cloudflare read smoke, and live disposable TXT write/update/readback/delete round-trip validation.

| Gate | State |
|---|---|
| Product rename and public package | Completed |
| Official-source knowledge vault, `legends.knowledge-pack/v1` pack, and Empire templates | Completed and verified through `legends-empire` `0.3.2` (preview, apply, repeat noop, and conflict refusal) |
| Attribution and MIT license | Completed |
| House banner and social image | Rendered and visually inspected |
| Offline behavior tests | 32 passed on Windows and 32 passed on Ubuntu 24.04 through WSL |
| Clean wheel and source installation | Passed isolated wheel and source-distribution installs with offline doctor; archive contents checked |
| Router recipe and isolated catalog integration | Passed real manager installation/probes against a local archive fixture; intent routing, legacy alias and handoff passed; router unchanged; admission helper preserves unrelated catalog entries |
| Live read smoke | Passed zone listing, zone-by-ID metadata and one zone's DNS listing; no writes sent; private inventory not published |
| Live write round trip | Passed authorized disposable TXT creation, exact-ID update, TTL preservation, API readback and exact-ID deletion; final inventory confirmed zero test records |
| Linux/macOS/Windows hosted CI | Configured in `.github/workflows/checks.yml` across `ubuntu-latest`, `windows-latest`, and `macos-latest` (`3.10`, `3.12`) |
| GitHub presentation audit and metadata | Portable verify, audit, SEO hypotheses, metadata, README, community, legal and release planning completed through `legends-github`; attribution checklist passes |
| Measured keyword/SERP research | Collected seven requested keywords and three SERPs; imported through `legends-github`; README/metadata choices applied; actual cost $0.01872 |

The wheel installs the CLI. The source distribution includes the knowledge vault (`wiki/` and `knowledge/cloudflare/pack.json`), agent recipe and presentation files. No production credentials or predecessor runtime files are included.

The authorized live canary changed only one newly created disposable TXT record and verified cleanup. Other record types have offline tests, not live write coverage. API readback does not establish propagation or service health.

The deterministic metadata planner suggested generic skill/plugin topics. Those were rejected in favor of product-matched DNS, Cloudflare, CLI, knowledge-base and agent topics. No artificial support response-time guarantee or ranking claim was added to satisfy a checklist.

See [release protocol](RELEASE.md) for the exact publication sequence.

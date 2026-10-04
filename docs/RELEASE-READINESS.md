# Release readiness

Candidate: `legends-cloudflare` 0.1.0. Review date: 2026-10-03.

Status: local release candidate prepared; not published or admitted to the public catalog.

| Gate | State |
|---|---|
| Product rename and public package | Prepared |
| Official-source knowledge vault and Empire templates | Prepared |
| Attribution and MIT license | Prepared |
| House banner and social image | Rendered and visually inspected |
| Offline behavior tests | 32 passed on Windows and 32 passed on Ubuntu 24.04 through WSL |
| Clean wheel and source installation | Passed isolated wheel and source-distribution installs with offline doctor; archive contents checked |
| Router recipe and isolated catalog integration | Passed real manager installation/probes against a local archive fixture; intent routing, legacy alias and handoff passed; router unchanged; admission helper preserves unrelated catalog entries |
| Live read smoke | Passed zone listing, zone-by-ID metadata and one zone's DNS listing; no writes sent; private inventory not published |
| Live write round trip | Not run; requires an authorized disposable zone and record |
| Linux/macOS/Windows hosted CI | Workflow prepared; not executed on GitHub |
| GitHub presentation audit and metadata | Portable verify, audit, SEO hypotheses, metadata, README, community, legal and release planning completed through legends-github; attribution checklist passes |
| Measured keyword/SERP research | Spending authorization pending; free search observations recorded |
| Public repository, tag and release | Not published |
| Social preview upload | Image ready; upload not attempted |
| Public catalog pins and fresh public install | Pending immutable public archive |

The candidate catalog row deliberately contains null commit and checksum values. It is not a valid live catalog entry until publication supplies real immutable pins.

The wheel installs the CLI. The source distribution includes the knowledge vault, agent recipe and presentation files. No production credentials or predecessor runtime files are included.

Windows and WSL tests do not establish macOS compatibility. The local archive fixture does not establish a public GitHub download or catalog sync. No live DNS mutation was performed during preparation, so write behavior is tested with synthetic transport responses only.

The GitHub workflow's offline release plan reported authentication unavailable, but a separate authenticated GitHub API identity check succeeded. Treat that plan warning as offline evidence absence, not an account failure. Live repository metadata is unavailable because the target repository has not been created.

The deterministic metadata planner suggested generic skill/plugin topics. Those were rejected in favor of product-matched DNS, Cloudflare, CLI, knowledge-base and agent topics. No artificial support response-time guarantee or ranking claim was added to satisfy a checklist.

See [release protocol](RELEASE.md) for the exact publication sequence.

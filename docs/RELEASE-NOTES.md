# legends-cloudflare v0.1.0

Cloudflare DNS automation with reviewed changes and a reusable knowledge vault.

This first public release brings zone and DNS inventories, assigned nameserver inspection, preview-first single-record changes, exact-ID deletion and API readback to the CTO Legends ecosystem.

Changes are tied to the exact zone, before-state and requested fields through a reviewed SHA-256 plan. Updates preserve settings the operator did not request to change. The client refuses arbitrary API origins, redirects, ambiguous matches and silently incomplete pagination.

The repository includes source-cited DNS runbooks, an Obsidian-compatible knowledge index, and templates for private Empire operating records. A single central `cto-legends` skill loads the module recipe on demand after catalog admission.

Requires Python 3.10+. No runtime dependencies. Independent community project; Cloudflare API and services remain Cloudflare's work. See THIRD_PARTY_NOTICES.md.

Validation: 32 offline tests passed on Windows and Linux/WSL. A scoped live TXT canary verified creation, exact-ID update, preservation of an omitted TTL, API readback, exact-ID deletion and an empty final test-record inventory. Clean wheel and source installs and local router integration passed. Hosted macOS CI and public catalog installation remain publication-stage checks.

Supported writes: A, AAAA, CNAME, TXT, MX and NS. No registrar transfers, Workers deployment, tunnel management, batch writes or automatic rollback. API readback is separate from propagation and service-health verification.

Read docs/RELEASE-READINESS.md for the exact validation performed before using this candidate.

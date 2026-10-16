# Cloudflare operating knowledge

Use this vault with the CLI or as a plain Markdown reference. Read the dated [source ledger](sources.md); provider behavior can change.

| Task | Runbook | Evidence to keep privately |
|---|---|---|
| Connect a scoped token | [Authentication](authentication.md) | Scope and verification result, never token value |
| Inspect or change DNS | [DNS operations](dns-operations.md) | Plan, approval, readback, resolution and service checks |
| Move DNS hosting | [Migration](migration.md) | Inventory comparison, DNSSEC plan, nameserver checks |
| Diagnose failure | [Troubleshooting](troubleshooting.md) | Sanitized error, exact operation, observed remote state |
| Capture change and incident records | [Change receipt](templates/change-receipt.md), [Domain inventory](templates/domain-inventory.md), [Incident review](templates/incident-review.md) | Canonical project links and private receipts |

This is a small operational knowledge base, not comprehensive Cloudflare documentation. Review guidance after an incident or provider behavior change.

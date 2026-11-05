# Operate legends-cloudflare

This is an on-demand module recipe, not a registered skill. The central `cto-legends` router (`skills/cto-legends/SKILL.md`) owns discovery.

## Readiness and Workflow

1. Resolve the selected module source (`legends-cloudflare resources`) and user workspace. Never save reports into a managed source.
2. Run `legends-cloudflare doctor`. This is offline and does not prove account access.
3. For authorized live work, load `CLOUDFLARE_API_TOKEN` securely and run `doctor --live`.
4. Route inventory to `zones`, `records`, or `nameservers`. Read `wiki/dns-operations.md` before changes.
5. Preview `upsert` or `delete`. Show the exact zone, record ID if present, before-state, requested fields and effect.
6. After owner authorization, apply the same request using its exact `--confirm-zone` and `--confirm-plan`. A stale plan must be reviewed again.
7. Check the returned `verified` field. On a timeout or mismatch, inspect actual state; never assume no change or retry automatically.
8. Verify authoritative DNS, recursive resolution and the affected service as separate checks when the task requires them.
9. Save a private receipt only when requested or already part of the authorized workflow. Use `templates/change-receipt.md` in the selected Empire project.

## CLI Command Reference

| Command | Mode | Purpose |
| --- | --- | --- |
| `legends-cloudflare doctor` | Offline | Verify Python 3.11+ runtime and CLI installation without network access. |
| `legends-cloudflare doctor --live` | Live read-only | Verify `CLOUDFLARE_API_TOKEN` and accessible zone listing (`GET /zones`). |
| `legends-cloudflare resources` | Offline | Return absolute paths to packaged `AGENT-RECIPE.md` and `knowledge/cloudflare/pack.json`. |
| `legends-cloudflare zones` | Live read-only | List all accessible zones (`id`, `name`, `status`, `name_servers`). |
| `legends-cloudflare nameservers --zone ZONE` | Live read-only | Read assigned Cloudflare nameservers for the selected zone. |
| `legends-cloudflare records --zone ZONE [--name NAME] [--type TYPE]` | Live read-only | List zone DNS records (`A`, `AAAA`, `CNAME`, `TXT`, `MX`, `NS`, etc.). |
| `legends-cloudflare upsert --zone ZONE --name NAME --type TYPE --content VALUE [--ttl TTL] [--priority PRIO] [--proxied \| --dns-only]` | Live preview | Preview a single-record create or update and emit a canonical `sha256` plan hash (`writes_sent: 0`). |
| `legends-cloudflare upsert ... --apply --confirm-zone ZONE --confirm-plan SHA256` | Live write | Re-verify plan hash and before-state, execute single-record create/PATCH, and verify via API readback. |
| `legends-cloudflare delete --zone ZONE --name NAME --type TYPE --record-id ID` | Live preview | Preview deletion of an exact record ID and emit a canonical `sha256` plan hash (`writes_sent: 0`). |
| `legends-cloudflare delete ... --apply --confirm-zone ZONE --confirm-plan SHA256` | Live write | Re-verify plan hash and record state, delete exact record ID, and confirm absence via API readback. |

## Domain Runbooks and Optional Knowledge Pack

Read `wiki/authentication.md` for permissions, `wiki/migration.md` for nameserver cutover planning, and `wiki/troubleshooting.md` for failures. Registrar transfers, Workers and tunnels are outside this executable scope.

The vault also ships as an attachable Empire knowledge pack (`knowledge/cloudflare/pack.json`, schema `legends.knowledge-pack/v1`, suggested home `wiki/library/legends-cloudflare/cloudflare`). Attachment is optional and explicit; see `docs/EMPIRE.md`.

## EDR and Security Guardrails

- Never spawn hidden consoles, execution-policy bypass shell wrappers, or background localhost daemons.
- Never read local browser profile databases, DPAPI stores, or third-party credential stores.
- Use only the explicit `CLOUDFLARE_API_TOKEN` environment variable over verified HTTPS origins (`https://api.cloudflare.com/client/v4`), and never pass tokens on command lines or commit live DNS records to public repositories.

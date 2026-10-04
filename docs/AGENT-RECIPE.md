# Operate legends-cloudflare

1. Resolve the selected module source and user workspace. Never save reports into a managed source.
2. Run `legends-cloudflare doctor`. This is offline and does not prove account access.
3. For authorized live work, load `CLOUDFLARE_API_TOKEN` securely and run `doctor --live`.
4. Route inventory to `zones`, `records`, or `nameservers`. Read `wiki/dns-operations.md` before changes.
5. Preview `upsert` or `delete`. Show the exact zone, record ID if present, before-state, requested fields and effect.
6. After owner authorization, apply the same request using its exact `--confirm-zone` and `--confirm-plan`. A stale plan must be reviewed again.
7. Check the returned `verified` field. On a timeout or mismatch, inspect actual state; never assume no change or retry automatically.
8. Verify authoritative DNS, recursive resolution and the affected service as separate checks when the task requires them.
9. Save a private receipt only when requested or already part of the authorized workflow. Use `templates/change-receipt.md` in the selected Empire project.

Read `wiki/authentication.md` for permissions, `wiki/migration.md` for nameserver cutover planning, and `wiki/troubleshooting.md` for failures. Registrar transfers, Workers and tunnels are outside this executable scope.

Do not install a standalone module skill. The central `cto-legends` skill loads this recipe on demand.

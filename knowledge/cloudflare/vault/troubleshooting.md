# Troubleshooting

| Observation | Next check |
|---|---|
| Missing token | Check environment provisioning without printing its value |
| HTTP 401/403 | Verify token validity, zone restrictions and permissions |
| HTTP 429 | Inspect service limits; wait according to provider guidance before a deliberate new request |
| Timeout during a write | Read current provider state before deciding whether to retry |
| Inventory pagination error | Treat the collection as incomplete; do not infer absence |
| Ambiguous name/type | Choose the exact record ID from a reviewed inventory |
| Plan hash mismatch | State or requested fields changed; generate and review a fresh preview |
| Readback mismatch | A write was sent; inspect provider normalization, concurrent edits and actual state |
| API readback passes but service fails | Check authoritative DNS, recursive caches, proxy behavior and application configuration |

No automatic rollback is attempted. The pre-change state helps an operator plan a correction, but replaying it without checking current state can overwrite another change.

Capture recurring failures with the [incident template](templates/incident-review.md); link the exact failed assumption and improve the runbook or regression tests.

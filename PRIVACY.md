# Privacy

`legends-cloudflare` is local-first and includes no telemetry, analytics, or background network activity.

## Offline by default

- `legends-cloudflare doctor` (without `--live`) and `legends-cloudflare resources` run completely offline.
- Packaged documentation, `wiki/` references, and `knowledge/cloudflare/` runbooks are resolved from the local installation without network requests.
- Plan hashes (`sha256`) and receipt templates are computed locally.

## Explicit Cloudflare API egress

- Live commands (`doctor --live`, `zones`, `nameservers`, `records`, `upsert`, `delete`) connect exclusively to `https://api.cloudflare.com/client/v4` using `CLOUDFLARE_API_TOKEN` from the caller's environment.
- Ambient proxy environment variables (`HTTP_PROXY`, `HTTPS_PROXY`) and HTTP redirects (`301`, `302`, `303`, `307`, `308`) are refused so credentials are never forwarded off-origin.
- Raw API tokens and provider error payloads are never printed to stdout, stderr, or logs.

See [SECURITY.md](SECURITY.md) for vulnerability reporting and credential hygiene rules.

# Security

Do not include credentials, DNS secrets, private inventories or raw API responses in public issues. Report suspected vulnerabilities privately through the repository's GitHub security reporting feature when available; otherwise contact the maintainer through a private channel.

Use narrowly scoped API tokens. The CLI uses the process environment, verified HTTPS, a fixed API origin, no redirects, and no automatic retries. JSON inventory and plan outputs may contain sensitive DNS content.

Live changes require explicit confirmation of the selected zone and preview hash. This is an operator guard, not an access-control boundary or atomic transaction. Cloudflare permissions are the actual authorization boundary.

If a request times out after submission, the provider may have changed state. Inspect it before repeating the operation. No automatic rollback is performed.

Only the current release candidate is maintained during the 0.1 series. Reported compatibility and test coverage are in `docs/RELEASE-READINESS.md`.

# Authentication

Use a scoped Cloudflare API token with only the zones and permissions needed for the operation. Read operations need Zone Read and DNS Read; DNS changes additionally need DNS Edit. Review the current permission labels in the [official token guide](https://developers.cloudflare.com/fundamentals/api/get-started/create-token/).

Load the token into `CLOUDFLARE_API_TOKEN` through your secret manager. Avoid shell-history literals, chat, screenshots and Markdown. This module does not load `.env` automatically or support the Global API Key.

Run offline doctor to prove the installation. Run live doctor to prove zone listing; then inspect records in the selected zone to prove DNS read access. Write permission is not tested by making an unsolicited canary change.

The client uses verified HTTPS to a fixed Cloudflare origin, refuses redirects, ignores ambient proxy variables, bounds response size, and does not print provider error bodies. Environments requiring a proxy need separate reviewed support.

Source review: 2026-10-03. See [source coverage](sources.md).

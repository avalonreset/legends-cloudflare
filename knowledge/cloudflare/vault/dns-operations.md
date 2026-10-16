# DNS operations

Start with the requested outcome and exact zone. List records, including mail and verification records when relevant. Record IDs distinguish records sharing a name and type.

For an update, review the old content and the fields that will change. Omitted TTL, proxy status and MX priority are preserved. New records default to automatic TTL and DNS-only; MX creation requires explicit priority. Structured record types are excluded from writes in this release.

Cloudflare supports different fields by record type. A/AAAA values are IP addresses; MX has a priority; DNS proxy support depends on type. CNAME and address records cannot simply coexist under the same name. The provider remains the final validator. See the official [record types](https://developers.cloudflare.com/dns/manage-dns-records/reference/dns-record-types/) and [record update API](https://developers.cloudflare.com/api/resources/dns/subresources/records/methods/edit/).

Preview first. A SHA-256 ties confirmation to the exact zone, before-state and proposed payload. Applying rebuilds that plan and rechecks state. A provider-side race can still occur between the last read and mutation; coordinate concurrent operators.

After an applied change:

1. Check provider API readback.
2. Query the authoritative nameservers.
3. Query the recursive resolvers relevant to users after applicable cache expiry.
4. Test the affected website, mail path or verification service.

These are separate observations. Proxied records can resolve to Cloudflare addresses instead of the origin address. Never use API success alone as proof of service health. Capture a [private receipt](templates/change-receipt.md).

Source review: 2026-10-03. See [source coverage](sources.md).

# Source ledger

Reviewed 2026-10-03 against official Cloudflare documentation. These links support provider behavior; module-specific guarantees are supported by implementation and tests.

| Source | Claims covered | Used by |
|---|---|---|
| [Create API token](https://developers.cloudflare.com/fundamentals/api/get-started/create-token/) | Scoped token creation, permission and resource selection | Authentication |
| [DNS record types](https://developers.cloudflare.com/dns/manage-dns-records/reference/dns-record-types/) | Type-specific fields, proxy behavior, record constraints | DNS operations |
| [Update DNS record](https://developers.cloudflare.com/api/resources/dns/subresources/records/methods/edit/) | PATCH endpoint, DNS edit authorization, record payload | API client, DNS operations |
| [Full setup](https://developers.cloudflare.com/dns/zone-setups/full-setup/setup/) | Record review, nameserver cutover, DNSSEC sequencing | Migration |
| [List DNS records](https://developers.cloudflare.com/api/resources/dns/subresources/records/methods/list/) | Record query and pagination | API client |
| [List zones](https://developers.cloudflare.com/api/resources/zones/methods/list/) | Zone enumeration and filtering | API client |

No external documentation corpus is bundled. Summaries are original and links retain upstream attribution. Dates are review dates, not a promise that upstream pages will remain unchanged.

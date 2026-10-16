# Plan a DNS hosting migration

DNS hosting, registrar ownership and application hosting are separate systems. Changing nameservers does not transfer a domain to another registrar. This CLI inspects assigned Cloudflare nameservers; it does not change the registrar.

Use Cloudflare's current [full setup guide](https://developers.cloudflare.com/dns/zone-setups/full-setup/setup/):

1. Inventory the existing records and identify critical web, mail and verification services.
2. Review the imported Cloudflare records against that inventory. Automated discovery may miss records.
3. Plan DNSSEC changes with the current registrar and Cloudflare instructions. Do not blindly preserve an old DS record across a nameserver change.
4. Review the assigned nameservers for the exact zone and obtain authorization for the registrar change.
5. Change nameservers through the registrar's authorized workflow.
6. Check Cloudflare activation, authoritative and recursive DNS, then actual service behavior.
7. Follow the provider's DNSSEC enablement instructions and retain a rollback plan.

Use the [domain inventory](templates/domain-inventory.md). Keep registrar contacts and billing information private. Registrar transfer eligibility, locks, pricing and renewal terms require separate current research; this module does not assert them.

Source review: 2026-10-03. See [source coverage](sources.md).

# Rename and compatibility

| Surface | Public identity |
|---|---|
| Product and repository | `legends-cloudflare` |
| Distribution and executable | `legends-cloudflare` |
| Python import | `legends_cloudflare` |
| Router catalog key | `legends-cloudflare` |
| Agent recipe | `docs/AGENT-RECIPE.md` |
| Registered host skill | Existing `cto-legends` only |

The predecessor `legends-cloudflare-kit` was a private PowerShell workspace, not a public Git repository. There is no public GitHub repository redirect to configure.

This release does not rename or move the predecessor folder, `.env`, installed standalone guides, or private historical receipts. They remain usable until the owner selects local migration. Do not copy their private content into the public project.

After public catalog admission and a verified installation, update selected local guide references to the new module recipe. Retain a compatibility note for old kit commands; do not imply that PowerShell arguments are accepted by the Python CLI.

The new command names preserve the intent, not positional syntax: `zones`, `records`, `nameservers`, `upsert`, and `delete`. `--apply --confirm-zone --confirm-plan` replaces the earlier live-write flags.

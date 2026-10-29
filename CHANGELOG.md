# Changelog

## 0.1.1 - 2026-10-29

- Raise minimum supported Python runtime to Python 3.11 (`requires-python = ">=3.11"`) across package metadata, documentation, and multi-OS CI.
- Harden `.github/workflows/checks.yml` with 40-character commit SHA action pins and upgrade `pip>=26.2.2` before package installation.

## 0.1.0 - 2026-10-16

- Public product identity: `legends-cloudflare`, replacing the private kit name for this distribution.
- Portable, dependency-free Python CLI for zone and DNS inventory, nameservers, previews and confirmed single-record changes.
- Full pagination with explicit incomplete-result errors; bounded, fixed-origin API transport.
- Plan hashes, stale-state checks, exact-ID deletion, PATCH preservation and API readback.
- Source-cited Markdown knowledge vault, attachable `legends.knowledge-pack/v1` library (`knowledge/cloudflare/pack.json`), and private Empire templates.
- Central `cto-legends` recipe integration, release packaging, house banner and social artwork.

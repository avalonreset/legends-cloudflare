# Changelog

## 0.1.4 - 2026-11-21

- Add `scripts/render_cards.py` and the 7 outlined Legends Font `r1` SVG architecture, comparison, plain-english chain, handoff, CTA, and collection star shrine cards under `assets/cards/r1/`.
- Upgrade `README.md` to the evergreen CTO Legends architecture and reference drawer standard with zero hardcoded version strings and collapsible `<details>` reference sections.
- Include `.svg` assets in `setup.py` build-time wheel `_data/` mirroring and `MANIFEST.in` source distribution packaging, and remove the duplicate root `assets/collection-star-shrine.svg`.
- Update release metadata, `CITATION.cff`, `docs/catalog-entry.candidate.json`, and 20-topic GitHub discovery metadata for `0.1.4`.

## 0.1.3 - 2026-11-11

- Enforce ancestor-chain symlink refusal (`check_no_symlink_chain` with macOS `/var`, `/tmp`, `/etc` allowance), `<= 1 MB` (`1,048,576` bytes) `O_NOFOLLOW` bounded file reads, and duplicate-key-rejecting JSON parsing in `legends_cloudflare/resources.py` and `scripts/prepare_catalog.py`.
- Derive HTTP `User-Agent` dynamically from `legends_cloudflare.__version__` (`api.py`) and reject boolean values (`isinstance(priority, bool)`) in MX priority validation (`dns.py`).
- Include `.legends-router-pin`, `PRIVACY.md`, and `CODE_OF_CONDUCT.md` across `MANIFEST.in`, `setup.py` wheel `_data/` mirroring, and `tests/test_packaging.py`.
- Fix CommonMark inline code-span backtick formatting in `CHANGELOG.md`, update release documentation to `0.1.3`, add `tags: ["v*"]` push trigger to `.github/workflows/checks.yml`, and align `scripts/check_release.py` with the Gold-Standard static gate.

## 0.1.2 - 2026-11-05

- Add `legends_cloudflare/resources.py` (`legends-cloudflare resources`), `setup.py` build-time wheel `_data/` mirroring, `scripts/smoke_installed_resources.py`, `scripts/verify_knowledge_attachment.py`, and `tests/test_packaging.py`.
- Add `.legends-module` and `assets/manifest.json`, update `README.md` to the standard 3-badge house layout and ``## Agent setup (via `cto-legends`)`` section, and expand `docs/AGENT-RECIPE.md` with a complete CLI command reference table.
- Upgrade `scripts/check_release.py`, `AGENTS.md`, and `docs/AGENT-RECIPE.md` with Windows Defender / EDR anti-ransomware guardrails, raster metadata verification, and em/en-dash enforcement.
- Expand `.github/workflows/checks.yml` to a 9-job cross-OS (`ubuntu-latest`, `windows-latest`, `macos-latest`) and `empire-attachment` matrix pinned to `avalonreset/legends-empire` `v0.3.4` (`1ede96ad670b60b215b66457369691da6c61d017`).

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

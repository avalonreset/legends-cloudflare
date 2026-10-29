# Release protocol

The public identity is `legends-cloudflare`. Target repository: `avalonreset/legends-cloudflare`. The earlier private kit keeps its existing files and credentials until a separately verified local migration.

## Candidate gates

1. Review implementation, official sources, attribution and the public file inventory.
2. Run offline tests and `python scripts/check_release.py`.
3. Build wheel and source distribution; install each into a clean environment and run doctor.
4. Verify router recipe probes and intent matching in an isolated test catalog. Preserve the canonical router skill byte-for-byte.
5. Verify authorized live reads and a disposable-zone write round trip when that operation is authorized. Keep evidence private.
6. Run `legends-github` portable verify, audit, SEO, metadata, legal and release planning. Preserve evidence and distinguish measured keyword research from free search or copy hypotheses.
7. Inspect banner and social image at full and thumbnail sizes.
8. Prepare release notes, metadata, package hashes and a concrete readiness receipt.

## Publication and admission

1. Confirm authorization for the concrete public candidate, then create the repository, push the reviewed commit and run hosted CI.
2. Tag the verified commit as `v0.1.1`; publish the source/wheel artifacts with SHA256SUMS and release notes.
3. Upload `assets/social-preview.png` through GitHub Settings and verify the served preview. A committed image is not an uploaded social preview.
4. Download the immutable GitHub codeload ZIP for that commit and calculate its SHA-256.
5. Use `scripts/prepare_catalog.py --catalog CURRENT_CATALOG --commit REAL_COMMIT --sha256 REAL_ARCHIVE_HASH --output NEW_CANDIDATE` to prepare admission. It adds the module, preserves unrelated entries, increments only the catalog version, and adds the `legends-cloudflare-kit` compatibility alias. It does not publish or verify that supplied pins exist; validate the actual public archive separately.
6. Validate the complete catalog and prove a fresh installation, probes, `handoff`, `doctor`, and `run` from the public immutable archive.
7. Publish the catalog update, then prove remote `sync` and installation from a fresh manager home.

Do not insert placeholder hashes into the live catalog. Repository publication alone does not provide router discovery. No new per-module skill registration is required.

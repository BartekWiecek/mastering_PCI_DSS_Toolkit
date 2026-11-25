# Maintain the Toolkit delivery site

The permanent reader site is served from docs/ on main. Public distribution is stable-only.

1. Freeze the reviewed educational ZIP. Never upload the manuscript, official standards, signed AOCs, private evidence or unapproved candidates to this public repository.
2. For a new accepted stable release, update docs/downloads/manifest.json (schema 2, current) with the stable version, exact filename, SHA-256, member and index counts and book compatibility. Upload only the accepted reader ZIP.
3. Verify the delivery workflow: archive CRC, path safety, SHA-256, evidence index, 56 synthetic tests and six browser cases. The workflow must not overwrite an existing stable release asset.
4. Verify the public smoke test (anonymous download from Pages and GitHub Releases, matching hash, one visible download, corrupted archive rejection, mobile layout). If verification fails, use the existing stable release while correcting the deployment.
5. Develop and test candidates privately, outside the public reader repository. Keep historical technical records in the editorial project. Do not rewrite the existing Git history.

Initial stable archive v1.0.0 is unchanged. Earlier public test releases, their tags and distribution files were withdrawn. This does not erase historical Git commits, earlier downloads, forks or caches. The original acceptance records are preserved in Git history and the editorial project. Book/KDP acceptance and real-world PCI DSS assessments remain separate.

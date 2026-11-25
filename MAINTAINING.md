# Maintaining the reader distribution

Keep this repository public and separate from the private author project.

## Initial preview

1. Add the exact `docs/downloads/PCI_DSS_Implementation_Toolkit_RC8.zip` archive. Its SHA-256 is `83d54ddb5495faa1e5ae31e0cb96bc5e2831d3bad7157323566c1b92f9949dc5`. Do not upload the manuscript or the complete publishing package.
2. In Settings → Pages, choose **Deploy from a branch**, `main`, `/docs`. Save. The anticipated reader address is `https://bartekwiecek.github.io/mastering_PCI_DSS_Toolkit/`. Verify it as an anonymous visitor before printing it in the book.
3. The preview publication workflow verifies the archive on upload and creates a versioned **pre-release**. If Actions cannot run, create a GitHub pre-release named `rc8-preview` and attach the exact ZIP and its checksum after independent verification.
4. Confirm the anonymous website and release asset download, hash, extraction and basic usability. Only then update the manuscript's companion link.

## Future versions

Use immutable versioned filenames and tags. A final release must explicitly identify its book edition; do not promote an RC to a final release by changing its label. Update the landing page, checksums, errata and compatibility information. Keep older editions available. Do not publish official source documents, real assessment evidence, secrets, private project files, or a full book manuscript.

Do not assign a permissive license without author approval. Keep the reader-use permission consistent with the book.
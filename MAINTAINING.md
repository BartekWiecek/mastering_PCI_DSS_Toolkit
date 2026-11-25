# Maintain the Toolkit delivery site

The Pages site is served from docs/ on main. Keep the permanent reader URL unchanged.

## New delivery
1. Freeze the reviewed reader ZIP. Never upload the publishing package, licensed standards, signed AOCs or internal reviewer records.
2. Set a new versioned filename, exact SHA-256, member count, index count and compatibility in docs/downloads/manifest.json. Upload only the corresponding reader ZIP to docs/downloads/.
3. The Verified Toolkit delivery workflow validates paths, CRC, SHA-256 and evidence index; executes 56 synthetic tests and six browser cases; and publishes only the exact tested bytes. Review logs and the delivery report. A missing next archive tests the existing preview instead, without publishing a new release.
4. A candidate uses a vX.Y.Z-rc.N tag. A stable version uses vX.Y.Z, channel stable and review accepted, only after editorial acceptance. Never rename a candidate as stable just to bypass review. The workflow refuses to replace bytes of existing release assets.
5. Test the public Pages site and direct release download anonymously. Verify the SHA-256, extract and open both workbooks. Confirm the correct edition and errata. If status checks fail, use release history and verify the file locally.

RC8 remains an earlier preview. RC14 is staged as the first 1.0 candidate; the ZIP must be uploaded. The stable gate is not accepted yet. All lab results are synthetic and are not evidence of production PCI DSS compliance.

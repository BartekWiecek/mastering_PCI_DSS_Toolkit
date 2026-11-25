"use strict";
const archive = "downloads/PCI_DSS_Implementation_Toolkit_RC8.zip";
const expected = "83d54ddb5495faa1e5ae31e0cb96bc5e2831d3bad7157323566c1b92f9949dc5";
const button = document.getElementById("download");
const status = document.getElementById("status");
async function checkAvailability() {
  try {
    const response = await fetch(archive, { method: "HEAD", cache: "no-store" });
    if (!response.ok) throw new Error("not published");
    if (!globalThis.crypto?.subtle) throw new Error("checksum verification unavailable");
    button.disabled = false;
    button.textContent = "Download Toolkit ZIP";
    status.textContent = "The preview archive is available. Its SHA-256 will be checked before download.";
  } catch {
    button.disabled = true;
    button.textContent = "Preview not available here yet";
    status.textContent = "Check the release history for published versions. This page does not offer an unverified archive.";
  }
}
button.addEventListener("click", async () => {
  button.disabled = true;
  status.textContent = "Downloading and checking integrity…";
  try {
    const response = await fetch(archive, { cache: "no-store" });
    if (!response.ok) throw new Error("download failed");
    const bytes = await response.arrayBuffer();
    const digest = Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256", bytes)), b => b.toString(16).padStart(2, "0")).join("");
    if (digest !== expected) throw new Error("checksum mismatch");
    const url = URL.createObjectURL(new Blob([bytes], { type: "application/zip" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = "PCI_DSS_Implementation_Toolkit_RC8.zip";
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 60000);
    status.textContent = "SHA-256 verified. Download started.";
  } catch {
    status.textContent = "Download could not be verified. No file was saved. Consult the release history.";
  } finally {
    button.disabled = false;
  }
});
checkAvailability();

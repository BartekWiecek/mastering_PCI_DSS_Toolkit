"""Anonymous end-to-end verification of the published reader site."""
import asyncio, hashlib, json, pathlib, urllib.request, time
from playwright.async_api import async_playwright

ROOT = "https://bartekwiecek.github.io/mastering_PCI_DSS_Toolkit/"
REPO = "https://github.com/BartekWiecek/mastering_PCI_DSS_Toolkit"
manifest = json.loads(pathlib.Path("docs/downloads/manifest.json").read_text())
spec = manifest["current"]
digest = spec["sha256"]
archive = spec["archive"]
tag = spec["tag"]
report = {"tag": tag, "sha256": digest, "site": ROOT, "anonymous": True, "checks": {}}
def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent":"Toolkit-public-delivery-check/1.0", "Cache-Control":"no-cache"})
    with urllib.request.urlopen(req, timeout=45) as res:
        assert res.status == 200
        return res.read()
def check_bytes(data):
    assert hashlib.sha256(data).hexdigest() == digest
    return len(data)
for attempt in range(12):
    try:
        deployed=json.loads(fetch(ROOT+"downloads/manifest.json?check="+str(time.time_ns())))
        assert deployed["schema"] == 2 and deployed["current"] == spec and "next" not in deployed
        report["checks"]["pages_zip_bytes"] = check_bytes(fetch(ROOT+"downloads/"+archive))
        break
    except Exception as e:
        print("Pages attempt",attempt+1,repr(e),flush=True)
        if attempt==11: raise
        time.sleep(15)
for attempt in range(16):
    try:
        report["checks"]["release_zip_bytes"]=check_bytes(fetch(REPO+"/releases/download/"+tag+"/"+archive))
        break
    except Exception as e:
        print("Release attempt",attempt+1,repr(e),flush=True)
        if attempt==15: raise
        time.sleep(15)
checksum=fetch(REPO+"/releases/download/"+tag+"/SHA256SUMS.txt").decode()
assert checksum.strip()==digest+"  "+archive
report["checks"]["release_checksum"]="PASS"
# Previews must not be offered through the public release or Pages surfaces.
from urllib.error import HTTPError
retired = [("rc8-preview","PCI_DSS_Implementation_Toolkit_RC8.zip"),("v1.0.0-rc.1","PCI_DSS_Implementation_Toolkit_RC14.zip"),("v1.0.0-rc.2","PCI_DSS_Implementation_Toolkit_RC19.zip")]
def gone(url):
    try:
        fetch(url)
        return False
    except HTTPError as e:
        if e.code in (404,410): return True
        raise
for attempt in range(20):
    try:
        listing=json.loads(fetch("https://api.github.com/repos/BartekWiecek/mastering_PCI_DSS_Toolkit/releases?per_page=100"))
        assert all(not r["prerelease"] and not r["draft"] for r in listing)
        assert {r["tag_name"] for r in listing} == {tag}
        for retired_tag, retired_archive in retired:
            assert gone(ROOT+"downloads/"+retired_archive+"?check="+str(time.time_ns()))
            assert gone(REPO+"/releases/download/"+retired_tag+"/"+retired_archive)
        break
    except Exception as e:
        print("Retirement propagation attempt",attempt+1,repr(e),flush=True)
        if attempt==19: raise
        time.sleep(15)
report["checks"]["obsolete_public_downloads_withdrawn"]="PASS"
async def main():
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True)
        ctx=await browser.new_context(accept_downloads=True,viewport={"width":1280,"height":900})
        page=await ctx.new_page()
        await page.goto(ROOT,wait_until="domcontentloaded")
        card=page.locator(".release-card").filter(has=page.get_by_role("heading",name=tag,exact=True))
        await card.wait_for(timeout=60000)
        assert await card.locator(".badge").inner_text()=="STABLE"
        assert await page.locator(".release-card").count()==1
        assert await page.get_by_role("heading",name="Put PCI DSS into practice",exact=True).count()==1
        report["checks"]["single_stable_download"]="PASS"
        async with page.expect_download(timeout=60000) as d:
            await card.get_by_role("button",name="Download Toolkit ZIP").click()
        download=await d.value
        assert download.suggested_filename==archive
        check_bytes(pathlib.Path(await download.path()).read_bytes())
        assert "Checksum verified" in await card.get_by_role("status").inner_text()
        report["checks"]["desktop_verified_download"]="PASS"
        # Negative control: a corrupted response must never create a download.
        await page.route("**/downloads/"+archive,lambda route: route.fulfill(status=200,body=b"not the approved ZIP",content_type="application/zip"))
        started=[]
        page.on("download",lambda d: started.append(d))
        await card.get_by_role("button",name="Download Toolkit ZIP").click()
        await card.get_by_role("status").get_by_text("Download not verified.",exact=False).wait_for(timeout=15000)
        assert not started
        report["checks"]["corruption_rejected"]="PASS"
        await ctx.close()
        mobile=await browser.new_context(viewport={"width":390,"height":844},is_mobile=True,has_touch=True,device_scale_factor=2)
        page=await mobile.new_page()
        await page.goto(ROOT,wait_until="domcontentloaded")
        card=page.locator(".release-card").filter(has=page.get_by_role("heading",name=tag,exact=True))
        await card.wait_for(timeout=60000)
        assert await page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
        assert await card.get_by_role("button",name="Download Toolkit ZIP").is_enabled()
        report["checks"]["mobile_layout"]="PASS"
        await browser.close()
asyncio.run(main())
pathlib.Path("public-smoke-report.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))

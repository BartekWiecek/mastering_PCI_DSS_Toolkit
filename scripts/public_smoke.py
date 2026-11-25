"""Anonymous end-to-end verification of the published reader site."""
import asyncio, hashlib, json, pathlib, urllib.request, time
from playwright.async_api import async_playwright

ROOT = "https://bartekwiecek.github.io/mastering_PCI_DSS_Toolkit/"
REPO = "https://github.com/BartekWiecek/mastering_PCI_DSS_Toolkit"
manifest = json.loads(pathlib.Path("docs/downloads/manifest.json").read_text())
spec = manifest["next"]
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
        assert deployed["next"] == spec
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
async def main():
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True)
        ctx=await browser.new_context(accept_downloads=True,viewport={"width":1280,"height":900})
        page=await ctx.new_page()
        await page.goto(ROOT,wait_until="domcontentloaded")
        card=page.locator(".release-card").filter(has=page.get_by_role("heading",name=tag,exact=True))
        await card.wait_for(timeout=60000)
        assert await card.locator(".badge").inner_text()==spec["channel"].upper()
        async with page.expect_download(timeout=60000) as d:
            await card.get_by_role("button",name="Download and verify ZIP").click()
        download=await d.value
        assert download.suggested_filename==archive
        check_bytes(pathlib.Path(await download.path()).read_bytes())
        assert "Checksum verified" in await card.get_by_role("status").inner_text()
        report["checks"]["desktop_verified_download"]="PASS"
        # Negative control: a corrupted response must never create a download.
        await page.route("**/downloads/"+archive,lambda route: route.fulfill(status=200,body=b"not the approved ZIP",content_type="application/zip"))
        started=[]
        page.on("download",lambda d: started.append(d))
        await card.get_by_role("button",name="Download and verify ZIP").click()
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
        assert await card.get_by_role("button",name="Download and verify ZIP").is_enabled()
        report["checks"]["mobile_layout"]="PASS"
        await browser.close()
asyncio.run(main())
pathlib.Path("public-smoke-report.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))

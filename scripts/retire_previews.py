"""One-time retirement of the exact obsolete reader releases, not stable assets."""
import hashlib, json, os, pathlib, subprocess, tempfile
repo = os.environ["GITHUB_REPOSITORY"]
assert repo.lower() == "bartekwiecek/mastering_pci_dss_toolkit"
def gh(*args):
    return subprocess.check_output(["gh",*args],text=True)
def api(path):
    return json.loads(gh("api",path))
base="repos/"+repo
manifest=json.loads(pathlib.Path("docs/downloads/manifest.json").read_text())
s=manifest["current"]
assert manifest["schema"]==2 and s["tag"]=="v1.0.0" and s["review"]=="accepted" and s["channel"]=="stable"
assert s["sha256"]=="111201a6f6b85e05794e1d40bf6a6a578bd5624ea8a90ecaf76eaaa7778c1404"
archive=pathlib.Path("docs/downloads")/s["archive"]
assert hashlib.sha256(archive.read_bytes()).hexdigest()==s["sha256"]
def stable():
    r=api(base+"/releases/tags/v1.0.0")
    assert r["id"]==458045040 and not r["prerelease"] and not r["draft"]
    assert api(base+"/releases/latest")["id"]==r["id"]
    a=next(x for x in r["assets"] if x["name"]==s["archive"])
    assert a["id"]==791353914 and a["digest"]=="sha256:"+s["sha256"]
    return r
stable()
with tempfile.TemporaryDirectory() as d:
    gh("release","download","v1.0.0","--repo",repo,"--dir",d,"--pattern",s["archive"])
    assert hashlib.sha256((pathlib.Path(d)/s["archive"]).read_bytes()).hexdigest()==s["sha256"]
obsolete={
"rc8-preview":(457883250,"PCI_DSS_Implementation_Toolkit_RC8.zip","83d54ddb5495faa1e5ae31e0cb96bc5e2831d3bad7157323566c1b92f9949dc5","4662153f77e061d504c95ef4b8d54fca2e2e6d3f"),
"v1.0.0-rc.1":(457957743,"PCI_DSS_Implementation_Toolkit_RC14.zip","e8adcfe057e8a88d3ad0543085bf0efb1a661be2dbf8c25f8af08b35faeffe0c","f22805531c8feac45419cf2da4a366f646b468ca"),
"v1.0.0-rc.2":(458031252,"PCI_DSS_Implementation_Toolkit_RC19.zip","3123c2dd3e6d702657b5ecdeda397aef113224c73b3d196f5781d604a22eb835","d1e4ef9145b48320596a924fdf44d16e283cd983")}
releases={r["tag_name"]:r for r in api(base+"/releases?per_page=100")}
assert set(releases)<={"v1.0.0",*obsolete}
# Validate every existing obsolete release before deleting any.
for tag,(ident,name,digest,target) in obsolete.items():
    if tag in releases:
        r=releases[tag]
        assert r["id"]==ident and r["prerelease"] and not r["draft"] and r["target_commitish"]==target
        assert any(a["name"]==name and a["digest"]=="sha256:"+digest for a in r["assets"])
    assert not (archive.parent/name).exists()
    refs=api(base+"/git/matching-refs/tags/"+tag)
    for ref in refs:
        if ref["ref"]=="refs/tags/"+tag:
            obj=ref["object"]
            if obj["type"]=="tag":
                obj=api(base+"/git/tags/"+obj["sha"])["object"]
            assert obj["type"]=="commit" and obj["sha"]==target
# Update the existing stable release's marketing copy without altering assets.
gh("release","edit","v1.0.0","--repo",repo,"--title","Implementation Toolkit v1.0.0","--notes-file","docs/downloads/RELEASE_NOTES.md")
stable()
for tag in obsolete:
    if tag in releases:
        print("Retiring public prerelease:",tag,flush=True)
        gh("release","delete",tag,"--repo",repo,"--yes","--cleanup-tag")
    else:
        refs=api(base+"/git/matching-refs/tags/"+tag)
        if any(r["ref"]=="refs/tags/"+tag for r in refs):
            gh("api","--method","DELETE",base+"/git/refs/tags/"+tag)
    assert not any(r["ref"]=="refs/tags/"+tag for r in api(base+"/git/matching-refs/tags/"+tag))
    print("Retired release and tag:",tag,flush=True)
# The prepared branch is a merged historical build ref. Remove only if the known commit is unchanged.
branch="refs/heads/release/v1.0.0-prepared"
refs=api(base+"/git/matching-refs/heads/release/v1.0.0-prepared")
for ref in refs:
    if ref["ref"]==branch:
        assert ref["object"]["sha"]=="b8aeeb50d7a017fcc9901d3a3c2805536e3529b5"
        gh("api","--method","DELETE",base+"/git/refs/heads/release/v1.0.0-prepared")
        print("Retired merged build branch",flush=True)
assert {r["tag_name"] for r in api(base+"/releases?per_page=100")}=={"v1.0.0"}
stable()
print("Only v1.0.0 remains published; stable archive and asset identity unchanged.",flush=True)

"""Validate an immutable reader archive and execute its synthetic labs."""
import argparse, csv, hashlib, io, json, pathlib, re, stat, subprocess, sys, zipfile
from tempfile import TemporaryDirectory

p = argparse.ArgumentParser()
p.add_argument("--manifest", default="docs/downloads/manifest.json")
p.add_argument("--browser", action="store_true")
p.add_argument("--report", default="delivery-test-report.json")
a = p.parse_args()
manifest = pathlib.Path(a.manifest)
data = json.loads(manifest.read_text())
spec = data["next"]
archive = manifest.parent / spec["archive"]
if not archive.is_file():
    spec = data["current"]
    archive = manifest.parent / spec["archive"]
assert re.fullmatch(r"PCI_DSS_Implementation_Toolkit_RC[0-9]+\.zip", spec["archive"])
assert re.fullmatch(r"[0-9a-f]{64}", spec["sha256"])
assert re.fullmatch(r"(?:rc[0-9]+-preview|v[0-9]+\.[0-9]+\.[0-9]+(?:-rc\.[0-9]+)?)", spec["tag"])
assert spec["channel"] in {"preview", "candidate", "stable"}
if spec["channel"] == "stable":
    assert spec["review"] == "accepted" and re.fullmatch(r"v[0-9]+\.[0-9]+\.[0-9]+", spec["tag"])
digest = hashlib.sha256(archive.read_bytes()).hexdigest()
assert digest == spec["sha256"], "Archive digest mismatch"
results = []
with TemporaryDirectory() as tmp:
    dest = pathlib.Path(tmp)
    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
        assert len(names) == len(set(names)) == spec["files"]
        assert sum(i.file_size for i in z.infolist()) < 30_000_000
        assert z.testzip() is None
        for entry in z.infolist():
            name = entry.filename
            path = pathlib.PurePosixPath(name)
            assert not path.is_absolute() and ".." not in path.parts and "\\" not in name
            assert not stat.S_ISLNK(entry.external_attr >> 16)
            assert name == "README.md" or path.parts[0] in {"toolkit", "labs"}
            assert path.suffix in {".csv", ".docx", ".json", ".log", ".md", ".py", ".xlsx"}
        index = "toolkit/readiness_pack/Evidence_Pack_Index.csv"
        rows = list(csv.DictReader(io.StringIO(z.read(index).decode("utf-8-sig"))))
        assert len(rows) == spec["index_rows"]
        indexed = set()
        for row in rows:
            path = row["Path relative to reader root"]
            assert path in names and path not in indexed
            assert hashlib.sha256(z.read(path)).hexdigest() == row["SHA-256"].lower()
            indexed.add(path)
        assert set(names) - indexed == {"README.md", index}
        z.extractall(dest)
    for lab, count in [("agent_gateway",10),("payment_page",11),("payment_state",12),("segmentation_model",12),("tls_acceptance",11)]:
        r = subprocess.run([sys.executable,"-m","unittest","discover","-v"],cwd=dest/"labs"/lab,capture_output=True,text=True,timeout=120)
        log = r.stdout + r.stderr
        print(log, flush=True)
        match = re.search(r"Ran (\d+) tests?",log)
        assert r.returncode == 0 and match and int(match[1]) == count, lab
        results.append({"lab":lab,"passed":count})
    browser = {"status":"NOT_RUN"}
    if a.browser:
        r = subprocess.run([sys.executable,"browser_lab.py"],cwd=dest/"labs/payment_page",capture_output=True,text=True,timeout=120)
        print(r.stdout, r.stderr, flush=True)
        assert r.returncode == 0, "Browser lab failed; no publication"
        browser = json.loads(r.stdout)
        assert len(browser["results"]) == 6 and all(x["pass"] is True for x in browser["results"])
        browser["status"] = "PASS_SYNTHETIC"
report = {"tag":spec["tag"],"channel":spec["channel"],"archive":spec["archive"],"sha256":digest,"members":spec["files"],"index_valid":spec["index_rows"],"suites":results,"local_tests":sum(x["passed"] for x in results),"browser":browser,"assessment":"Not production compliance evidence."}
pathlib.Path(a.report).write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))

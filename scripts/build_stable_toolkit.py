"""Promote the frozen RC19 educational reader package; deterministic ZIP_STORED."""
import csv, hashlib, io, json, pathlib, sys, zipfile
source, dest = map(pathlib.Path, sys.argv[1:3])
assert hashlib.sha256(source.read_bytes()).hexdigest() == '3123c2dd3e6d702657b5ecdeda397aef113224c73b3d196f5781d604a22eb835'
with zipfile.ZipFile(source) as z:
    assert z.testzip() is None and len(z.namelist()) == len(set(z.namelist())) == 90
    data = {n:z.read(n) for n in z.namelist()}
idx = 'toolkit/readiness_pack/Evidence_Pack_Index.csv'
rows = list(csv.DictReader(io.StringIO(data[idx].decode('utf-8-sig'))))
assert len(rows) == 88 and {r['Path relative to reader root'] for r in rows} == set(data)-{'README.md',idx}
for r in rows:
    assert hashlib.sha256(data[r['Path relative to reader root']]).hexdigest() == r['SHA-256']
def replace(name, old, new):
    s = data[name].decode('utf-8')
    assert old in s, (name,old)
    data[name] = s.replace(old,new,1).encode('utf-8')
replace('README.md', '# PCI DSS Implementation Toolkit RC19\n\nCandidate reader materials.', '# PCI DSS Implementation Toolkit v1.0.0\n\nStable educational reader release, based on RC19.')
data['README.md'] += b'\nCompatible with Mastering PCI DSS 4.0.1 Compliance (the revised second or third edition, as applicable). The book\'s publication status is separate. See the release notes and errata at https://bartekwiecek.github.io/mastering_PCI_DSS_Toolkit/. Purchasers may adapt original implementation templates and example records for their own internal business use; no general redistribution or resale license is granted.\n'
replace('toolkit/README.md', '# PCI DSS Implementation Toolkit | 1.0 delivery candidate (RC19)', '# PCI DSS Implementation Toolkit | v1.0.0 (RC19 baseline)')
replace('toolkit/readiness_pack/README.md', '# Readiness pack — RC19 candidate', '# Readiness pack — v1.0.0 (RC19 baseline)')
data['toolkit/local_regression/browser.log'] += b'\nHistorical local-run record. Subsequently the exact published RC19 archive passed all six browser cases in GitHub Actions run 45606388819. See the v1.0.0 release delivery report for tests of these exact repackaged bytes.\n'
# Keep the historical metrics and run manifest as snapshots; explain the distinction in the reader guide.
data['toolkit/README.md'] += b'\n## Verification history\n\nThe local regression logs and metrics are historical RC19 snapshots. Exact RC19 later passed 56 local and six browser cases (GitHub Actions run 45606388819), and anonymous delivery smoke tests passed (run 45607725041). The v1.0.0 release changes only publication wording and the artifact index; use its accompanying delivery-test-report.json for exact-archive CI evidence. These checks do not assess real-world PCI DSS compliance.\n'
for i,r in enumerate(rows,1):
    r['Record ID'] = f'V1-PACK-{i:03d}'
    r['SHA-256'] = hashlib.sha256(data[r['Path relative to reader root']]).hexdigest()
s = io.StringIO(newline=''); w=csv.DictWriter(s,fieldnames=list(rows[0]),lineterminator='\n'); w.writeheader(); w.writerows(rows); data[idx]=s.getvalue().encode('utf-8-sig')
with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_STORED) as z:
    for name in data:
        info=zipfile.ZipInfo(name,date_time=(2026,11,25,0,0,0)); info.compress_type=zipfile.ZIP_STORED; info.create_system=3; info.external_attr=0o100644<<16
        z.writestr(info,data[name])
print(hashlib.sha256(dest.read_bytes()).hexdigest(),dest.stat().st_size)

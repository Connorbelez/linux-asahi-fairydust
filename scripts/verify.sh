#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
for file in PKGBUILD *.sh; do bash -n "$file"; done
python3 - <<'CHECK'
import ast,hashlib,json,pathlib
root=pathlib.Path('.')
for p in root.rglob('*.py'): ast.parse(p.read_text(), filename=str(p))
provenance=json.loads((root/'source-provenance.json').read_text())
for name in ['config','patch']:
 path=root/('fairydust.patch' if name=='patch' else name)
 assert hashlib.sha256(path.read_bytes()).hexdigest()==provenance[name+'_sha256']
assert len(provenance['commits'])==12
print('PASS: pinned delta and configuration integrity')
CHECK
python3 tests/build-manifest.py

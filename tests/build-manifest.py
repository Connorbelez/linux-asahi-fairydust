#!/usr/bin/env python3
"""Check a fresh build's manifest without compiling or installing a kernel."""
import os
import pathlib
import shutil
import subprocess
import tempfile

PACKAGE = pathlib.Path(__file__).resolve().parent.parent
with tempfile.TemporaryDirectory(prefix="fairydust-manifest-") as directory:
    root = pathlib.Path(directory)
    shutil.copy2(PACKAGE / "build.sh", root / "build.sh")
    tools = root / "bin"
    tools.mkdir()
    commands = {
        "rustc": "#!/bin/bash\nprintf 'stub rustc 1.93.1\\n'\n",
        "bindgen": "#!/bin/bash\nprintf 'stub bindgen\\n'\n",
        "makepkg": "#!/bin/bash\nif [[ $1 == --packagelist ]]; then printf '%s/fake-kernel.pkg.tar.xz\\n' \"$PWD\"; else printf 'fresh package bytes\\n' > fake-kernel.pkg.tar.xz; fi\n",
    }
    for name, content in commands.items():
        path = tools / name
        path.write_text(content)
        path.chmod(0o755)
    env = dict(os.environ, PATH=str(tools) + ":" + os.environ["PATH"])
    subprocess.run(["bash", "build.sh"], cwd=root, env=env, check=True)
    assert (root / "build.exit-status").read_text().strip() == "0"
    subprocess.run(["sha256sum", "--check", "package.sha256"], cwd=root, check=True)
    (root / "fake-kernel.pkg.tar.xz").write_text("changed package bytes\n")
    result = subprocess.run(["sha256sum", "--check", "package.sha256"], cwd=root, capture_output=True)
    assert result.returncode != 0
    print("PASS: new build manifest verifies the current artifact and rejects changed bytes")

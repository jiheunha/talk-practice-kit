#!/usr/bin/env python
"""One-time setup: create .venv, install the packages, download the model files.

  Windows:  py -3.13 setup_kit.py
  macOS:    python3.13 setup_kit.py

You can run it again. It skips the steps that are already done.
"""
import os
import subprocess
import sys
import venv
from pathlib import Path

HERE = Path(__file__).resolve().parent
VENV = HERE / ".venv"
PY = VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def main():
    if sys.version_info[:2] not in ((3, 12), (3, 13)):
        sys.exit(f"Python 3.12 or 3.13 is needed; this is {sys.version.split()[0]}. "
                 "Run this file with one of those, e.g. 'py -3.13 setup_kit.py' or 'python3.13 setup_kit.py'.")
    if not PY.exists():
        print("creating .venv")
        venv.create(VENV, with_pip=True)
    subprocess.check_call([str(PY), "-m", "pip", "install", "-r", str(HERE / "requirements.txt")])
    subprocess.check_call([str(PY), str(HERE / "get_models.py")])
    print("\nSetup done. Test it with the example talk:")
    print(f"  {PY.relative_to(HERE)} build.py --script example/script.md --deck example/deck.pdf --out example/app")


if __name__ == "__main__":
    main()

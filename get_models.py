#!/usr/bin/env python
"""Download the two Kokoro model files (~350 MB) into models/ and verify them.

  python get_models.py

Files come from the kokoro-onnx GitHub release "model-files-v1.0". That release
lists no checksums, so the sha256 values below were taken from a known-good
download (2026-11) and each file is checked against them.
"""
import hashlib
import sys
import urllib.request
from pathlib import Path

BASE = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
FILES = {
    "kokoro-v1.0.onnx": "7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5",
    "voices-v1.0.bin": "bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d",
}
MODELS = Path(__file__).resolve().parent / "models"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url, path):
    tmp = path.with_suffix(path.suffix + ".part")
    with urllib.request.urlopen(url) as r, open(tmp, "wb") as f:
        total, done = int(r.headers.get("Content-Length", 0)), 0
        while chunk := r.read(1 << 20):
            f.write(chunk)
            done += len(chunk)
            print(f"\r  {done / 1e6:6.0f} / {total / 1e6:.0f} MB", end="", flush=True)
    print()
    tmp.replace(path)


def main():
    MODELS.mkdir(exist_ok=True)
    for name, want in FILES.items():
        path = MODELS / name
        if path.exists() and sha256(path) == want:
            print(f"{name}: already here, sha256 ok")
            continue
        print(f"{name}: downloading")
        download(BASE + name, path)
        if sha256(path) != want:
            path.unlink()
            sys.exit(f"{name}: sha256 does not match, file removed. Run get_models.py again.")
        print(f"{name}: sha256 ok")


if __name__ == "__main__":
    main()

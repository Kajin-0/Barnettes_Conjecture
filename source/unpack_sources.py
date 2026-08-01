#!/usr/bin/env python3
"""Decode source/search_sources.tar.gz.b64 into the repository root."""
import base64
import gzip
import io
import tarfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
payload = (root / "source" / "search_sources.tar.gz.b64").read_text().strip()
raw = gzip.decompress(base64.b64decode(payload))
with tarfile.open(fileobj=io.BytesIO(raw), mode="r:") as archive:
    archive.extractall(root, filter="data")
print("Extracted search/adversarial_evolution.py and search/patch_gluing_search.py")

#!/usr/bin/env python3
"""Reassemble and extract the chunked search-source archive."""
import base64
import gzip
import io
import tarfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
parts = sorted((root / "source").glob("search_sources.tar.gz.b64.part*"))
if not parts:
    raise SystemExit("No source payload chunks found")
payload = "".join(part.read_text().strip() for part in parts)
raw = gzip.decompress(base64.b64decode(payload, validate=True))
with tarfile.open(fileobj=io.BytesIO(raw), mode="r:") as archive:
    archive.extractall(root, filter="data")
print("Extracted search/adversarial_evolution.py and search/patch_gluing_search.py")

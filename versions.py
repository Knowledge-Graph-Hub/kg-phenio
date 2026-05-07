"""Upstream source version fetcher for kg-phenio.

kg-phenio merges phenio.json with two upheno SSSOM mappings. The receipt
nests phenio's per-ontology versions (read from phenio's `phenio-upstream-
versions.tsv` release asset) under a phenio "build" entry; the two upheno
mapping files appear as peer leaves at the kg-phenio level.

In local development against an unreleased phenio checkout, set
`PHENIO_MANIFEST_PATH` to point at the local TSV (e.g.
`../phenio/src/ontology/phenio-upstream-versions.tsv`). In CI / Jenkins the
manifest is fetched from phenio's latest GitHub release.
"""

from __future__ import annotations

import csv
import os
import re
from pathlib import Path
from typing import Any

from kozahub_metadata_schema import (
    now_iso,
    version_from_github_release,
    version_from_http_last_modified,
)


PHENIO_REPO = "monarch-initiative/phenio"
PHENIO_JSON_URL = f"https://github.com/{PHENIO_REPO}/releases/latest/download/phenio.json"
PHENIO_MANIFEST_URL = f"https://github.com/{PHENIO_REPO}/releases/latest/download/phenio-upstream-versions.tsv"

UPHENO_CROSS_URL = (
    "https://data.monarchinitiative.org/mappings/latest/upheno-cross-species.sssom.tsv"
)
UPHENO_SPECIES_IND_URL = (
    "https://data.monarchinitiative.org/mappings/latest/upheno-species-independent.sssom.tsv"
)

# Match the date segment in version IRIs. Most ontologies put the date under
# `/releases/YYYY-MM-DD/` (CHEBI, MONDO, RO, …) but BFO uses `/YYYY-MM-DD/`
# directly without the `releases/` prefix, so match any path segment shaped
# like a date.
VERSION_IRI_DATE = re.compile(r"/(\d{4}-\d{2}-\d{2})/")


def _ontology_version(version_info: str, version_iri: str) -> str:
    """Prefer the versionInfo column; fall back to the date in versionIRI."""
    vi = (version_info or "").strip()
    if vi:
        return vi
    m = VERSION_IRI_DATE.search(version_iri or "")
    if m:
        return m.group(1)
    return "unknown"


def _fetch_phenio_manifest(timeout: float = 10.0) -> str:
    """Fetch phenio-upstream-versions.tsv. Raises on failure."""
    override = os.environ.get("PHENIO_MANIFEST_PATH")
    if override:
        text = Path(override).read_text()
        if not text.strip():
            raise RuntimeError(f"PHENIO_MANIFEST_PATH={override} is empty")
        return text

    import requests

    r = requests.get(PHENIO_MANIFEST_URL, allow_redirects=True, timeout=timeout)
    r.raise_for_status()
    if not r.text.strip():
        raise RuntimeError(f"{PHENIO_MANIFEST_URL} returned empty body")
    return r.text


def _phenio_ontology_leaves(tsv_text: str) -> list[dict[str, Any]]:
    leaves: list[dict[str, Any]] = []
    for row in csv.DictReader(tsv_text.splitlines(), delimiter="\t"):
        source = (row.get("source") or "").strip()
        if not source:
            continue
        version_iri = (row.get("versionIRI") or "").strip()
        leaves.append(
            {
                "id": f"infores:{source}",
                "name": source.upper(),
                "urls": [version_iri] if version_iri else [],
                "version": _ontology_version(row.get("versionInfo", ""), version_iri),
                "version_method": "owl_version_iri",
            }
        )
    return leaves


def get_source_versions() -> list[dict[str, Any]]:
    now = now_iso()

    # Phenio nested-build entry.
    phenio_version, phenio_method = version_from_github_release(PHENIO_REPO)
    manifest = _fetch_phenio_manifest()
    phenio_entry: dict[str, Any] = {
        "id": "phenio",
        "name": "PHENIO",
        "urls": [PHENIO_JSON_URL],
        "version": phenio_version,
        "version_method": phenio_method,
        "retrieved_at": now,
        "sources": _phenio_ontology_leaves(manifest),
    }

    sources: list[dict[str, Any]] = [phenio_entry]

    # Upheno mappings — peer leaves at the kg-phenio level.
    for url, infores_id, name in [
        (UPHENO_CROSS_URL, "infores:upheno-cross-species", "UPheno cross-species mappings"),
        (UPHENO_SPECIES_IND_URL, "infores:upheno-species-independent", "UPheno species-independent mappings"),
    ]:
        ver, method = version_from_http_last_modified(url)
        sources.append(
            {
                "id": infores_id,
                "name": name,
                "urls": [url],
                "version": ver,
                "version_method": method,
                "retrieved_at": now,
            }
        )

    return sources

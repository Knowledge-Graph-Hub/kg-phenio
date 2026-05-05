"""Emit `output/release-metadata.yaml` for kg-phenio (kozahub-metadata-schema)."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parents[1]
# Import versions.py from the repo root without triggering kg_phenio/__init__.py.
sys.path.insert(0, str(REPO_DIR))

from kozahub_metadata_schema import write_metadata  # noqa: E402

from versions import get_source_versions  # noqa: E402


def transform_files() -> list[Path]:
    """Files whose contents go into transform_version (kg-phenio's code + configs)."""
    src_dir = REPO_DIR / "kg_phenio"
    py_files = sorted(src_dir.rglob("*.py"))
    config_files = [REPO_DIR / "versions.py", REPO_DIR / "merge.yaml", REPO_DIR / "download.yaml"]
    return py_files + [p for p in config_files if p.is_file()]


def main() -> None:
    write_metadata(
        ingest_name="kg-phenio",
        source_versions=get_source_versions(),
        transform_paths=transform_files(),
        artifacts=["merged-kg.tar.gz"],
        output_dir=REPO_DIR / "output",
    )


if __name__ == "__main__":
    main()

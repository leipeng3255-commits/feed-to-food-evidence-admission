#!/usr/bin/env python3
"""Build a deterministic, raw-data-free reproducibility bundle."""

from __future__ import annotations

import hashlib
import json
import zipfile
import subprocess
import sys
import re
from datetime import datetime, timezone
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[3]
BRANCH = Path(__file__).resolve().parents[1]
FIXED_TIME = (2026, 9, 22, 0, 0, 0)
SCIENCE_FILES = (
    '01_protocol/study_protocol.md', '01_protocol/validation_design_addendum_20260923.md',
    '01_protocol/data_admission_matrix.csv', '01_protocol/admission_challenge_cases.json',
    '03_harmonisation/module_separation_and_crosswalk_spec.md',
    '04_analysis/claim_evidence_repair_map_20260928.csv',
    '04_analysis/computational_audit_20260930.md',
    '05_code/evaluate_admission.py', '05_code/test_evaluate_admission.py',
    '05_code/harmonise_pilot.py', '05_code/audit_pilot_semantics.py',
    '05_code/build_reproducibility_bundle.py',
    '05_code/test_release_audit.py',
)


def sanitise_paths(data: bytes, paths: dict[str, Path]) -> bytes:
    """Remove machine locations in release copies only; retain genuine timestamps."""
    text = data.decode('utf-8')
    for key, path in sorted(paths.items(), key=lambda item: len(str(item[1])), reverse=True):
        text = text.replace(str(path), '${' + key + '}')
    if re.search(r"/(?:Users|Volumes)/[^\s\"']+", text):
        raise ValueError('Unmapped local path in release candidate')
    return text.encode('utf-8')


def read_paths() -> dict[str, Path]:
    values: dict[str, Path] = {}
    for line in (PROJECT / "00_admin/paths.yaml").read_text(encoding="utf-8").splitlines():
        if ":" in line and not line.lstrip().startswith("#"):
            key, value = line.split(":", 1)
            values[key.strip()] = Path(value.strip().strip('"'))
    return values


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def add_bytes(bundle: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, FIXED_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    bundle.writestr(info, data)


def main() -> int:
    subprocess.run([sys.executable, str(PROJECT / '05_code/utilities/check_paths.py')], check=True, stdout=subprocess.DEVNULL)
    paths = read_paths()
    output_root = paths["animal_food_outputs_root"]
    processed_root = paths["animal_food_processed_root"]
    intermediate_root = paths["animal_food_intermediate_root"]
    output_root.mkdir(parents=True, exist_ok=True)
    release_stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    target = output_root / f"animal_food_feed_transfer_science_{release_stamp}.zip"

    entries: list[tuple[str, bytes]] = []
    for name in SCIENCE_FILES:
        path = BRANCH / name
        entries.append((f"repository/{name}", sanitise_paths(path.read_bytes(), paths)))
    external = [
        intermediate_root / "source_schema_audit.json",
        processed_root / "technical_feasibility_summary.json",
        processed_root / "pilot_harmonisation_summary.json",
        processed_root / "pilot_matrix_summary.csv",
        output_root / "raw_source_manifest.csv",
        output_root / "validation_source_manifest_20260923.json",
        output_root / "li2022_source_manifest_20260923.json",
        output_root / "pilot_semantics_audit_20260930.json",
    ]
    for path in external:
        data = path.read_bytes()
        if path.suffix == '.json':
            data = (json.dumps(json.loads(data), ensure_ascii=False, indent=2) + '\n').encode('utf-8')
        data = sanitise_paths(data, paths)
        entries.append((f"derived/{path.name}", data))

    manifest = {
        "bundle_id": "AFFT_SCIENCE_" + release_stamp,
        "scope": "Selected scientific source snapshot; not a standalone executable release or submission approval. Third-party raw documents and private administrative files excluded. Local paths redacted in copies; source timestamps retained.",
        "review_status": "NONBLINDED_REVIEW_COMPLETED_USER_REPORTED; CURRENT_CONCLUSIONS_ADOPTED_BY_USER; INDEPENDENT_VALIDATION_NOT_ESTABLISHED",
        "raw_data_included": False,
        "scientific_state": "MODULE_A_NO_GO; MODULE_B_DESCRIPTIVE_ONLY; SUBMISSION_AUTHOR_GATE_PENDING",
        "files": [{"path": name, "bytes": len(data), "sha256": digest(data)} for name, data in entries],
    }
    manifest_bytes = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    with zipfile.ZipFile(target, "x") as bundle:
        for name, data in entries:
            add_bytes(bundle, name, data)
        add_bytes(bundle, "MANIFEST.json", manifest_bytes)

    package_sha256 = digest(target.read_bytes())
    validation = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "bundle": str(target),
        "sha256": package_sha256,
        "file_count_excluding_manifest": len(entries),
        "raw_data_included": False,
        "zip_crc": "PASS" if zipfile.ZipFile(target).testzip() is None else "FAIL",
    }
    validation_path = output_root / f"science_bundle_validation_{release_stamp}.json"
    validation_path.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False))
    return 0 if validation["zip_crc"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

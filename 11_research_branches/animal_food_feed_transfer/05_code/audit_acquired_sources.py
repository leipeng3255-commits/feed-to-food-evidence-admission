#!/usr/bin/env python3
"""Validate raw source integrity and produce non-destructive feasibility summaries."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import sys
import zipfile
from collections import Counter
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BRANCH_ROOT = Path(__file__).resolve().parents[1]
PATHS_FILE = PROJECT_ROOT / "00_admin" / "paths.yaml"

EXPECTED_MD5 = {
    "efsa_pesticides_luxembourg/MOPER_ALL_DATA_SSD2_2024_LU.ZIP": "74e983751aea4ded9dd5410cd0c445dc",
    "efsa_vmpr_belgium/VMPR_2024_BE.ZIP": "b7536c29335842ec39384d78b88dff87",
    "efsa_catalogues_2026/DCF_catalogues.zip": "66da7ba8448fe68e6bf87f40435cd1f7",
}


def hash_file(path: Path, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def present(value: str | None) -> bool:
    return bool(value and value not in {"N_A", "NA", "NULL"})


def audit_ssd2_zip(path: Path, module: str) -> dict:
    with zipfile.ZipFile(path) as archive:
        corrupt = archive.testzip()
        members = [name for name in archive.namelist() if not name.startswith("__MACOSX/")]
        if len(members) != 1 or corrupt:
            raise RuntimeError(f"unexpected or corrupt archive {path}: members={members}, corrupt={corrupt}")
        with archive.open(members[0]) as binary:
            reader = csv.DictReader(io.TextIOWrapper(binary, encoding="utf-8-sig", newline=""))
            fields = reader.fieldnames or []
            required = {
                "sampId_A",
                "sampAnId_A",
                "sampStrategy",
                "sampMatCode.base.building",
                "sampMatCode.source",
                "sampMatCode.part",
                "paramCode.base.param",
                "resType",
                "resUnit",
                "resVal",
                "resLOD",
                "resLOQ",
                "evalCode",
            }
            missing_required = sorted(required - set(fields))
            row_count = 0
            samples: set[str] = set()
            sample_analyses: set[str] = set()
            populated = Counter()
            values: dict[str, Counter] = {
                name: Counter()
                for name in [
                    "sampStrategy",
                    "progType",
                    "sampMatCode.base.building",
                    "sampMatCode.source",
                    "sampMatCode.part",
                    "paramType",
                    "resType",
                    "resQualValue",
                    "resUnit",
                    "evalCode",
                ]
            }
            top_params = Counter()
            for row in reader:
                row_count += 1
                if present(row.get("sampId_A")):
                    samples.add(row["sampId_A"])
                if present(row.get("sampAnId_A")):
                    sample_analyses.add(row["sampAnId_A"])
                for name in [
                    "resVal",
                    "resQualValue",
                    "resLOD",
                    "resLOQ",
                    "CCalpha",
                    "CCbeta",
                    "evalLowLimit",
                    "evalHighLimit",
                    "origCountry",
                    "sampCountry",
                    "sampY",
                ]:
                    if present(row.get(name)):
                        populated[name] += 1
                for name, counter in values.items():
                    value = row.get(name)
                    if present(value):
                        counter[value] += 1
                parameter = row.get("paramCode.base.param")
                if present(parameter):
                    top_params[parameter] += 1
    return {
        "module": module,
        "archive": str(path),
        "zip_crc": "PASS",
        "member": members[0],
        "column_count": len(fields),
        "row_count": row_count,
        "unique_samples": len(samples),
        "unique_sample_analyses": len(sample_analyses),
        "missing_required_fields": missing_required,
        "populated_counts": dict(populated),
        "value_counts": {name: dict(counter.most_common(30)) for name, counter in values.items()},
        "top_parameter_codes": dict(top_params.most_common(50)),
    }


def audit_feed_csvs(directory: Path) -> dict:
    files = sorted(p for p in directory.glob("*.csv") if not p.name.startswith("._"))
    total_rows = 0
    years = Counter()
    flags = Counter()
    countries: set[str] = set()
    items: set[str] = set()
    schemas: dict[str, list[str]] = {}
    for path in files:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            schemas[path.name] = reader.fieldnames or []
            for row in reader:
                total_rows += 1
                countries.add(row.get("country_name_en", ""))
                items.add(row.get("item", ""))
                years[row.get("year", "")] += 1
                flags[row.get("feed_1000_tonnes_flag", "")] += 1
    return {
        "file_count": len(files),
        "row_count": total_rows,
        "country_count": len(countries - {""}),
        "items": sorted(items - {""}),
        "year_min": min((int(y) for y in years if y.isdigit()), default=None),
        "year_max": max((int(y) for y in years if y.isdigit()), default=None),
        "flag_counts": dict(flags),
        "schemas": schemas,
    }


def main() -> int:
    config = yaml.safe_load(PATHS_FILE.read_text(encoding="utf-8"))
    raw_root = Path(config["animal_food_raw_root"])
    intermediate_root = Path(config["animal_food_intermediate_root"])
    processed_root = Path(config["animal_food_processed_root"])
    outputs_root = Path(config["animal_food_outputs_root"])
    for root in [raw_root, intermediate_root, processed_root, outputs_root]:
        if not root.is_dir():
            raise RuntimeError(f"configured root unavailable: {root}")

    required_raw = [
        raw_root / "efsa_pesticides_luxembourg" / "MOPER_ALL_DATA_SSD2_2024_LU.ZIP",
        raw_root / "efsa_vmpr_belgium" / "VMPR_2024_BE.ZIP",
    ]
    for path in required_raw:
        if not path.is_file():
            raise RuntimeError(f"required raw file missing: {path}")

    manifest_rows = []
    for path in sorted(p for p in raw_root.rglob("*") if p.is_file() and not p.name.startswith("._") and not p.name.endswith(".partial")):
        relative = path.relative_to(raw_root).as_posix()
        # Later validation sources have their own immutable-source manifest.
        # Preserve the acquired pilot's 16-file denominator for reproducibility.
        if relative.startswith("validation_sources/"):
            continue
        md5 = hash_file(path, "md5")
        expected = EXPECTED_MD5.get(relative)
        manifest_rows.append(
            {
                "relative_path": relative,
                "bytes": path.stat().st_size,
                "md5": md5,
                "sha256": hash_file(path, "sha256"),
                "expected_md5": expected or "",
                "hash_status": "PASS" if expected is None or expected == md5 else "FAIL",
            }
        )
    if any(row["hash_status"] == "FAIL" for row in manifest_rows):
        raise RuntimeError("one or more raw source hashes failed")

    # A legacy comparison is optional, explicitly configured, and re-hashed.
    # Its absence must not be replaced by a historical hard-coded success.
    legacy_value = config.get("animal_food_legacy_catalogue")
    legacy_path = Path(legacy_value) if legacy_value else None
    shared_catalogue = {
        "reuse_status": "NOT_ASSESSED",
        "limitation": "No existing explicitly configured legacy catalogue; 2022 is not assumed current for 2024 codes",
    }
    if legacy_path is not None and legacy_path.is_file():
        shared_catalogue = {
            "path": str(legacy_path), "sha256": hash_file(legacy_path, "sha256"),
            "reuse_status": "CONFIGURED_FILE_HASHED_FOR_LEGACY_COMPARISON_ONLY",
            "limitation": "A current hash is not proof of scientific code compatibility; 2022 is not assumed current for 2024 codes",
        }
    technical = {
        "feed": audit_feed_csvs(raw_root / "faostat_feed" / "pilot_items"),
        "pesticide_occurrence": audit_ssd2_zip(required_raw[0], "A_PESTICIDE"),
        "veterinary_drug_occurrence": audit_ssd2_zip(required_raw[1], "B_VETERINARY_DRUG"),
        "shared_catalogue": shared_catalogue,
    }

    intermediate_root.mkdir(parents=True, exist_ok=True)
    processed_root.mkdir(parents=True, exist_ok=True)
    outputs_root.mkdir(parents=True, exist_ok=True)
    (intermediate_root / "source_schema_audit.json").write_text(
        json.dumps(technical, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (processed_root / "technical_feasibility_summary.json").write_text(
        json.dumps(technical, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    with (outputs_root / "raw_source_manifest.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(manifest_rows[0]))
        writer.writeheader()
        writer.writerows(manifest_rows)
    print(json.dumps({
        "manifest_files": len(manifest_rows),
        "feed_rows": technical["feed"]["row_count"],
        "pesticide_rows": technical["pesticide_occurrence"]["row_count"],
        "vmpr_rows": technical["veterinary_drug_occurrence"]["row_count"],
    }))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        raise

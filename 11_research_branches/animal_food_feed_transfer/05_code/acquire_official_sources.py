#!/usr/bin/env python3
"""Acquire a bounded set of official sources without overwriting raw files.

All destinations are resolved from the repository's authoritative paths.yaml.
The script deliberately downloads only the Stage-1 feasibility set; it is not a
general bulk downloader and does not imply scientific admission.
"""

from __future__ import annotations

import hashlib
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PATHS_FILE = PROJECT_ROOT / "00_admin" / "paths.yaml"


def load_simple_yaml(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def digest(path: Path, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, destination: Path, expected_md5: str | None = None) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if expected_md5 and digest(destination, "md5") != expected_md5:
            raise RuntimeError(f"existing raw file hash mismatch: {destination}")
        print(f"REUSE {destination}")
        return
    partial = destination.with_suffix(destination.suffix + ".partial")
    request = urllib.request.Request(url, headers={"User-Agent": "AFFT-source-audit/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=120) as response, partial.open("wb") as out:
            while chunk := response.read(1024 * 1024):
                out.write(chunk)
        if expected_md5 and digest(partial, "md5") != expected_md5:
            raise RuntimeError(f"downloaded raw file hash mismatch: {destination}")
        partial.rename(destination)
    finally:
        if partial.exists():
            partial.unlink()
    print(f"DOWNLOADED {destination}")


def main() -> int:
    paths = load_simple_yaml(PATHS_FILE)
    raw_root = Path(paths["animal_food_raw_root"])
    data_root = Path(paths["data_root"])
    if not data_root.is_dir() or not raw_root.is_dir():
        raise RuntimeError("configured external data roots are unavailable")
    probe = raw_root / ".write_probe"
    probe.write_text("path check only\n", encoding="utf-8")
    probe.unlink()

    files = [
        (
            "https://data.apps.fao.org/catalog/api/3/action/package_show?id=e4f1fc7d-2f74-4167-a6d8-d3dba4f384b2",
            raw_root / "faostat_feed" / "catalog_package.json",
            None,
        ),
        (
            "https://data.apps.fao.org/catalog/dataset/ff4ad234-500e-4745-800f-f200f6f9cebe/resource/a3cc17b6-0325-4bf6-b4c3-8686945e906e/download/feeds-fct-fbs-food-balances.schema.json",
            raw_root / "faostat_feed" / "feeds-fct-fbs-food-balances.schema.json",
            None,
        ),
        (
            "https://data.apps.fao.org/catalog/dataset/ff4ad234-500e-4745-800f-f200f6f9cebe/resource/f19e6078-11e7-4c0f-9cf8-310f5c15a983/download/feeds-fct-fbs-food-balances.query.sql",
            raw_root / "faostat_feed" / "feeds-fct-fbs-food-balances.query.sql",
            None,
        ),
        (
            "https://data.apps.fao.org/catalog/api/3/action/package_show?id=955a7b61-ce56-4a04-adf5-61a3012eec84",
            raw_root / "faostat_trade_metadata" / "catalog_package.json",
            None,
        ),
        (
            "https://data.apps.fao.org/catalog/dataset/62a2bd8e-08b1-45da-8044-076bb60acbcc/resource/7df37d24-665b-4d1f-b456-765842e9b9d2/download/tm-detailed-trade-matrix-schema.json",
            raw_root / "faostat_trade_metadata" / "tm-detailed-trade-matrix-schema.json",
            None,
        ),
        (
            "https://www.oecd.org/content/dam/oecd/en/publications/reports/2013/09/guidance-document-on-residues-in-livestock_39c912a3/74878553-en.pdf",
            raw_root / "methods" / "OECD_GD73_2013.pdf",
            None,
        ),
        (
            "https://zenodo.org/records/18429596/files/DCF_catalogues.zip?download=1",
            raw_root / "efsa_catalogues_2026" / "DCF_catalogues.zip",
            "66da7ba8448fe68e6bf87f40435cd1f7",
        ),
        (
            "https://zenodo.org/records/20035795/files/MOPER_ALL_DATA_SSD2_2024_LU.ZIP?download=1",
            raw_root / "efsa_pesticides_luxembourg" / "MOPER_ALL_DATA_SSD2_2024_LU.ZIP",
            "74e983751aea4ded9dd5410cd0c445dc",
        ),
        (
            "https://zenodo.org/records/19661560/files/VMPR_2024_BE.ZIP?download=1",
            raw_root / "efsa_vmpr_belgium" / "VMPR_2024_BE.ZIP",
            "b7536c29335842ec39384d78b88dff87",
        ),
    ]
    for url, destination, expected_md5 in files:
        download(url, destination, expected_md5)

    schema = json.loads((raw_root / "faostat_feed" / "feeds-fct-fbs-food-balances.schema.json").read_text())
    labels = schema["dimension"]["item_code"]["category"]["label"]
    pilot_names = {
        "Barley and products",
        "Maize and products",
        "Oats",
        "Rape and Mustardseed",
        "Soyabeans",
        "Sunflower seed",
        "Wheat and products",
    }
    sql_url = (
        "https://data.apps.fao.org/catalog/dataset/ff4ad234-500e-4745-800f-f200f6f9cebe/"
        "resource/f19e6078-11e7-4c0f-9cf8-310f5c15a983/download/feeds-fct-fbs-food-balances.query.sql"
    )
    for item_code, label in labels.items():
        if label not in pilot_names:
            continue
        query = urllib.parse.urlencode({"sql_url": sql_url, "item_code": item_code})
        safe_label = label.lower().replace(" ", "_").replace("&", "and")
        download(
            f"https://api.data.apps.fao.org/api/v2/bigquery?{query}",
            raw_root / "faostat_feed" / "pilot_items" / f"{item_code}_{safe_label}.csv",
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        raise

#!/usr/bin/env python3
"""Create aggregate, module-separated pilot summaries from admitted raw archives.

No individual result rows are copied from raw storage. The output is a technical
feasibility summary and must not be interpreted as a population exposure result.
"""

from __future__ import annotations

import csv
import io
import json
import re
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PATHS_FILE = PROJECT_ROOT / "00_admin" / "paths.yaml"


def cell_text(cell: ET.Element, shared_strings: list[str]) -> str:
    inline = "".join((node.text or "") for node in cell.iter() if node.tag.endswith("}t"))
    if inline:
        return inline
    if cell.attrib.get("t") == "s":
        value = next((node.text for node in cell if node.tag.endswith("}v")), None)
        if value is not None:
            return shared_strings[int(value)]
    return ""


def read_mtx_mapping(dcf_zip: Path) -> tuple[dict[str, str], str]:
    """Read term code/name pairs from EFSA's large inline-string workbook."""
    with zipfile.ZipFile(dcf_zip) as outer:
        candidates = [name for name in outer.namelist() if name.endswith("/MTX.xlsx") or name == "MTX.xlsx"]
        if not candidates:
            raise RuntimeError(f"MTX.xlsx not found in {dcf_zip}")
        workbook_bytes = outer.read(candidates[0])
    mapping: dict[str, str] = {}
    with zipfile.ZipFile(io.BytesIO(workbook_bytes)) as workbook:
        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in workbook.namelist():
            with workbook.open("xl/sharedStrings.xml") as shared:
                for _, element in ET.iterparse(shared, events=("end",)):
                    if element.tag.endswith("}si"):
                        shared_strings.append(
                            "".join((node.text or "") for node in element.iter() if node.tag.endswith("}t"))
                        )
                        element.clear()
        with workbook.open("xl/worksheets/sheet4.xml") as sheet:
            for _, row in ET.iterparse(sheet, events=("end",)):
                if not row.tag.endswith("}row"):
                    continue
                values: dict[str, str] = {}
                for cell in row:
                    if not cell.tag.endswith("}c"):
                        continue
                    match = re.match(r"([A-Z]+)", cell.attrib.get("r", ""))
                    if match and match.group(1) in {"A", "B"}:
                        values[match.group(1)] = cell_text(cell, shared_strings)
                if values.get("A") and values.get("B"):
                    mapping[values["A"]] = values["B"]
                row.clear()
    return mapping, str(dcf_zip)


def classify(name: str) -> str:
    lower = name.lower()
    if "feed" in lower or "fodder" in lower:
        return "feed_candidate"
    if "eggplant" in lower or "plant-based" in lower or "meat analogue" in lower:
        return "other"
    if re.search(r"\b(meat|milk|eggs?|liver|kidney|offal|muscle|fish|honey)\b", lower) or any(
        term in lower for term in ("animal fat", "body fat")
    ):
        return "animal_food_candidate"
    return "other"


def summarise(path: Path, module: str, mapping: dict[str, str]) -> tuple[list[dict], dict]:
    aggregates: dict[tuple[str, str, str], Counter] = defaultdict(Counter)
    unresolved = Counter()
    all_samples: set[str] = set()
    selected_samples: dict[str, set[str]] = defaultdict(set)
    selected_rows = Counter()
    selected_quantified = Counter()
    selected_strategies: dict[str, Counter] = defaultdict(Counter)
    selected_strategy_samples: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    selected_evaluations: dict[str, Counter] = defaultdict(Counter)
    selected_qualitative: dict[str, Counter] = defaultdict(Counter)
    with zipfile.ZipFile(path) as archive, archive.open(archive.namelist()[0]) as binary:
        reader = csv.DictReader(io.TextIOWrapper(binary, encoding="utf-8-sig", newline=""))
        for row in reader:
            sample = row.get("sampId_A", "")
            all_samples.add(sample)
            code = row.get("sampMatCode.base.building", "")
            name = mapping.get(code, "")
            if not name:
                unresolved[code] += 1
            category = classify(name)
            if category == "other":
                continue
            selected_samples[category].add(sample)
            selected_rows[category] += 1
            is_quantified = row.get("resType") == "VAL" or bool(row.get("resVal") and row.get("resVal") != "N_A")
            if is_quantified:
                selected_quantified[category] += 1
            strategy = row.get("sampStrategy", "")
            selected_strategies[category][strategy] += 1
            selected_strategy_samples[category][strategy].add(sample)
            if row.get("evalCode") and row.get("evalCode") != "N_A":
                selected_evaluations[category][row["evalCode"]] += 1
            if row.get("resQualValue") and row.get("resQualValue") != "N_A":
                selected_qualitative[category][row["resQualValue"]] += 1
            key = (category, code, name)
            aggregates[key]["result_rows"] += 1
            aggregates[key]["quantified_rows"] += int(is_quantified)
            aggregates[key][f"sample::{sample}"] = 1
    rows = []
    for (category, code, name), counter in sorted(aggregates.items()):
        rows.append(
            {
                "module": module,
                "category": category,
                "matrix_code": code,
                "matrix_name": name,
                "sample_count": sum(1 for key in counter if key.startswith("sample::")),
                "result_rows": counter["result_rows"],
                "quantified_rows": counter["quantified_rows"],
            }
        )
    overview = {
        "archive": str(path),
        "all_unique_samples": len(all_samples - {""}),
        "selected_unique_samples": {key: len(value - {""}) for key, value in selected_samples.items()},
        "selected_result_rows": dict(selected_rows),
        "selected_quantified_rows": dict(selected_quantified),
        "selected_strategy_rows": {key: dict(value) for key, value in selected_strategies.items()},
        "selected_strategy_samples": {
            category: {strategy: len(samples - {""}) for strategy, samples in strategies.items()}
            for category, strategies in selected_strategy_samples.items()
        },
        "selected_evaluation_rows": {key: dict(value) for key, value in selected_evaluations.items()},
        "selected_qualitative_rows": {key: dict(value) for key, value in selected_qualitative.items()},
        "unresolved_code_rows": sum(unresolved.values()),
        "top_unresolved_codes": dict(unresolved.most_common(20)),
        "classification_warning": "Keyword classification is a feasibility screen, not a validated FoodEx2 tissue crosswalk.",
    }
    return rows, overview


def main() -> int:
    config = yaml.safe_load(PATHS_FILE.read_text(encoding="utf-8"))
    raw_root = Path(config["animal_food_raw_root"])
    processed_root = Path(config["animal_food_processed_root"])
    outputs_root = Path(config["animal_food_outputs_root"])
    current_catalogue = raw_root / "efsa_catalogues_2026" / "DCF_catalogues.zip"
    if not current_catalogue.is_file():
        raise FileNotFoundError("Configured 2026 DCF catalogue missing; no legacy substitution is permitted")
    mapping, mapping_source = read_mtx_mapping(current_catalogue)

    pesticide_rows, pesticide_overview = summarise(
        raw_root / "efsa_pesticides_luxembourg" / "MOPER_ALL_DATA_SSD2_2024_LU.ZIP",
        "A_PESTICIDE",
        mapping,
    )
    vmpr_rows, vmpr_overview = summarise(
        raw_root / "efsa_vmpr_belgium" / "VMPR_2024_BE.ZIP",
        "B_VETERINARY_DRUG",
        mapping,
    )
    rows = pesticide_rows + vmpr_rows
    processed_root.mkdir(parents=True, exist_ok=True)
    outputs_root.mkdir(parents=True, exist_ok=True)
    with (processed_root / "pilot_matrix_summary.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else ["module"])
        writer.writeheader()
        writer.writerows(rows)
    overview = {
        "mapping_source": mapping_source,
        "mapping_term_count": len(mapping),
        "pesticide": pesticide_overview,
        "veterinary_drug": vmpr_overview,
    }
    (processed_root / "pilot_harmonisation_summary.json").write_text(
        json.dumps(overview, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(overview, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

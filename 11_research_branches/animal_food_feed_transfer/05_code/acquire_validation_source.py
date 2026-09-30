#!/usr/bin/env python3
"""Archive the primary JMPR study evaluation as a separate validation source."""
import hashlib
import argparse
import json
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from acquire_official_sources import load_simple_yaml, PATHS_FILE, PROJECT_ROOT

URL = "https://www.fao.org/fileadmin/templates/agphome/documents/Pests_Pesticides/JMPR/Evaluation05/2005_Glyphosate1.pdf"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', choices=['jmpr', 'li2022'], default='jmpr')
    args = parser.parse_args()
    subprocess.run([sys.executable, str(PROJECT_ROOT / "05_code/utilities/check_paths.py")],
                   cwd=PROJECT_ROOT, check=True, stdout=subprocess.DEVNULL)
    paths = load_simple_yaml(PATHS_FILE)
    url = URL if args.source == 'jmpr' else 'https://backend.orbit.dtu.dk/ws/portalfiles/portal/276005666/d1em00454a.pdf'
    filename = 'JMPR_2005_Glyphosate_evaluation.pdf' if args.source == 'jmpr' else 'Li_Xiong_Fantke_2022.pdf'
    manifest_name = 'validation_source_manifest_20260923.json' if args.source == 'jmpr' else 'li2022_source_manifest_20260923.json'
    target = Path(paths["animal_food_raw_root"]) / "validation_sources" / filename
    manifest = Path(paths["animal_food_outputs_root"]) / manifest_name
    if target.exists():
        data = target.read_bytes()
    else:
        request = urllib.request.Request(url, headers={"User-Agent": "AFFT-validation-source-audit/1.0"})
        with urllib.request.urlopen(request, timeout=45) as response:
            data = response.read(20 * 1024 * 1024 + 1)
        if len(data) > 20 * 1024 * 1024 or not data.startswith(b"%PDF"):
            raise ValueError("Not a bounded PDF response; no raw file written")
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as handle:
            handle.write(data)
    digest = hashlib.sha256(data).hexdigest()
    if manifest.exists():
        previous = json.loads(manifest.read_text())
        if previous["sha256"] != digest:
            raise ValueError("Archived validation source changed")
    else:
        manifest.write_text(json.dumps({
            "source_url": url, "raw_path": str(target), "sha256": digest,
            "bytes": len(data), "acquired_utc": datetime.now(timezone.utc).isoformat(),
            "published_checksum": None,
            "scope": "Supplemental primary-source audit; separate from the frozen 16-file pilot manifest",
        }, indent=2) + "\n")
    print(json.dumps({"pdf": str(target), "manifest": str(manifest), "sha256": digest}))


if __name__ == "__main__":
    main()

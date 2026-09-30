#!/usr/bin/env python3
"""Run and record a reproducible PubMed novelty search."""

from __future__ import annotations

import csv
import json
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path


BRANCH_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BRANCH_ROOT / "02_literature"
BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

QUERIES = {
    "pesticide_transfer_review": (
        '(pesticide*[Title/Abstract]) AND (feed*[Title/Abstract]) AND '
        '("residue transfer"[Title/Abstract] OR "transfer factor"[Title/Abstract] OR biotransfer[Title/Abstract]) '
        'AND (livestock[Title/Abstract] OR milk[Title/Abstract] OR egg*[Title/Abstract] OR meat[Title/Abstract])'
    ),
    "pesticide_feed_transfer": (
        '(pesticide residue*[Title/Abstract]) AND (feed[Title/Abstract] OR feedstuff*[Title/Abstract]) '
        'AND (livestock[Title/Abstract] OR cattle[Title/Abstract] OR poultry[Title/Abstract]) '
        'AND (milk[Title/Abstract] OR egg*[Title/Abstract] OR meat[Title/Abstract]) '
        'AND (transfer[Title/Abstract] OR carryover[Title/Abstract] OR "carry-over"[Title/Abstract])'
    ),
    "livestock_feeding_studies": (
        '(pesticide*[Title/Abstract]) AND ("feeding study"[Title/Abstract] OR "feeding studies"[Title/Abstract]) '
        'AND (livestock[Title/Abstract] OR ruminant*[Title/Abstract] OR poultry[Title/Abstract])'
    ),
    "veterinary_drug_exposure": (
        '(veterinary drug residue*[Title/Abstract]) AND (dietary exposure[Title/Abstract] OR intake[Title/Abstract]) '
        'AND (meat[Title/Abstract] OR milk[Title/Abstract] OR egg*[Title/Abstract] OR "animal-derived food"[Title/Abstract])'
    ),
    "integrated_trade_attribution": (
        '(pesticide*[Title/Abstract]) AND (feed trade[Title/Abstract] OR traded feed[Title/Abstract]) '
        'AND (animal food*[Title/Abstract] OR milk[Title/Abstract] OR meat[Title/Abstract] OR egg*[Title/Abstract]) '
        'AND (residue*[Title/Abstract] OR exposure[Title/Abstract])'
    ),
}


def get_json(endpoint: str, params: dict[str, str]) -> dict:
    url = f"{BASE}/{endpoint}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers={"User-Agent": "AFFT-novelty-audit/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    log = {"database": "PubMed", "search_date": date.today().isoformat(), "queries": []}
    records: dict[str, dict] = {}
    for query_id, query in QUERIES.items():
        result = get_json(
            "esearch.fcgi",
            {"db": "pubmed", "term": query, "retmode": "json", "retmax": "200", "sort": "relevance"},
        )["esearchresult"]
        ids = result.get("idlist", [])
        log["queries"].append({"query_id": query_id, "query": query, "count": int(result["count"]), "returned": len(ids)})
        if ids:
            time.sleep(0.35)
            summaries = get_json(
                "esummary.fcgi",
                {"db": "pubmed", "id": ",".join(ids), "retmode": "json"},
            )["result"]
            for pmid in ids:
                item = summaries.get(pmid, {})
                if not item:
                    continue
                record = records.setdefault(
                    pmid,
                    {
                        "pmid": pmid,
                        "title": item.get("title", ""),
                        "pubdate": item.get("pubdate", ""),
                        "source": item.get("source", ""),
                        "doi": next(
                            (x.get("value", "") for x in item.get("articleids", []) if x.get("idtype") == "doi"),
                            "",
                        ),
                        "query_ids": set(),
                    },
                )
                record["query_ids"].add(query_id)
        time.sleep(0.35)

    rows = []
    for record in records.values():
        row = dict(record)
        row["query_ids"] = ";".join(sorted(row["query_ids"]))
        rows.append(row)
    rows.sort(key=lambda row: (row["pubdate"], row["pmid"]), reverse=True)
    with (OUTPUT_DIR / "pubmed_novelty_results.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["pmid", "title", "pubdate", "source", "doi", "query_ids"])
        writer.writeheader()
        writer.writerows(rows)
    (OUTPUT_DIR / "pubmed_search_log.json").write_text(
        json.dumps(log, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps({"queries": len(QUERIES), "unique_records": len(rows), "counts": {q["query_id"]: q["count"] for q in log["queries"]}}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

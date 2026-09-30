#!/usr/bin/env python3
"""Run a reproducible, open-index literature discovery audit.

This supplements, but does not claim equivalence to, subscription searches in
CAB Abstracts, Embase, Scopus, or Web of Science.
"""

from __future__ import annotations

import csv
import json
import re
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path


BRANCH = Path(__file__).resolve().parents[1]
OUT = BRANCH / "02_literature"
USER_AGENT = "AFFT-evidence-audit/1.0 (academic reproducibility audit)"

QUERIES = {
    "A_transfer": 'pesticide residues animal feed transfer carryover milk eggs tissue livestock',
    "A_burden": 'livestock dietary burden pesticide residues feed',
    "A_animal_food": 'pesticide biotransfer foods of animal origin feed',
    "A_trade": 'feed trade pesticide residues livestock animal food',
    "B_vmpr": 'veterinary drug residues dietary exposure monitoring meat milk eggs',
    "framework": 'evidence mapping data readiness exposure assessment food chemical risk',
}


def get_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def clean_doi(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value.strip(), flags=re.I).lower()


def inverted_abstract(value: dict | None) -> str:
    if not value:
        return ""
    words: list[tuple[int, str]] = []
    for word, positions in value.items():
        words.extend((int(position), word) for position in positions)
    return " ".join(word for _, word in sorted(words))


def score_record(title: str, abstract: str, modules: set[str]) -> tuple[int, str]:
    text = f"{title} {abstract}".lower()
    groups = {
        "feed": ("feed", "feedstuff", "ration", "dietary burden"),
        "pesticide": ("pesticide", "agrochemical", "plant protection"),
        "vet": ("veterinary drug", "antibiotic residue", "medicinal product"),
        "animal": ("livestock", "cattle", "cow", "poultry", "hen", "animal origin"),
        "food": ("milk", "egg", "meat", "tissue", "liver", "kidney", "animal food"),
        "transfer": ("transfer", "carryover", "biotransfer", "dietary burden"),
        "exposure": ("exposure", "monitoring", "surveillance", "risk assessment"),
        "framework": ("framework", "evidence map", "data readiness", "admission"),
    }
    hits = {name for name, terms in groups.items() if any(term in text for term in terms)}
    score = len(hits)
    if "A" in modules and {"feed", "pesticide", "animal", "food", "transfer"}.issubset(hits):
        score += 4
    if "B" in modules and {"vet", "food", "exposure"}.issubset(hits):
        score += 3
    if "F" in modules and {"framework", "exposure"}.issubset(hits):
        score += 2
    return score, ";".join(sorted(hits))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    records: dict[str, dict] = {}
    logs: list[dict] = []

    def merge(item: dict, query_id: str, source: str) -> None:
        doi = clean_doi(item.get("doi"))
        title = re.sub(r"\s+", " ", (item.get("title") or "").strip())
        if not title:
            return
        key = f"doi:{doi}" if doi else f"title:{re.sub(r'\W+', '', title.lower())}"
        module = "A" if query_id.startswith("A_") else "B" if query_id.startswith("B_") else "F"
        if key not in records:
            records[key] = {
                "title": title,
                "year": item.get("year") or "",
                "doi": doi,
                "abstract": item.get("abstract") or "",
                "sources": set(),
                "queries": set(),
                "modules": set(),
            }
        record = records[key]
        record["sources"].add(source)
        record["queries"].add(query_id)
        record["modules"].add(module)
        if not record["abstract"] and item.get("abstract"):
            record["abstract"] = item["abstract"]

    for query_id, query in QUERIES.items():
        encoded = urllib.parse.quote(query)

        openalex_url = f"https://api.openalex.org/works?search={encoded}&per-page=100"
        oa = get_json(openalex_url)
        logs.append({"database": "OpenAlex", "query_id": query_id, "query": query, "reported_total": oa["meta"]["count"], "retrieved": len(oa["results"])})
        for work in oa["results"]:
            merge({"title": work.get("display_name"), "year": work.get("publication_year"), "doi": work.get("doi"), "abstract": inverted_abstract(work.get("abstract_inverted_index"))}, query_id, "OpenAlex")

        ep_query = urllib.parse.quote(f'({query}) AND FIRST_PDATE:[1900-01-01 TO {date.today().isoformat()}]')
        ep_url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&pageSize=100&resultType=core&query={ep_query}"
        ep = get_json(ep_url)
        ep_results = ep.get("resultList", {}).get("result", [])
        logs.append({"database": "Europe PMC", "query_id": query_id, "query": query, "reported_total": ep.get("hitCount", 0), "retrieved": len(ep_results)})
        for work in ep_results:
            merge({"title": work.get("title"), "year": work.get("pubYear"), "doi": work.get("doi"), "abstract": work.get("abstractText", "")}, query_id, "Europe PMC")
        time.sleep(0.1)

    rows = []
    for record in records.values():
        score, terms = score_record(record["title"], record["abstract"], record["modules"])
        if score < 4:
            continue
        rows.append({
            "relevance_score": score,
            "module": ";".join(sorted(record["modules"])),
            "year": record["year"],
            "title": record["title"],
            "doi": record["doi"],
            "indexed_in": ";".join(sorted(record["sources"])),
            "query_ids": ";".join(sorted(record["queries"])),
            "term_groups": terms,
            "screening_status": "CANDIDATE_TITLE_ABSTRACT",
        })
    rows.sort(key=lambda row: (-int(row["relevance_score"]), -int(row["year"] or 0), row["title"].lower()))

    result_path = OUT / "expanded_open_search_results.csv"
    with result_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else ["relevance_score"])
        writer.writeheader()
        writer.writerows(rows)

    source_counts = defaultdict(int)
    for row in rows:
        for source in row["indexed_in"].split(";"):
            source_counts[source] += 1
    log = {
        "search_id": "AFFT_OPEN_DISCOVERY_20260923",
        "executed_utc": datetime.now(timezone.utc).isoformat(),
        "databases": ["OpenAlex", "Europe PMC"],
        "scope_note": "Open-index discovery audit; not equivalent to subscription searches in CAB Abstracts, Embase, Scopus, or Web of Science.",
        "queries": logs,
        "deduplicated_before_threshold": len(records),
        "candidate_records": len(rows),
        "candidate_index_counts": dict(source_counts),
        "ranking_rule": "Transparent term-group score; candidates require score >=4 and still require human screening.",
        "output": str(result_path),
    }
    log_path = OUT / "expanded_open_search_log.json"
    log_path.write_text(json.dumps(log, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"deduplicated": len(records), "candidates": len(rows), "results": str(result_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

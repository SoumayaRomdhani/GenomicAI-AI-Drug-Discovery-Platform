from __future__ import annotations

import argparse
import json
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import requests


BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def esearch(query: str, retmax: int) -> list[str]:
    response = requests.get(
        f"{BASE}/esearch.fcgi",
        params={"db": "pubmed", "term": query, "retmax": retmax, "retmode": "json"},
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    return payload["esearchresult"]["idlist"]


def efetch(pmids: list[str]) -> str:
    response = requests.get(
        f"{BASE}/efetch.fcgi",
        params={"db": "pubmed", "id": ",".join(pmids), "retmode": "xml"},
        timeout=30,
    )
    response.raise_for_status()
    return response.text


def parse_pubmed_xml(xml_text: str) -> list[dict]:
    root = ET.fromstring(xml_text)
    records = []
    for article in root.findall(".//PubmedArticle"):
        pmid = article.findtext(".//PMID")
        title = " ".join(article.findtext(".//ArticleTitle", default="").split())
        abstract_parts = [
            " ".join(elem.text.split()) for elem in article.findall(".//Abstract/AbstractText") if elem.text
        ]
        year_text = article.findtext(".//PubDate/Year")
        year = int(year_text) if year_text and year_text.isdigit() else None
        abstract = " ".join(abstract_parts).strip()
        if title and abstract:
            records.append(
                {
                    "doc_id": f"pmid-{pmid}",
                    "title": title,
                    "source": "PubMed",
                    "year": year,
                    "abstract": abstract,
                }
            )
    return records


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True, help="PubMed search query")
    parser.add_argument("--retmax", type=int, default=20)
    parser.add_argument(
        "--out",
        default="app/data/pubmed_demo.json",
        help="Output path for JSON corpus",
    )
    args = parser.parse_args()

    pmids = esearch(args.query, args.retmax)
    time.sleep(0.34)
    xml_text = efetch(pmids)
    records = parse_pubmed_xml(xml_text)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Saved {len(records)} PubMed records to {out_path}")

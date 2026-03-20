#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import json
import math
import re
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE = "https://eap.bl.uk"
SEARCH_URL = "https://eap.bl.uk/collection/EAP180-3-10/search"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; OpenDataArmenia/1.0)"
}
DELAY = 1.0
TIMEOUT = 30

OUT_CSV = "eap180_3_10_clean.csv"
OUT_JSONL = "eap180_3_10_clean.jsonl"


def get_soup(url: str) -> BeautifulSoup:
    r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")


def clean_text(text: str) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def get_total_results_and_page_size(soup: BeautifulSoup):
    text = soup.get_text(" ", strip=True)
    m = re.search(r"Showing\s+(\d+)\s+to\s+(\d+)\s+of\s+(\d+)\s+results", text, re.I)
    if not m:
        raise RuntimeError("Could not detect pagination text.")
    start_i = int(m.group(1))
    end_i = int(m.group(2))
    total = int(m.group(3))
    page_size = end_i - start_i + 1
    return total, page_size


def extract_collection_title(soup: BeautifulSoup) -> str:
    h1 = soup.find("h1")
    return clean_text(h1.get_text(" ", strip=True)) if h1 else ""


def parse_title_fields(title: str):
    t = clean_text(title).strip(' "\'“”')

    year = ""
    issue = ""
    pages = ""

    m_year = re.search(r"(\d{4})\s*$", t)
    if m_year:
        year = m_year.group(1)

    m_issue = re.search(r"\bIssue\s+(\d+)\b", t, re.I)
    if m_issue:
        issue = m_issue.group(1)

    m_pages = re.search(r"\bpages?\s+([0-9]+(?:\s*[-–]\s*[0-9]+)?)\b", t, re.I)
    if m_pages:
        pages = clean_text(m_pages.group(1)).replace(" ", "")

    return year, issue, pages


def extract_reference_from_text(text: str) -> str:
    m = re.search(r"File Ref:\s*([A-Z0-9/.-]+)", text, re.I)
    return clean_text(m.group(1)) if m else ""


def extract_results_from_page(soup: BeautifulSoup):
    results = []
    seen = set()

    # Every record links to /archive-file/...
    for a in soup.select('a[href^="/archive-file/"]'):
        href = a.get("href", "")
        item_url = urljoin(BASE, href)
        if item_url in seen:
            continue
        seen.add(item_url)

        title = clean_text(a.get_text(" ", strip=True)).strip('“”')
        if not title:
            continue

        # take a nearby text container and search inside it
        container = a
        for _ in range(5):
            if container is None:
                break
            txt = clean_text(container.get_text(" ", strip=True))
            if "File Ref:" in txt:
                break
            container = container.parent

        context_text = clean_text(container.get_text(" ", strip=True)) if container else title
        reference = extract_reference_from_text(context_text)

        year, issue, pages = parse_title_fields(title)

        results.append({
            "item_title": title,
            "item_url": item_url,
            "reference": reference,
            "year": year,
            "issue": issue,
            "pages": pages,
        })

    return results


def drop_empty_columns(rows):
    if not rows:
        return rows
    keep = []
    for key in rows[0].keys():
        if any(clean_text(str(row.get(key, ""))) not in {"", "nan", "None"} for row in rows):
            keep.append(key)
    return [{k: row.get(k, "") for k in keep} for row in rows]


def save_csv(rows, path):
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def save_jsonl(rows, path):
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main():
    first = get_soup(SEARCH_URL)
    collection_title = extract_collection_title(first)
    total, page_size = get_total_results_and_page_size(first)
    total_pages = math.ceil(total / page_size)

    print(f"Collection: {collection_title}")
    print(f"Total results: {total}")
    print(f"Page size: {page_size}")
    print(f"Total pages: {total_pages}")

    rows = []
    for page in range(total_pages):
        url = SEARCH_URL if page == 0 else f"{SEARCH_URL}?page={page}"
        print(f"[PAGE {page + 1}/{total_pages}] {url}")
        soup = get_soup(url)
        page_rows = extract_results_from_page(soup)
        rows.extend(page_rows)
        time.sleep(DELAY)

    # deduplicate by item_url
    dedup = {}
    for row in rows:
        dedup[row["item_url"]] = row
    rows = list(dedup.values())

    for row in rows:
        row["collection_title"] = collection_title

    # reorder
    ordered = []
    for row in rows:
        ordered.append({
            "collection_title": row.get("collection_title", ""),
            "item_title": row.get("item_title", ""),
            "item_url": row.get("item_url", ""),
            "reference": row.get("reference", ""),
            "year": row.get("year", ""),
            "issue": row.get("issue", ""),
            "pages": row.get("pages", ""),
        })

    ordered = drop_empty_columns(ordered)

    save_csv(ordered, OUT_CSV)
    save_jsonl(ordered, OUT_JSONL)

    print(f"Saved {len(ordered)} rows to {OUT_CSV}")
    print(f"Saved {len(ordered)} rows to {OUT_JSONL}")


if __name__ == "__main__":
    main()
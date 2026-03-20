# Ardzaganq (EAP180/3/10 Armenian periodicals) Scraper 

Scraper and dataset for metadata from the British Library Endangered Archives Programme collection EAP180/3/10, as part of the Open Data Armenia project.

This repository is part of **Open Data Armenia**, an initiative focused on collecting, structuring, and publishing open metadata about Armenian heritage collections around the world.

## Source

- **Institution:** British Library Endangered Archives Programme
- **Collection:** EAP180/3/10 Armenian periodicals metadata
- **Collection URL:** https://eap.bl.uk/collection/EAP180-3-10/search

## What this repository contains

- scraper code for collecting collection-level/item-level metadata
- cleaned exported dataset files
- basic project documentation for reuse and verification

## Output files

After running the scraper, the main output files are:

- `eap180_3_10_clean.csv`
- `eap180_3_10_clean.jsonl`

## Dataset scope

This dataset contains metadata scraped from the collection search/results pages for the specified EAP collection.

Kept columns:

- `collection_title`
- `item_title`
- `item_url`
- `reference`
- `year`
- `issue`
- `pages`

## Dataset notes

This collection is highly uniform, so some fields were intentionally not kept as separate columns because they are constant or not analytically useful for this dataset.

Collection-wide notes:

- language: Armenian
- script: Armenian
- material/support: paper

## How to run

1. Create and activate a virtual environment
2. Install dependencies
3. Run the scraper

```bash
pip install -r requirements.txt
python main.py
```

## Method

The scraper:
- requests the collection search pages
- extracts item links and visible metadata
- parses title patterns to separate `year`, `issue`, and `pages`
- saves cleaned tabular outputs in CSV and JSONL

## Important notice

This repository republishes **metadata only** for research, documentation, and open data purposes.

The underlying collection, images, texts, scans, and all associated rights remain the property of their respective owners, custodians, or rights holders. Please refer to the source institution for rights, reuse conditions, and access policies.

## Open Data Armenia

This repository is part of **Open Data Armenia** and contributes to documenting Armenian heritage materials dispersed across archives, libraries, museums, and digital collections worldwide.

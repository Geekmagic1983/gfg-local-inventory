#!/usr/bin/env python3
"""
Gifts for Geeks — Local Inventory Feed Generator
Fetches the ShopWired product feed and outputs a Google-compliant
local product inventory TSV for Merchant Center account 3308669.

Store code: GFG-LE1
"""

import urllib.request
import xml.etree.ElementTree as ET
import csv
import os

FEED_URL = "https://www.giftsforgeeks.org.uk/feed/google?show=all"
STORE_CODE = "GFG-LE1"
OUTPUT_PATH = "docs/local-inventory.tsv"

# Categories to exclude from local listings (online-only products)
# Spray paints can't be shipped from store and may not suit local listing
EXCLUDED_PRODUCT_TYPES = [
    "Citadel Spray Paints",
    "Army Painter Sprays",
    "Colour Forge Sprays",
]

def fetch_feed(url):
    print(f"Fetching feed from {url}...")
    req = urllib.request.Request(url, headers={"User-Agent": "GFG-LocalFeed/1.0"})
    with urllib.request.urlopen(req, timeout=60) as response:
        return response.read()

def parse_feed(xml_data):
    root = ET.fromstring(xml_data)
    ns = {"g": "http://base.google.com/ns/1.0"}
    items = []

    for item in root.findall(".//item"):
        item_id = item.findtext("id", "").strip()
        if not item_id:
            continue

        availability_raw = item.findtext("g:availability", "", ns).strip().lower()

        # Only include in_stock products
        if availability_raw != "in stock":
            continue

        availability = "in_stock"
        quantity = 1

        # Check product type exclusions
        product_types = [pt.text for pt in item.findall("g:product_type", ns) if pt.text]
        excluded = any(
            exc.lower() in " ".join(product_types).lower()
            for exc in EXCLUDED_PRODUCT_TYPES
        )
        if excluded:
            continue

        items.append({
            "store_code": STORE_CODE,
            "id": item_id,
            "quantity": quantity,
            "availability": availability,
        })

    return items

def write_tsv(items, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["store_code", "id", "quantity", "availability"],
            delimiter="\t",
        )
        writer.writeheader()
        writer.writerows(items)
    print(f"Written {len(items)} products to {output_path}")

def main():
    xml_data = fetch_feed(FEED_URL)
    items = parse_feed(xml_data)
    write_tsv(items, OUTPUT_PATH)
    print("Done.")

if __name__ == "__main__":
    main()

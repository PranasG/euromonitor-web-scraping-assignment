
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import json
import re
import pandas as pd

BASE_URL = (
    "https://www.cellarbrations.com.au/sm/delivery/rsid/144981/"
    "categories/spirits/whisky-id-Whisky_Food"
)

all_products = []
seen_ids = set()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)

    try:
        page = browser.new_page()

        page_number = 1

        while True:
            skip = (page_number - 1) * 30
            url = f"{BASE_URL}?page={page_number}&skip={skip}"

            print(f"\nOpening page {page_number}: {url}")

            response = page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=60000
            )

            # Wait for the product cards to appear on the page

            # wait for the product cards to appear on the page
            try:
                page.locator(
                    'article[data-testid^="ProductCardWrapper-"]'
                ).first.wait_for(state="attached", timeout=20000)

            except Exception:
                print("No product cards appeared within 20 seconds.")
                print("Page title:", page.title())
                print("Current URL:", page.url)

            html = page.content()

            soup = BeautifulSoup(html, "html.parser")

            product_cards = soup.select(
                'article[data-testid^="ProductCardWrapper-"]'
            )

            print("Products found:", len(product_cards))

            # Jei produktų nebėra, stabdome ciklą
            if not product_cards:
                if page_number == 1:
                    raise RuntimeError(
                        "No products found on the first page. "
                        "Check whether the website loaded correctly."
                    )

                if previous_page_count < 30:
                    print("Pagination complete.")
                    break

                raise RuntimeError(
                    f"Page {page_number} returned no products. "
                    "This may be a loading failure or access challenge."
                )

            for card in product_cards:
                product_id = card["data-testid"].split("-")[-1]

                if product_id in seen_ids:
                    continue

                name_element = card.select_one(
                    '[data-testid$="-ProductNameTestId"]'
                )

                link_element = card.select_one(
                    'a[href*="/product/"]'
                )

                image_element = card.select_one("img")

                price_element = card.select_one(
                    '[class*="ProductPrice--"]'
                )

                if not name_element or not link_element:
                    continue

                product_name = name_element.get_text(" ", strip=True)
                product_name = product_name.replace(
                    "Open Product Description", ""
                ).strip()

                image_url = (
                    image_element.get("src")
                    if image_element else None
                )

                price = (
                    price_element.get_text(strip=True)
                    if price_element else ""
                )

                size_match = re.search(
                    r"(\d+(?:\.\d+)?)\s*(mL|L|cl)\b",
                    product_name,
                    re.IGNORECASE
                )

                units = size_match.group(1) if size_match else ""
                measuring_units = size_match.group(2) if size_match else ""

                description_container = card.select_one(
                    f'[id="productCard_title__{product_id}"]'
                )

                description = ""

                if description_container:
                    paragraphs = description_container.select("p")

                    if len(paragraphs) >= 2:
                        description = paragraphs[1].get_text(
                            " ", strip=True
                        )

                description = BeautifulSoup(
                    description, "html.parser"
                ).get_text(" ", strip=True)

                product = {
                    "product_name": product_name,
                    "product_id": str(product_id),
                    "image": [image_url] if image_url else [],
                    "url": link_element["href"],
                    "price": str(price),
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                    "measuring_units": measuring_units,
                    "units": units,
                    "description": description
                }

                all_products.append(product)
                seen_ids.add(product_id)

            previous_page_count = len(product_cards)
            page_number += 1

        # Saving the results to a JSON file
        with open(
            "cellarbrations_products.json",
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                all_products,
                f,
                ensure_ascii=False,
                indent=4
            )

        print("Saved to cellarbrations_products.json")

        pd.DataFrame(all_products).to_csv(
            "cellarbrations_products.csv",
            index=False,
            encoding="utf-8-sig"
        )

        print("Saved to cellarbrations_products.csv")

        print("\nTOTAL UNIQUE PRODUCTS:", len(all_products))

        descriptions_found = sum(
            1 for product in all_products
            if product["description"]
        )

        print("Descriptions found:", descriptions_found)
        print(
            "Descriptions missing:",
            len(all_products) - descriptions_found
        )

    finally:
        browser.close()

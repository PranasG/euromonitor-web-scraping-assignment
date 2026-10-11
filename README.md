# Euromonitor Web Scraping Assignment

This repository contains my solutions for the two web scraping tasks.

## Task 1 – Glossier

Scraped products from the Glossier website.

The solution includes:
- Product names, IDs, URLs, images and prices
- Scraping timestamps
- Pagination
- Product descriptions
- Product variants
- US region product data

The scraper is written in a Jupyter Notebook (`glossier_scraper.ipynb`).

Results are saved in CSV files.

## Task 2 – Cellarbrations

Scraped whisky products from the Cellarbrations website.

The solution includes:
- Product names, IDs, URLs, images and prices
- Scraping timestamps
- Product sizes and measuring units
- Pagination
- Product descriptions

The scraper is written in Python (`cellarbrations_scraper.py`) using Playwright and BeautifulSoup.

Results are saved in CSV and JSON files.

## Installation

Install the required libraries:

```bash
pip install -r requirements.txt
```

Install Chromium for Playwright:

```bash
python -m playwright install chromium
```

## Running the code

**Task 1:** Open `glossier_scraper.ipynb` in Jupyter Notebook and run the cells.

**Task 2:** Run the Python script:

```bash
python cellarbrations_scraper.py
```

The scraped results are included in the repository.
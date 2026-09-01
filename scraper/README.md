## Target classification

Target: Books to Scrape

Purpose: This is a public sandbox designed to allow people to learn and practise web scraping.

Scope: Only the first 3 catalogue pages will be processed.

Data collected: Book title, product URL, price text, availability text,
rating text, description, source page, and timestamp.

Reason: This site is specifically provided as a scraping practice sandbox,
so it is appropriate for this learning assignment.

Robots.txt: 404 Not Found  nginx/1.21.6

I will not reuse this code on another site without checking its rules and terms first.

## My Lane
Python Lane

## How to install it

1. Pip install requests, beautifulsoup4, pydantic
    \'''
2. Run the scraper:
    \''' 
    python scr/main.py
    \'''
3. Output appears in 'output/books.json', 'output/errors.json', and 'output/run-report.json'

## Record Schema
| Field | Type | Required | Extras |
|-------|------|----------|-------|
| title | string | Yes | |
| product_url | string | Yes | Absolute URL |
| price_text | string | Yes | |
| price_gbp | number | Yes | Parsed from price_text |
| availability_text | string | Yes | |
| rating_text | string | No | |
| description | string | No | null when the book has no description |
| source_page | string | Yes | |
| fetched_at | string | Yes | ISO 8601 UTC timestamp |


## Politeness Rules

- Every real request sends an honest user-agent identifying this project and a link to the repo
- 10-second timeout on every request
- At least 5-second delay between real requests while cached pages don't have a delay as they fon't need oen
- Status code checked before parsing anything
- Failed requests retry once on timeout but never on 404/403
- Development reads from a local cache instead of re-requesting the site

One limitation would be that this simple scraper only scrapes the first 3 catalogue pages not the full catalogue

## Run - Report.json

{
  "start_time": "2026-09-01T21:54:40.702408+00:00",
  "duration_seconds": 103.8567,
  "pages_fetched": 60,
  "cache_hits": 3,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 1
}

## Why this assignment doesn't need a browser
This assignment doesn't need a browser because the data is already in the HTML the server sends, so a browser would only add cost


## Ethical consideration
Always check for an official API before resorting to web scraping.
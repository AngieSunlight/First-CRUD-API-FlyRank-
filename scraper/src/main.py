import time
import requests
import json
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timezone
from pydantic import BaseModel, ValidationError
from typing import Optional

headers = {
    "User-Agent": "FlyRankInternship-A9/1.0 (+https://github.com/AngieSunlight/First-CRUD-API-FlyRank-)"
}

start_url = "https://books.toscrape.com/catalogue/page-1.html"

class books(BaseModel):
    title: str
    product_url: str
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: Optional[str] = None
    description: Optional[str] = None
    source_page: str
    fetched_at: str

def fetch_else_cache(url, cache_file):
    if cache_file.exists():
        print(f"CACHE HIT {url}")
        html = cache_file.read_text(encoding="utf-8")
        print(f"Response size: {len(html)} bytes")
        return html, "cache_hit"

    print(f"FETCH {url}")

    for attempt in range(2):
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=10
            )
        except requests.exceptions.RequestException as e:
            print(f"Fetch failed due to network error: {e}")
            if attempt ==  0:
                time.sleep(1)
                continue
            return None, "failed"

        if response.status_code == 200:
            # Ensures that the price is in the correct format
            response.encoding = "utf-8"
            html = response.text
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            cache_file.write_text(html, encoding="utf-8")
            print(f"Response size: {len(html)} bytes")
            return html, "fetched"

        if response.status_code in (404, 403):
                print(f"Fetch failed: {response.status_code} (not retrying)")
                return None, "failed"

        if response.status_code >= 500:
            print(f"Fetch failed: {response.status_code} (server error, retrying)")
            if attempt == 0:
                time.sleep(1)
                continue
            return None, "failed"

        print(f"Fetch failed: {response.status_code}")
        return None, "failed"

    return None, "failed"

def get_book_links(html):
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for h3 in soup.find_all("h3"):
        a_tag = h3.find("a")
        links.append(a_tag["href"])
    return links

def get_next_link(html):
    soup = BeautifulSoup(html, "html.parser")
    next_li = soup.find("li", class_="next")
    if next_li is None:
        return None
    return next_li.find("a")["href"]

def extract(html, product_url, source_page):
    soup = BeautifulSoup(html, "html.parser")
    product_area = soup.find("div", class_ = "product_main")
    title = product_area.find("h1").get_text(strip=True)
    price_el = product_area.find("p", class_="price_color")
    price_text = price_el.get_text(strip=True) if price_el else None
    availability_el = product_area.find("p", class_ = "availability")
    availability_text = availability_el.get_text(strip=True) if availability_el else None
    rating_el = product_area.find("p", class_="star-rating")
    rating_text = rating_el["class"][1] if rating_el else None
    description_el = soup.find("div", id="product_description")
    if description_el:
        sibling_p = description_el.find_next_sibling("p")
        description = sibling_p.get_text(strip=True)
    else:
        description = None
    return {
        "title": title,
        "product_url": product_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": datetime.now(timezone.utc).isoformat()
    }

def price_convert(price_text):
    if price_text is None:
        return None
    change = price_text.replace("£", "").strip()
    return float(change)

# tracking for the run-report
start = datetime.now(timezone.utc)
pages = 0
cache_hits = 0
failures = 0

all_links = []
page_count = 0
current_url = start_url
max_num = 3

while current_url and page_count < max_num:
    # Build the cache names for the page
    page_count += 1
    cache_file = Path(f"cache/catalogue-page-{page_count}.html")
    was_cached = cache_file.exists()

    # Fetch the page, else break
    html, fetch_status = fetch_else_cache(current_url, cache_file)

    if fetch_status == "cache_hit":
        cache_hits += 1
    elif fetch_status == "fetched":
        pages += 1
    elif fetch_status == "failed":
        failures += 1

    if html is None:
        break

    if not was_cached:
        time.sleep(0.5)

    # Gets book links from the html and converts each one to an absolute URL
    book_links = get_book_links(html)
    for link in book_links:
        absolute_url = urljoin(current_url, link)
        all_links.append({"url": absolute_url, "source_page": current_url})

    # Determines whether the while condition is being held
    next_href = get_next_link(html)
    if next_href is None:
        current_url = None
    else:
        current_url = urljoin(current_url, next_href)

seen_urls = set()
unique_book_entries = []
for entry in all_links:
    if entry["url"] not in seen_urls:
        seen_urls.add(entry["url"])
        unique_book_entries.append(entry)

# broken url attempt
unique_book_entries.append({
    "url": "https://books.toscrape.com/123/my-favourite-book/index.html",
    "source_page": "test"
})

records = []
for i, entry in enumerate(unique_book_entries, start=1):
    cache_file = Path(f"cache/book-{i}.html")
    was_cached = cache_file.exists()
    html, fetch_status = fetch_else_cache(entry["url"], cache_file)

    if fetch_status == "cache_hit":
        cache_hits += 1
    elif fetch_status == "fetched":
        pages += 1
    elif fetch_status == "failed":
        failures += 1

    if html is None:
        continue
    if not was_cached:
        time.sleep(0.5)
    record = extract(html, entry["url"], entry["source_page"])
    records.append(record)

print(records[0])
print(f"detail_pages={len(records)}")
print(f"catalogue_pages={page_count}")
print(f"discovered={len(all_links)}")
print(f"unique_urls={len(unique_book_entries)}")


valid_records = []
error_records = []
for raw in records:
    try:
        validated = books(**{**raw, "price_gbp": price_convert(raw["price_text"])})
        valid_records.append(validated.model_dump())
    except ValidationError as e:
        error_records.append({"record": raw, "reason": str(e)})

Path("output").mkdir(parents=True, exist_ok=True)  # creates folder called output
# creates a file, takes python lists if dicts and writes it in this open file as json
json.dump(valid_records, open("output/books.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
json.dump(error_records, open("output/errors.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)

print(f"valid_records={len(valid_records)}")
print(f"error_records={len(error_records)}")

# run report
end_time = datetime.now(timezone.utc)
duration_seconds = (end_time - start).total_seconds()

report = {
    "start_time": start.isoformat(),
    "duration_seconds": duration_seconds,
    "pages_fetched": pages,
    "cache_hits": cache_hits,
    "valid_records": len(valid_records),
    "invalid_records": len(error_records),
    "failed_pages": failures
}

json.dump(report, open("output/run-report.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)

print(f"failed_pages={failures}")
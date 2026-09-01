import requests
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timezone
import time

headers = {
    "User-Agent": "FlyRankInternship-A9/1.0 (+https://github.com/AngieSunlight/First-CRUD-API-FlyRank-)"
}

start_url = "https://books.toscrape.com/catalogue/page-1.html"

def fetch_else_cache(url, cache_file):
    if cache_file.exists():
        print(f"CACHE HIT {url}")
        html = cache_file.read_text(encoding="utf-8")
        print(f"Response size: {len(html)} bytes")
        return html

    print(f"FETCH {url}")

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )
    except requests.exceptions.RequestException as e:
        print(f"Fetch failed due to network error: {e}")
        return None

    if response.status_code != 200:
        print(f"Fetch failed: {response.status_code}")
        return None

    response.encoding = "utf-8"
    html = response.text

    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(html, encoding="utf-8")

    print(f"Response size: {len(html)} bytes")

    return html

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
    html = fetch_else_cache(current_url, cache_file)
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

records = []
for i, entry in enumerate(unique_book_entries, start=1):
    cache_file = Path(f"cache/book-{i}.html")
    was_cached = cache_file.exists()
    html = fetch_else_cache(entry["url"], cache_file)
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
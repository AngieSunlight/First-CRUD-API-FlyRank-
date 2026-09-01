import requests
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
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
    absolute_links = [urljoin(current_url, link) for link in book_links]
    all_links.extend(absolute_links)

    # Determines whether the while condition is being held
    next_href = get_next_link(html)
    if next_href is None:
        current_url = None
    else:
        current_url = urljoin(current_url, next_href)

unique_links = list(set(all_links))

print(f"catalogue_pages={page_count}")
print(f"discovered={len(all_links)}")
print(f"unique_urls={len(unique_links)}")
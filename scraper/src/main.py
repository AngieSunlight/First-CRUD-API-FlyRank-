import requests
from pathlib import Path

url = "https://books.toscrape.com/catalogue/page-1.html"

headers = {
    "User-Agent": "FlyRankInternship-A9/1.0 (+https://github.com/AngieSunlight/First-CRUD-API-FlyRank-)"
}

cache_file = Path("cache/catalogue-page-1.html")

if cache_file.exists():
    print("CACHE HIT")
    html = cache_file.read_text(encoding="utf-8")
else:
    print("FETCH")

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )
    except requests.exceptions.RequestException as e:
        print(f"Fetch failed due to network error: {e}")
        exit()

    if response.status_code != 200:
        print(f"Fetch failed: {response.status_code}")
        exit()

    html = response.text

    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(html, encoding="utf-8")

print(f"Response size: {len(html)} bytes")
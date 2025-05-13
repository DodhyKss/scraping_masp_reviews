import requests
import time
import json

API_KEY = "9edd557854c90ff5653bbe8da4e5233c1d2affe3ead640efe73aa587c8774a91"
cafes = []
reviews = []
start = 0

# Step 1: Ambil daftar cafe (min 40)
while len(cafes) < 40:
    params = {
        "engine": "google_maps",
        "q": "cafe area tamalanrea makassar",
        "ll": "@-5.1390782,119.4872171,14z",  # Koordinat Tamalanrea
        "type": "search",
        "start": start,
        "api_key": API_KEY
    }

    response = requests.get("https://serpapi.com/search.json", params=params)
    data = response.json()

    results = data.get("local_results", [])
    if not results:
        print("No more results found.")
        break

    cafes.extend(results)
    print(f"Fetched {len(cafes)} cafes...")
    start += 20
    time.sleep(1)

# Truncate jika lebih dari 40
cafes = cafes[:40]

# Step 2: Simpan data cafe ke file
with open("cafes_tamalanrea.json", "w", encoding="utf-8") as f:
    json.dump(cafes, f, ensure_ascii=False, indent=2)

# Step 3: Ambil review dari setiap cafe (max 50 reviews per cafe)
for i, cafe in enumerate(cafes, start=1):
    place_id = cafe.get("place_id")
    if not place_id:
        continue

    print(f"[{i}] Fetching up to 50 reviews for: {cafe.get('title')}")

    params = {
        "engine": "google_maps_reviews",
        "place_id": place_id,
        "api_key": API_KEY,
        "reviews_limit": 50  # Limit to 50 reviews
    }

    response = requests.get("https://serpapi.com/search.json", params=params)
    review_data = response.json()

    review_results = review_data.get("reviews", [])
    reviews.append({
        "cafe_name": cafe.get("title"),
        "place_id": place_id,
        "address": cafe.get("address"),
        "reviews": review_results
    })

    time.sleep(1)

# Step 4: Simpan review ke file json
with open("cafe_reviews.json", "w", encoding="utf-8") as f:
    json.dump(reviews, f, ensure_ascii=False, indent=2)

print("✅ Selesai! Data cafe dan review disimpan.")

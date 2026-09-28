"""
Traveling Panda Image Fetching Service
Fetches real high-quality images for specific attraction spots, destination sights, and recommended hotels
from Wikimedia Commons & Unsplash APIs, and caches them locally for display, PDF, DOCX, and JPG exports.
"""
import os
import re
import requests
from PIL import Image

IMAGE_CACHE_DIR = r"e:\Antigravity\outputs\image_cache"
HEADERS = {"User-Agent": "TravelingPanda/1.0 (educational travel app)"}

def search_place_images(query: str, count: int = 2) -> list:
    """Fetch high-res image URLs from Wikimedia Commons."""
    urls = []
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php", params={
            "action": "query", "list": "search",
            "srsearch": f"{query} filetype:bitmap",
            "srnamespace": 6, "srlimit": count * 2, "format": "json"
        }, timeout=8, headers=HEADERS)
        
        if r.status_code == 200:
            results = r.json().get("query", {}).get("search", [])
            titles = [x["title"] for x in results if not any(b in x["title"].lower() for b in [".svg", ".png", "map", "flag", "icon", "logo"])]
            if titles:
                r2 = requests.get("https://commons.wikimedia.org/w/api.php", params={
                    "action": "query", "titles": "|".join(titles[:count]),
                    "prop": "imageinfo", "iiprop": "url|size", "format": "json"
                }, timeout=8, headers=HEADERS)
                pages = r2.json().get("query", {}).get("pages", {})
                for _, page in pages.items():
                    ii_list = page.get("imageinfo", [])
                    if ii_list and ii_list[0].get("url"):
                        url = ii_list[0]["url"]
                        urls.append(url)
    except Exception as e:
        print(f"Image search error for '{query}': {e}")

    # Fallback to unsplash source if wikimedia yields fewer
    if len(urls) < count:
        clean_q = re.sub(r'[^\w\s]', '', query).replace(" ", ",")
        for i in range(count - len(urls)):
            urls.append(f"https://source.unsplash.com/800x600/?{clean_q},{i}")
            
    return urls[:count]

def download_and_cache_image(url: str, filename: str) -> str | None:
    """Download image URL and save as local JPG file. Returns local path or None."""
    os.makedirs(IMAGE_CACHE_DIR, exist_ok=True)
    local_path = os.path.join(IMAGE_CACHE_DIR, filename)

    if os.path.exists(local_path) and os.path.getsize(local_path) > 10000:
        return local_path

    try:
        r = requests.get(url, timeout=12, stream=True, headers=HEADERS)
        if r.status_code == 200:
            with open(local_path, "wb") as f:
                for chunk in r.iter_content(131072):
                    f.write(chunk)
            
            # Verify and normalize to JPG using Pillow
            with Image.open(local_path) as img:
                img = img.convert("RGB")
                img.save(local_path, "JPEG", quality=85)
            
            if os.path.getsize(local_path) > 5000:
                return local_path
    except Exception as e:
        print(f"Failed to download image {url}: {e}")
        if os.path.exists(local_path):
            try: os.remove(local_path)
            except: pass
    return None

def extract_attraction_spots(destination: str, itinerary_text: str) -> list:
    """Extract specific attraction/spot names mentioned across itinerary days."""
    spots = []
    # Pattern for bold spot names
    bold_items = re.findall(r'\*\*([^*]+)\*\*', itinerary_text)
    ignore_words = ['day', 'morning', 'afternoon', 'evening', 'budget', 'tips', 'how to reach', 'stay', 'hotel', 'cost', 'total', 'breakfast', 'lunch', 'dinner', 'night']
    
    for item in bold_items:
        clean = item.strip()
        if any(w in clean.lower() for w in ignore_words):
            continue
        if len(clean) > 3 and len(clean) < 45 and clean not in spots:
            spots.append(clean)

    if len(spots) < 4:
        lines = itinerary_text.split('\n')
        for line in lines:
            line_s = line.strip()
            if line_s.startswith('- ') or line_s.startswith('* ') or line_s.startswith('### '):
                clean_l = re.sub(r'^[#\*-\s]+', '', line_s).split(':')[0].strip()
                if not any(w in clean_l.lower() for w in ignore_words) and len(clean_l) > 3 and len(clean_l) < 40 and clean_l not in spots:
                    spots.append(clean_l)

    return spots[:10]  # Return up to 10 distinct attraction spots

def fetch_trip_gallery(destination: str, itinerary_text: str) -> dict:
    """
    Parses destination spots and hotel names from itinerary text,
    fetches dedicated real photos for EACH spot and hotel, and caches them locally.
    Returns dict:
      {
         "destination_images": [{"name": spot_name, "path": local_path}, ...],
         "hotel_images": [{"name": hotel_name, "path": local_path}, ...]
      }
    """
    os.makedirs(IMAGE_CACHE_DIR, exist_ok=True)
    result = {"destination_images": [], "hotel_images": []}

    # 1. Extract Specific Attraction Spots
    spots = extract_attraction_spots(destination, itinerary_text)
    if not spots:
        spots = [f"{destination} Top Sight 1", f"{destination} Scenic View 2", f"{destination} Famous Temple", f"{destination} Beach Landmark"]

    for idx, spot_name in enumerate(spots):
        urls = search_place_images(f"{spot_name} {destination}", count=1)
        if urls:
            safe_filename = f"spot_{idx}_{re.sub(r'[^a-z0-9]', '_', spot_name.lower())[:30]}.jpg"
            path = download_and_cache_image(urls[0], safe_filename)
            if path:
                result["destination_images"].append({
                    "name": spot_name,
                    "path": path
                })

    # 2. Extract suggested hotel names from itinerary markdown
    hotel_matches = re.findall(r'(?:Hotel|Resort|Hostel|Stay|Palace|Villa|Inn|Lodge)\s+([A-Z][A-Za-z0-9\s\-\']+)', itinerary_text)
    if not hotel_matches:
        hotel_matches = re.findall(r'\*\*([^*]+(?:Hotel|Resort|Hostel|Stay|Palace|Villa|Inn|Lodge)[^*]*)\*\*', itinerary_text)

    unique_hotels = []
    for h in hotel_matches:
        h_clean = h.strip()
        if len(h_clean) > 3 and len(h_clean) < 40 and h_clean not in unique_hotels:
            unique_hotels.append(h_clean)

    if not unique_hotels:
        unique_hotels = [f"Budget Hotel in {destination}", f"Luxury Resort in {destination}"]

    for idx, hotel_name in enumerate(unique_hotels[:4]):
        h_urls = search_place_images(f"{hotel_name} {destination}", count=1)
        if h_urls:
            safe_filename = f"hotel_{idx}_{re.sub(r'[^a-z0-9]', '_', hotel_name.lower())[:30]}.jpg"
            path = download_and_cache_image(h_urls[0], safe_filename)
            if path:
                result["hotel_images"].append({
                    "name": hotel_name,
                    "path": path
                })

    return result

"""
Pre-download a curated library of free India travel videos from Wikimedia Commons.
Run once to populate e:/Antigravity/assets/broll_library/
No API key needed - uses Wikimedia Commons (free, open license).
"""
import os
import sys
import json
import requests

LIBRARY_DIR = r"e:\Antigravity\assets\broll_library"
INDEX_FILE  = os.path.join(LIBRARY_DIR, "index.json")
H = {"User-Agent": "TravelingPanda/1.0 (educational YouTube channel project)"}

# Curated search queries for each destination
DESTINATION_QUERIES = {
    "goa":        ["filetype:video Goa beach India", "filetype:video Goa sea", "filetype:video Baga beach"],
    "kerala":     ["filetype:video Kerala backwaters", "filetype:video Kerala India nature", "filetype:video Munnar tea"],
    "rajasthan":  ["filetype:video Rajasthan India", "filetype:video Jaipur India", "filetype:video Thar desert"],
    "ladakh":     ["filetype:video Ladakh India", "filetype:video Himalayas India", "filetype:video Leh India"],
    "kashmir":    ["filetype:video Kashmir India", "filetype:video Dal Lake India", "filetype:video Srinagar"],
    "mumbai":     ["filetype:video Mumbai India", "filetype:video Marine Drive Mumbai", "filetype:video Bombay India"],
    "delhi":      ["filetype:video Delhi India", "filetype:video India Gate Delhi", "filetype:video Old Delhi"],
    "varanasi":   ["filetype:video Varanasi India", "filetype:video Ganges India", "filetype:video Banaras"],
    "agra":       ["filetype:video Agra India", "filetype:video Taj Mahal India"],
    "shimla":     ["filetype:video Shimla India", "filetype:video Himachal Pradesh India"],
    "andaman":    ["filetype:video Andaman India", "filetype:video Havelock Island India"],
    "rishikesh":  ["filetype:video Rishikesh India", "filetype:video Ganges river India"],
    "spiti":      ["filetype:video Spiti Valley India", "filetype:video Himachal Pradesh mountains"],
    "ooty":       ["filetype:video Ooty India", "filetype:video Nilgiris India Tamil Nadu"],
    "udaipur":    ["filetype:video Udaipur Rajasthan", "filetype:video Lake Pichola India"],
    "general":    ["filetype:video India travel scenic", "filetype:video India nature", "filetype:video India landscape"],
}

def search_wikimedia(query, limit=5):
    """Search Wikimedia Commons for video files."""
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php", params={
            "action": "query", "list": "search",
            "srsearch": query, "srnamespace": 6,
            "srlimit": limit, "format": "json"
        }, timeout=15, headers=H)
        if r.status_code == 200 and r.content:
            return r.json().get("query", {}).get("search", [])
    except Exception as e:
        print(f"  Search error: {e}")
    return []


def get_video_url(title):
    """Get the direct download URL for a Wikimedia file."""
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php", params={
            "action": "query", "titles": title,
            "prop": "videoinfo", "viprop": "url|size|mime|duration",
            "format": "json"
        }, timeout=12, headers=H)
        if r.status_code == 200 and r.content:
            pages = r.json().get("query", {}).get("pages", {})
            for _, page in pages.items():
                vi_list = page.get("videoinfo", [])
                if vi_list:
                    vi = vi_list[0]
                    return {
                        "url":      vi.get("url", ""),
                        "size":     vi.get("size", 0),
                        "mime":     vi.get("mime", ""),
                        "duration": vi.get("duration", 0),
                        "title":    title
                    }
    except Exception as e:
        print(f"  URL fetch error: {e}")
    return None


def download_video(url, out_path):
    """Download a video file. Returns True on success."""
    try:
        r = requests.get(url, timeout=120, stream=True, headers=H)
        if r.status_code == 200:
            with open(out_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=131072):
                    if chunk:
                        f.write(chunk)
            size = os.path.getsize(out_path)
            if size > 100_000:
                return True
            os.remove(out_path)
    except Exception as e:
        print(f"  Download error: {e}")
    return False


def build_library():
    """Download curated India travel clips for all destinations."""
    os.makedirs(LIBRARY_DIR, exist_ok=True)

    # Load existing index
    index = {}
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "r") as f:
            index = json.load(f)

    total_new = 0

    for dest, queries in DESTINATION_QUERIES.items():
        dest_dir = os.path.join(LIBRARY_DIR, dest)
        os.makedirs(dest_dir, exist_ok=True)
        dest_clips = index.get(dest, [])
        already = len([c for c in dest_clips if os.path.exists(c["path"])])

        if already >= 3:
            print(f"[{dest.upper()}] Already have {already} clips. Skipping.")
            continue

        print(f"\n[{dest.upper()}] Downloading clips...")

        for query in queries:
            if len([c for c in dest_clips if os.path.exists(c.get("path",""))]) >= 3:
                break

            results = search_wikimedia(query, limit=6)
            for res in results:
                title = res["title"]
                if any(c.get("title") == title for c in dest_clips):
                    continue  # already downloaded

                info = get_video_url(title)
                if not info:
                    continue

                size_mb = info["size"] / 1024 / 1024
                dur = info["duration"]

                # Only accept: video type, 0.5-25MB, 5-120 seconds
                if "video" not in info["mime"]:
                    continue
                if not (500_000 < info["size"] < 25_000_000):
                    continue
                if not (5 < dur < 120):
                    continue

                ext = ".webm" if "webm" in info["mime"] else ".mp4"
                safe_name = title.replace("File:", "").replace(" ", "_")[:50] + ext
                out_path = os.path.join(dest_dir, safe_name)

                print(f"  Downloading: {title[:55]} ({size_mb:.1f}MB, {dur:.0f}s)")
                if download_video(info["url"], out_path):
                    dest_clips.append({"title": title, "path": out_path, "duration": dur})
                    total_new += 1
                    print(f"  OK: {safe_name}")
                    if len([c for c in dest_clips if os.path.exists(c["path"])]) >= 3:
                        break

        index[dest] = dest_clips

        # Save index after each destination
        with open(INDEX_FILE, "w") as f:
            json.dump(index, f, indent=2)

    print(f"\nDone! Downloaded {total_new} new clips.")
    print(f"Library index: {INDEX_FILE}")
    return index


if __name__ == "__main__":
    build_library()

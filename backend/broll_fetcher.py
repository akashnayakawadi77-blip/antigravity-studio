import os
import requests
import urllib.parse

WIKIMEDIA_API  = "https://commons.wikimedia.org/w/api.php"
USER_AGENT     = "TravelingPanda/1.0 (youtube travel channel; educational)"

# Destination-specific Wikimedia search queries
DESTINATION_QUERIES = {
    "goa":        ["Goa beach India", "Goa travel", "Goa sea India"],
    "kerala":     ["Kerala backwaters India", "Kerala nature", "Munnar tea garden"],
    "leh":        ["Ladakh mountains", "Leh India landscape", "Himalayas India"],
    "ladakh":     ["Ladakh India", "Himalayan valley India", "Nubra valley"],
    "jaipur":     ["Jaipur Rajasthan India", "Hawa Mahal India", "Rajasthan palace"],
    "rajasthan":  ["Rajasthan India desert", "Rajasthan palace India"],
    "kashmir":    ["Kashmir India", "Dal Lake India", "Kashmir valley"],
    "mumbai":     ["Mumbai India", "Mumbai skyline", "Marine Drive Mumbai"],
    "delhi":      ["Delhi India", "Old Delhi India", "India Gate Delhi"],
    "agra":       ["Agra India", "Taj Mahal India", "Agra Fort"],
    "varanasi":   ["Varanasi India", "Ganges river India", "Varanasi ghats"],
    "munnar":     ["Munnar tea garden Kerala", "Kerala hills India"],
    "spiti":      ["Spiti Valley India", "Himachal Pradesh mountains"],
    "ooty":       ["Ooty Tamil Nadu India", "Nilgiris India"],
    "andaman":    ["Andaman Islands India beach", "Andaman sea India"],
    "shimla":     ["Shimla India", "Himachal Pradesh India snow"],
    "udaipur":    ["Udaipur Rajasthan", "Lake Pichola India"],
    "rishikesh":  ["Rishikesh India Ganges", "Rishikesh river India"],
    "mysuru":     ["Mysore India", "Mysore Palace India"],
    "hampi":      ["Hampi India ruins", "Hampi Karnataka India"],
}

# Generic travel fallback queries
GENERIC_QUERIES = ["India travel scenic", "India nature landscape", "India tourism",
                   "Indian culture travel", "India aerial view"]


def _get_queries(destination: str) -> list:
    dest_lower = destination.lower()
    for key, queries in DESTINATION_QUERIES.items():
        if key in dest_lower:
            return queries + GENERIC_QUERIES
    return [f"{destination} India travel", f"{destination} landscape"] + GENERIC_QUERIES


def _search_wikimedia_videos(query: str, limit: int = 5) -> list:
    """Search Wikimedia Commons for videos matching a query. Returns list of file info dicts."""
    try:
        # Step 1: Search for file titles
        resp = requests.get(WIKIMEDIA_API, params={
            'action': 'query', 'list': 'search',
            'srsearch': f'filetype:video {query}',
            'srnamespace': 6,
            'srlimit': limit,
            'format': 'json'
        }, timeout=15, headers={'User-Agent': USER_AGENT})

        if resp.status_code != 200:
            return []

        results = resp.json().get('query', {}).get('search', [])
        if not results:
            return []

        # Step 2: Get actual download URLs for each result
        titles = '|'.join(r['title'] for r in results)
        fi_resp = requests.get(WIKIMEDIA_API, params={
            'action': 'query', 'titles': titles,
            'prop': 'videoinfo', 'viprop': 'url|size|mime|duration',
            'format': 'json'
        }, timeout=15, headers={'User-Agent': USER_AGENT})

        pages = fi_resp.json().get('query', {}).get('pages', {})
        videos = []
        for pid, page in pages.items():
            vi_list = page.get('videoinfo', [])
            if not vi_list:
                continue
            vi = vi_list[0]
            url  = vi.get('url', '')
            mime = vi.get('mime', '')
            size = vi.get('size', 0)
            dur  = vi.get('duration', 0)
            # Filter: must be video, reasonable size (500KB–30MB), min 3 seconds
            if url and 'video' in mime and 500_000 < size < 30_000_000 and dur > 3:
                videos.append({
                    'title': page.get('title', ''),
                    'url': url,
                    'size': size,
                    'duration': dur,
                    'mime': mime
                })
        # Sort smallest first for fastest/most reliable downloads
        videos.sort(key=lambda x: x['size'])
        return videos

    except Exception as e:
        print(f"    Wikimedia search error for '{query}': {e}")
        return []


def _download_file(url: str, out_path: str) -> bool:
    """Download a file from URL to out_path. Returns True on success. Retries 3x."""
    for attempt in range(3):
        try:
            r = requests.get(url, timeout=(10, 90), stream=True,
                             headers={'User-Agent': USER_AGENT})
            if r.status_code != 200:
                return False
            with open(out_path, 'wb') as f:
                downloaded = 0
                for chunk in r.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
            if os.path.exists(out_path) and os.path.getsize(out_path) > 100_000:
                return True
            if os.path.exists(out_path):
                os.remove(out_path)
        except Exception as e:
            print(f"    Download attempt {attempt+1} failed: {e}")
            if os.path.exists(out_path):
                try: os.remove(out_path)
                except: pass
    return False


def fetch_broll_clips(destination: str, num_clips: int = 5,
                      output_dir: str = "outputs/broll") -> list:
    """
    Fetches B-roll video clips using the best available source:
    1. Kling AI / Runway ML (if credits available) — AI-generated cinematic video
    2. Wikimedia Commons (free, always available)
    Returns list of local downloaded .webm/.mp4 file paths.
    """
    os.makedirs(output_dir, exist_ok=True)
    downloaded = []

    # ── Priority 1: AI-Generated B-Roll (Kling / Runway) ──────────────────
    try:
        from backend.ai_video_service import generate_broll_smart
        ai_prompts = [
            f"Cinematic aerial drone shot of {destination} India, golden hour, travel video, 4K",
            f"Beautiful scenic landscape of {destination} India, nature, wide shot, cinematic",
            f"Street life and culture in {destination} India, vibrant colors, travel documentary",
        ]
        for i, prompt in enumerate(ai_prompts[:num_clips]):
            ai_path = os.path.join(output_dir, f"ai_broll_{i:02d}.mp4")
            result = generate_broll_smart(prompt, ai_path, duration=5)
            if result:
                downloaded.append(result)
        if downloaded:
            print(f"  AI video: {len(downloaded)} clip(s) generated for {destination}")
            return downloaded
    except Exception as e:
        print(f"  AI video service unavailable: {e}")

    queries = _get_queries(destination)

    print(f"[B-ROLL] Fetching clips for '{destination}' from Wikimedia Commons (free)...")

    for query in queries:
        if len(downloaded) >= num_clips:
            break

        videos = _search_wikimedia_videos(query, limit=5)
        for vid in videos:
            if len(downloaded) >= num_clips:
                break

            ext = '.webm' if 'webm' in vid['mime'] else '.mp4'
            out_path = os.path.join(output_dir, f"broll_{len(downloaded):02d}{ext}")
            short_title = vid['title'].replace('File:', '')[:50]
            size_mb = round(vid['size'] / 1024 / 1024, 1)
            dur_s   = round(vid['duration'], 1)
            print(f"    Downloading: {short_title} ({size_mb} MB, {dur_s}s)")

            if _download_file(vid['url'], out_path):
                downloaded.append(out_path)
                print(f"    OK: {out_path}")
            else:
                print(f"    Failed. Trying next...")

    # Supplement with Pexels if key available and need more clips
    pexels_key = os.environ.get("PEXELS_API_KEY", "")
    if pexels_key and len(downloaded) < num_clips:
        print(f"[B-ROLL] Supplementing with Pexels clips...")
        headers = {"Authorization": pexels_key}
        for query in queries:
            if len(downloaded) >= num_clips:
                break
            try:
                resp = requests.get(
                    f"https://api.pexels.com/videos/search",
                    params={"query": query, "per_page": 1, "orientation": "landscape"},
                    headers=headers, timeout=15
                )
                videos = resp.json().get("videos", [])
                if videos:
                    files = videos[0].get("video_files", [])
                    best = next((v for v in files if v.get("quality") == "hd"), files[0] if files else None)
                    if best:
                        out_path = os.path.join(output_dir, f"pexels_{len(downloaded):02d}.mp4")
                        if _download_file(best["link"], out_path):
                            downloaded.append(out_path)
                            print(f"    Pexels clip saved: {out_path}")
            except Exception as e:
                print(f"    Pexels error: {e}")

    if not downloaded:
        print("[B-ROLL] No clips downloaded -- using animated gradient backgrounds.")
    else:
        print(f"[B-ROLL] Ready: {len(downloaded)} clip(s) downloaded.")

    return downloaded

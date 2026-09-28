"""
AI Video Generation Service
Integrates Runway ML and Kling AI for generating cinematic B-roll from text prompts.
Automatically activates when credits are available, falls back to free sources otherwise.
"""
import os
import time
import requests

# ── Runway ML ─────────────────────────────────────────────────────────────────
RUNWAY_BASE = "https://api.dev.runwayml.com/v1"

def _runway_headers():
    key = os.environ.get("RUNWAY_API_KEY", "")
    return {
        "Authorization": f"Bearer {key}",
        "X-Runway-Version": "2024-11-06",
        "Content-Type": "application/json"
    }

def runway_has_credits() -> bool:
    """Check if Runway account has credits available."""
    try:
        r = requests.get(f"{RUNWAY_BASE}/organization",
                         headers=_runway_headers(), timeout=10)
        if r.status_code == 200:
            balance = r.json().get("creditBalance", 0)
            return balance > 0
    except Exception:
        pass
    return False

def generate_broll_runway(prompt: str, output_path: str,
                          duration: int = 5) -> str | None:
    """
    Generate a cinematic B-roll video clip using Runway ML Gen-4 Turbo.
    Returns local file path on success, None on failure.
    """
    if not os.environ.get("RUNWAY_API_KEY"):
        return None
    if not runway_has_credits():
        print("  [Runway] No credits available. Skipping.")
        return None

    try:
        print(f"  [Runway Gen-4] Generating: {prompt[:60]}...")
        payload = {
            "model": "gen4_turbo",
            "promptText": prompt,
            "duration": duration,
            "ratio": "1280:720",
        }
        r = requests.post(f"{RUNWAY_BASE}/image_to_video",
                          headers=_runway_headers(),
                          json=payload, timeout=30)
        data = r.json()

        if r.status_code not in (200, 201) or "id" not in data:
            print(f"  [Runway] Error: {data}")
            return None

        task_id = data["id"]
        print(f"  [Runway] Task started: {task_id}")

        # Poll for completion (max 3 minutes)
        for attempt in range(36):
            time.sleep(5)
            r2 = requests.get(f"{RUNWAY_BASE}/tasks/{task_id}",
                              headers=_runway_headers(), timeout=15)
            task = r2.json()
            status = task.get("status", "")
            print(f"  [Runway] Status: {status} ({attempt*5}s)")

            if status == "SUCCEEDED":
                video_url = task.get("output", [None])[0]
                if video_url:
                    return _download_video(video_url, output_path)
                break
            elif status in ("FAILED", "CANCELLED"):
                print(f"  [Runway] Failed: {task.get('failure', '')}")
                break

    except Exception as e:
        print(f"  [Runway] Exception: {e}")
    return None


# ── Kling AI ──────────────────────────────────────────────────────────────────
KLING_BASE = "https://api.klingai.com/v1"

def _kling_headers():
    key = os.environ.get("KLING_API_KEY", "")
    return {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }

def kling_has_balance() -> bool:
    """Check if Kling account has balance by trying a minimal request."""
    try:
        r = requests.get(f"{KLING_BASE}/videos/text2video",
                         headers=_kling_headers(), timeout=10)
        if r.status_code == 200:
            # code 1102 = insufficient balance
            return r.json().get("code", 0) != 1102
    except Exception:
        pass
    return False

def generate_broll_kling(prompt: str, output_path: str,
                         duration: int = 5) -> str | None:
    """
    Generate a cinematic B-roll video clip using Kling AI.
    Returns local file path on success, None on failure.
    """
    if not os.environ.get("KLING_API_KEY"):
        return None

    try:
        print(f"  [Kling AI] Generating: {prompt[:60]}...")
        payload = {
            "model_name": "kling-v1",
            "prompt": prompt,
            "negative_prompt": "blurry, low quality, text, watermark, logo",
            "cfg_scale": 0.5,
            "mode": "std",
            "duration": str(duration)
        }
        r = requests.post(f"{KLING_BASE}/videos/text2video",
                          headers=_kling_headers(),
                          json=payload, timeout=30)
        data = r.json()

        if data.get("code") == 1102:
            print("  [Kling] Insufficient balance. Skipping.")
            return None
        if data.get("code") != 0:
            print(f"  [Kling] Error: {data.get('message')}")
            return None

        task_id = data["data"]["task_id"]
        print(f"  [Kling] Task started: {task_id}")

        # Poll for completion (max 3 minutes)
        for attempt in range(36):
            time.sleep(5)
            r2 = requests.get(f"{KLING_BASE}/videos/text2video/{task_id}",
                              headers=_kling_headers(), timeout=15)
            task = r2.json().get("data", {})
            status = task.get("task_status", "")
            print(f"  [Kling] Status: {status} ({attempt*5}s)")

            if status == "succeed":
                videos = task.get("task_result", {}).get("videos", [])
                if videos:
                    video_url = videos[0].get("url", "")
                    if video_url:
                        return _download_video(video_url, output_path)
                break
            elif status in ("failed", "cancelled"):
                print(f"  [Kling] Failed.")
                break

    except Exception as e:
        print(f"  [Kling] Exception: {e}")
    return None


# ── Shared Helper ─────────────────────────────────────────────────────────────
def _download_video(url: str, out_path: str) -> str | None:
    """Download a video from URL to local path."""
    try:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        r = requests.get(url, timeout=120, stream=True)
        if r.status_code == 200:
            with open(out_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=131072):
                    if chunk:
                        f.write(chunk)
            if os.path.getsize(out_path) > 50000:
                print(f"  Downloaded: {out_path}")
                return out_path
    except Exception as e:
        print(f"  Download error: {e}")
    return None


# ── Smart Generator: Try AI first, then free sources ─────────────────────────
def generate_broll_smart(prompt: str, output_path: str,
                         duration: int = 5) -> str | None:
    """
    Try AI video generation in priority order:
    1. Kling AI (if balance available)
    2. Runway ML (if credits available)
    3. Return None → caller uses free Wikimedia/gradient fallback
    """
    # Try Kling first (usually cheaper per second)
    result = generate_broll_kling(prompt, output_path, duration)
    if result:
        return result

    # Try Runway as backup
    result = generate_broll_runway(prompt, output_path, duration)
    if result:
        return result

    return None

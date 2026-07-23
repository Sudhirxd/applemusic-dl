import re
import json
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, request, jsonify

import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# --- Developer Credits ---
DEV_CREDITS = {
    "name": "Sudhirxd",
    "website": "https://www.sudhirxd.in",
    "github": "https://www.github.com/Sudhirxd",
    "telegram": "https://t.me/Sudhirxd",
    "instagram": "https://www.instagram.com/sudhirxd.in"
}

# --- Apple Music Scraper Engine ---
APL_BASE = "https://aplmate.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": APL_BASE,
    "Referer": f"{APL_BASE}/",
    "X-Requested-With": "XMLHttpRequest",
}

APPLE_RE = re.compile(
    r"https?://music\.apple\.com/[a-z]{2}/(album|playlist|song)/[^\s]+"
)


def create_apple_session() -> requests.Session:
    s = requests.Session()
    s.headers.update(HEADERS)
    s.get(f"{APL_BASE}/", timeout=15)
    return s


def get_apple_token(session: requests.Session, apple_url: str) -> str:
    r = session.post(
        f"{APL_BASE}/action/userverify",
        data={"url": apple_url},
        timeout=20
    )
    r.raise_for_status()
    try:
        resp = r.json()
    except ValueError:
        raise RuntimeError("Invalid response from verification server.")
        
    token = resp.get("token")
    if not resp.get("success") or not token:
        raise RuntimeError(resp.get("message", "User verification failed on aplmate.com."))
        
    return token


def get_apple_track_forms(session: requests.Session, apple_url: str, token: str):
    r = session.post(
        f"{APL_BASE}/action",
        data={"url": apple_url, "cf-turnstile-response": token},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=25
    )
    r.raise_for_status()
    try:
        resp = r.json()
    except ValueError:
        raise RuntimeError("Invalid response format from action endpoint.")

    if resp.get("error"):
        raise RuntimeError(resp.get("message", "Failed to fetch Apple Music track data."))

    html = resp.get("data", "") or resp.get("html", "")
    soup = BeautifulSoup(html, "html.parser")
    forms = soup.find_all("form", {"name": "submitapurl"})

    results = []
    for form in forms:
        fields = {}
        for inp in form.find_all("input"):
            if inp.get("name"):
                fields[inp["name"]] = inp.get("value", "")
        results.append(fields)

    fallback_thumb = None
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if "mzstatic.com" in src or "mzcdn.com" in src:
            fallback_thumb = src
            break

    return results, fallback_thumb


def resolve_apple_track(session: requests.Session, form_data: dict, index: int, fallback_thumb: str | None = None) -> dict:
    try:
        info = json.loads(base64.b64decode(form_data.get("data", "")).decode())
        title = info.get("name", f"Track {index + 1}")
        artist = info.get("artist", "")
        name = f"{title} - {artist}" if artist else title
        thumb_url = info.get("cover") or info.get("image") or fallback_thumb
    except Exception:
        title, artist, name, thumb_url = f"Track {index + 1}", "", f"Track {index + 1}", fallback_thumb

    try:
        r = session.post(f"{APL_BASE}/action/track", data=form_data, timeout=30)
        r.raise_for_status()
        resp = r.json()
    except Exception as e:
        return {
            "index": index,
            "name": name,
            "title": title,
            "artist": artist,
            "thumb_url": thumb_url,
            "download_url": None,
            "error": f"Failed to fetch action track: {e}"
        }

    if resp.get("error"):
        return {
            "index": index,
            "name": name,
            "title": title,
            "artist": artist,
            "thumb_url": thumb_url,
            "download_url": None,
            "error": resp.get("message", "API returned error")
        }

    track_html = resp.get("data", "") or resp.get("html", "")
    soup = BeautifulSoup(track_html, "html.parser")

    img = soup.find("img")
    if img and not thumb_url:
        thumb_url = img.get("src")

    href = None
    for a in soup.find_all("a", href=re.compile(r"cdndl\.aplmate\.com|/mp3\?token=")):
        href = a["href"]
        if href.startswith("/"):
            href = APL_BASE + href
        break

    if not href:
        for a in soup.find_all("a", href=re.compile(r"https?://")):
            if "ko-fi" not in a["href"] and "buymeacoffee" not in a["href"]:
                href = a["href"]
                break

    return {
        "index": index,
        "name": name,
        "title": title,
        "artist": artist,
        "thumb_url": thumb_url,
        "download_url": href,
        "error": None if href else "No direct download link found"
    }


def extract_apple_data(url: str, max_workers: int = 5) -> dict:
    session = create_apple_session()
    token = get_apple_token(session, url)
    forms, fallback_thumb = get_apple_track_forms(session, url, token)

    if not forms:
        raise RuntimeError("No tracks found at the provided Apple Music URL.")

    total_tracks = len(forms)
    resolved_tracks = [None] * total_tracks

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(resolve_apple_track, session, form, i, fallback_thumb): i
            for i, form in enumerate(forms)
        }
        for future in as_completed(futures):
            res = future.result()
            resolved_tracks[res["index"]] = res

    return {
        "success": True,
        "developer": DEV_CREDITS,
        "total_tracks": total_tracks,
        "tracks": resolved_tracks
    }


# --- Flask Pure JSON Routes ---

@app.route("/", methods=["GET"])
@app.route("/api/download", methods=["GET", "POST"])
def apple_api():
    headers = {"Access-Control-Allow-Origin": "*"}

    if request.path == "/" and not request.args.get("url"):
        return jsonify({
            "status": "online",
            "service": "Apple Music Downloader JSON API",
            "developer": DEV_CREDITS,
            "usage": {
                "download_endpoint": "/api/download",
                "example_query": "/api/download?url=YOUR_APPLE_MUSIC_URL"
            }
        }), 200, headers

    apple_url = None
    if request.method == "GET":
        apple_url = request.args.get("url")
    elif request.method == "POST":
        data = request.get_json(silent=True) or {}
        apple_url = data.get("url") or request.form.get("url")

    if not apple_url:
        return jsonify({
            "success": False,
            "developer": DEV_CREDITS,
            "error": "Missing required parameter 'url'."
        }), 400, headers

    apple_url = apple_url.strip()
    if not APPLE_RE.search(apple_url):
        return jsonify({
            "success": False,
            "developer": DEV_CREDITS,
            "error": "Invalid Apple Music URL. Must be a valid song, album, or playlist link."
        }), 400, headers

    try:
        data = extract_apple_data(apple_url)
        return jsonify(data), 200, headers
    except Exception as e:
        return jsonify({
            "success": False,
            "developer": DEV_CREDITS,
            "error": str(e)
        }), 500, headers


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

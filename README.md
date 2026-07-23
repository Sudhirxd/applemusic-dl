#  Apple Music Downloader JSON API 

A lightweight, high-performance Apple Music link extractor written in Python. Ships as a **Vercel-Friendly Pure JSON API** that returns direct extracted download links.

---

## 🚀 Features of this Api Endpoint

- **Pure JSON API (No UI)**: 100% JSON endpoints returning direct extracted MP3 download links.
- **Ultra-Fast Speed**: Average response time of **3~4 sec** for link extraction.
- **Vercel Serverless Ready**: Deploy to Vercel instantly with `vercel.json` pre-configured.
- **Developer Credits**: Includes developer credits metadata (**Sudhirxd**).
- **REST API Endpoints**:
  - `GET /` -> API Status & Documentation in JSON
  - `GET /api/download?url=...` -> Extracts Apple Music download links in JSON
  - `POST /api/download` -> Accepts JSON `{"url": "..."}`

---

## 📦 Installation & Local Testing

- Python 3.8+
- Dependencies: `requests`, `beautifulsoup4`, `flask`

Install dependencies:
```bash
pip install -r requirements.txt
```

Run locally:
```bash
python api/index.py
```

---

## 🌐 Deploying to Vercel

This repository is pre-configured for Vercel deployment with `vercel.json` and `api/index.py`.
---

## 🔌 API Usage

### 1. API Status (GET /)
```http
GET /
```

### 2. Extract Download Links (GET)
```http
GET /api/download?url=https://music.apple.com/us/album/1989-taylors-version/1708308989
```

### 3. Extract Download Links (POST)
```http
POST /api/download
Content-Type: application/json

{
  "url": "https://music.apple.com/us/album/1989-taylors-version/1708308989"
}
```

### Sample JSON Response
```json
{
  "success": true,
  "developer": {
    "name": "Sudhirxd",
    "website": "https://www.sudhirxd.in",
    "github": "https://www.github.com/Sudhirxd",
    "telegram": "https://t.me/Sudhirxd",
    "instagram": "https://www.instagram.com/sudhirxd.in"
  },
  "total_tracks": 21,
  "tracks": [
    {
      "name": "Welcome To New York (Taylor's Version) - Taylor Swift",
      "title": "Welcome To New York (Taylor's Version)",
      "artist": "Taylor Swift",
      "thumb_url": "https://is1-ssl.mzstatic.com/image/thumb/...",
      "download_url": "https://cdndl.aplmate.com/mp3?token=...",
      "error": null
    }
  ]
}
```

---

## 👨‍💻 Developer & Credits

- **Developer**: **Sudhirxd**
- **Website**: [https://www.sudhirxd.in](https://www.sudhirxd.in)
- **GitHub**: [https://www.github.com/Sudhirxd](https://www.github.com/Sudhirxd)
- **Telegram**: [@Sudhirxd](https://t.me/Sudhirxd)
- **Instagram**: [@sudhirxd.in](https://www.instagram.com/sudhirxd.in)

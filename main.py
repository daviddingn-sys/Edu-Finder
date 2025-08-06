# main.py —— Flask on Vercel

from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.environ.get("SEARCH_ENGINE_ID")

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "message": "Edu Finder is running."})

@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify({"error": "Missing 'query' parameter"}), 400

    if not GOOGLE_API_KEY or not SEARCH_ENGINE_ID:
        return jsonify({"error": "Missing GOOGLE_API_KEY or SEARCH_ENGINE_ID in environment."}), 500

    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": GOOGLE_API_KEY, "cx": SEARCH_ENGINE_ID, "q": query}

    try:
        resp = requests.get(url, params=params, timeout=10)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request to Google failed: {str(e)}"}), 502

    if resp.status_code != 200:
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        return jsonify({"error": "Google API error", "status_code": resp.status_code, "detail": detail}), 502

    data = resp.json()
    items = data.get("items", []) or []
    results = [{"title": it.get("title"), "link": it.get("link"), "snippet": it.get("snippet")} for it in items]

    return jsonify({"query": query, "count": len(results), "results": results})
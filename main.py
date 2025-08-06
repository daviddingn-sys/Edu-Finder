# main.py  —— Flask on Vercel

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
    # 1) 校验 query
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify({"error": "Missing 'query' parameter"}), 400

    # 2) 校验环境变量
    if not GOOGLE_API_KEY or not SEARCH_ENGINE_ID:
        return jsonify({
            "error": "Missing GOOGLE_API_KEY or SEARCH_ENGINE_ID in environment."
        }), 500

    # 3) 调用 Google Custom Search API
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "q": query,
    }

    try:
        # 给一个超时，避免函数卡住
        resp = requests.get(url, params=params, timeout=10)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request to Google failed: {str(e)}"}), 502

    if resp.status_code != 200:
        # 尽量把 Google 的错误信息透传回来，方便排查
        try:
            err = resp.json()
        except Exception:
            err = resp.text
        return jsonify({"error": "Google API error", "status_code": resp.status_code, "detail": err}), 502

    data = resp.json()
    items = data.get("items", []) or []

    # 4) 统一精简后的结果
    results = [
        {
            "title": it.get("title"),
            "link": it.get("link"),
            "snippet": it.get("snippet"),
        }
        for it in items
    ]

    return jsonify({
        "query": query,
        "count": len(results),
        "results": results
    })
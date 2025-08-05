from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import json
import os

app = Flask(__name__)
SCRAPERAPI_KEY = "your_scraperapi_key_here"
HISTORY_FILE = "search_history.json"

# 加载历史记录
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        seen_links = json.load(f)
else:
    seen_links = {}

def save_history():
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(seen_links, f, ensure_ascii=False, indent=2)

def fetch_google_results(query, country):
    google_search_url = f"https://www.google.com/search?q={query}&hl=en"
    scraper_url = f"http://api.scraperapi.com/?api_key={SCRAPERAPI_KEY}&url={google_search_url}&render=true"
    response = requests.get(scraper_url)

    if response.status_code != 200:
        return {"error": f"ScraperAPI failed: {response.status_code}", "details": response.text}

    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    if country not in seen_links:
        seen_links[country] = []

    for result_block in soup.find_all("div", class_="tF2Cxc"):
        if len(results) >= 50:
            break
        title_tag = result_block.find("h3")
        link_tag = result_block.find("a")
        snippet_tag = result_block.find("div", class_="VwiC3b")

        if title_tag and link_tag:
            link = link_tag["href"].strip()
            if link in seen_links[country]:
                continue
            seen_links[country].append(link)
            results.append({
                "title": title_tag.text.strip(),
                "link": link,
                "snippet": snippet_tag.text.strip() if snippet_tag else ""
            })

    save_history()
    return results

@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query", "")
    country = request.args.get("country", "")
    if not query and not country:
        return jsonify({"error": "Missing 'query' or 'country' parameter"}), 400

    if not query:
        query = f"Chinese language school in {country}"

    results = fetch_google_results(query, country or query)
    return jsonify({
        "query": query,
        "country": country,
        "results": results if isinstance(results, list) else [],
        "status": "success" if isinstance(results, list) else "error",
        "debug": results if isinstance(results, dict) else None
    })

if __name__ == "__main__":
    app.run(debug=True, port=5055)

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os
import requests

app = FastAPI()

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.environ.get("SEARCH_ENGINE_ID")

@app.get("/")
async def root():
    return {"message": "Welcome to the Edu Finder Plugin!"}

@app.get("/search")
async def search(query: str):
    if not GOOGLE_API_KEY or not SEARCH_ENGINE_ID:
        return JSONResponse(status_code=500, content={"error": "Missing API key or Search Engine ID"})

    url = (
        f"https://www.googleapis.com/customsearch/v1"
        f"?key={AIzaSyCRq0dc3AoCmdIasQKCxEATkDttdYs1VDY}&cx={a35a28d6dd49f410b}&q={query}"
    )

    response = requests.get(url)
    if response.status_code != 200:
        return JSONResponse(status_code=500, content={"error": "Google API request failed"})

    results = response.json().get("items", [])
    simplified = [{"title": item["title"], "link": item["link"]} for item in results]

    return {"results": simplified}
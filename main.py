import os
import requests

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.environ.get("SEARCH_ENGINE_ID")

def handler(request):
    try:
        # 获取 query 参数
        query = request.args.get("query", "")
        if not query:
            return {
                "statusCode": 400,
                "body": "Missing 'query' parameter"
            }

        # 调用 Google Search API
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": GOOGLE_API_KEY,
            "cx": SEARCH_ENGINE_ID,
            "q": query
        }
        response = requests.get(url, params=params)

        return {
            "statusCode": 200,
            "body": response.text
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error: {str(e)}"
        }
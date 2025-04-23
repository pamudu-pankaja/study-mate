from googleapiclient.discovery import build
from app.config.config import WEB_SEARCH_API_KEY,WEB_SEARC_ID

service = build("customsearch","v1",developerKey=WEB_SEARCH_API_KEY)

def web_search(query):
    try:
        response = service.cse().list(q=query , cx=WEB_SEARC_ID , num=5).execute()
    except Exception as e:
        return f"Erro : {e}"
    
    result = []
    for item in response.get('items',[]):
        title = item.get("title","")
        url = item.get("link","")
        snippet = item.get("snippet","")
        if snippet : 
            result.append(
                {
                    "title":title,
                    "url":url,
                    "snippet":snippet
                }
            )
    return result
    
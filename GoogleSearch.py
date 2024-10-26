from googleapiclient.discovery import build
from dotenv import load_dotenv
import os


class GoogleSearch:
    def __init__(self) -> None:
        load_dotenv()
        
        self.api_key = os.environ["GOOGLE_SEARCH_API"]
        self.search_engine_id = os.environ["SEARCH_ENGINE_ID"]
        
    def search(self, query: str, n:int=5) -> list:
        service = build('customsearch', 'v1', developerKey=self.api_key)
        result = service.cse().list(q=query, cx=self.search_engine_id, num=n).execute()
        result = result.get('items', [])
        
        return [link['link'] for link in result]
    

if __name__ == "__main__":
    search_engine = GoogleSearch()
    links = search_engine.search(query="唐揚げ 作り方 簡単")
    print(links)
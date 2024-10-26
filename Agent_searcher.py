from Agent import *
from Knowledge import *
from Chatbot_manager import *
from GoogleSearch import GoogleSearch

from dotenv import load_dotenv
from googleapiclient.discovery import build
from readability import Document
import requests
from bs4 import BeautifulSoup
import concurrent.futures
import os, time, random, datetime
from typing import List
from googlesearch import search


Searcher_system_prompt = """
- Role: 
   - Act as an advanced search word generator for search engine.

- What's given:
   - Current time: Use the current time as context.
   - Knowledge: Assumptions are the base of your response construction.
   - Prompt: The specific topic you need to search for, presented as a string.
   - Final goal: Your search results will be used to achieve the goal described in this final statement.

- Your output must be:
   - Search words: Deliver search words that meet the specifications.

- Format:
   - Only provide search words as output.
   - Do not include any other words, code blocks, or JSON format.

- Language:
   - Use the same language as the given prompt unless directed otherwise.

- Response Generation Procedure:
   1. Analyze the prompt thoroughly; refine it using the provided knowledge to be as precise as possible.
   2. Develop search words derived from the refined prompt.

- Specifications:
   - Devise a procedure to fulfill the task described in the prompt.
   - You're permitted to obtain information via a search engine to satisfy the "prompt" and "final goal."
   - Choose search words to obtain information that meets the prompt and final goal.
   - Consider what the user wants to achieve and the desired outcome based on Final goal when selecting search words.
   - You may modify or use synonyms for words in the prompt if it improves search results.
   - Aim for a minimal number of search words. The maximum number of words should be no more than five.

- Limitations:
   - Strictly adhere to the "specifications" when formulating the thought process and policy.
   - Do not output any strings except those in the specified output format.
   - Only provide results in the designated format without deviation.

"""


class Search_request:
    def __init__(self, query: str, final_goal: str, knowledge: Knowledge=None, use_knowledge: bool | list=True) -> None:
        self.query = query
        self.final_goal = final_goal
        self.knowledge = knowledge
        
        if use_knowledge == True:
            if self.knowledge is None:
                # do not use knowledge at all
                self.use_knowledge = []
            else:
                # use all knowledge
                self.use_knowledge = list(range(len(self.knowledge.memories)))
            
        elif use_knowledge == False or use_knowledge is None:
            # do not use knowledge at all
            self.use_knowledge = []
        else:
            # use selected knowledge
            self.use_knowledge = use_knowledge
         

class Search_response:
    def __init__(self, link: str, title: str, content: str) -> None:
        self.link = link
        self.title = title
        self.content = content
        
    def __str__(self) -> str:
        return f"title:  {self.title}\nlink:   {self.link}\ncontent: {self.content[:30]}"
    
    
class Searcher(Agent):
    def __init__(self) -> None:
        load_dotenv()
        self.api_key = os.environ.get("GOOGLE_SEARCH_API")
        self.search_engine_id = os.environ.get("SEARCH_ENGINE_ID")
        
        self.name = Agent_role.Searcher
        self.description = "Search engine"
        self.system_prompt = Searcher_system_prompt
        
        # self.model = model
        
        super().__init__(self.name, self.description, self.system_prompt)
    
    def search_words_generator(self, model:LLM, request: Search_request) -> str:
        ai = Chatbot_manager(system_prompt=Searcher_system_prompt)
        
        if len(request.use_knowledge) != 0:
            info = f"current time: {datetime.datetime.now().strftime('%Y/%m/%d/')}\n"
            
            info += (
                    "\n***********************************************************"
                    "\nKnowledge section:"
                    "\nUse information below to generate beneficial answer."
                    "\n***********************************************************\n"
                )
            
            for index in request.use_knowledge:
                info +=  f"{index}. {request.knowledge.summaries[index]}\n"
                
            info += (
                    "\n***********************************************************"
                    "\nFinal goal section:"
                    "\nWhat output you generate will ultimately be used to answer the question?"
                    "\n***********************************************************\n"
                )
            info += request.final_goal + "\n"
                    
            info += (
                    "\n***********************************************************"
                    "\nPrompt section:"
                    "\nBelow is a request from user. Your answer must follow the prompt."
                    "\n***********************************************************\n"
                )
            info += request.query + "\n"
            
            result = ai.invoke(model=model, query=Chat_request(prompt=info))
            
            return result.text
        
        else:
            result = ai.invoke(model=model, query=Chat_request(prompt=f"current time: {datetime.datetime.now().strftime('%Y/%m/%d/')}\n\nprompt: {request.query}"))
            
            return result.text
    
    def content_parser(self, url: str) -> Search_response:
        import time
        
        try:
            start = time.time()
            response = requests.get(url, timeout=1)
            end = time.time()
            # print(end-start, response.status_code)
            
            if response.status_code == 200:
                doc = Document(response.content)

                soup = BeautifulSoup(doc.summary(), 'html.parser')
                content = soup.get_text().strip()
                
                response = Search_response(link=url, title=doc.title(), content=content)
                
                return response

            else:
                return Search_response(link="", title="", content="")
        except:
            return Search_response(link="", title="", content="")
    
    def invoke(self, model:LLM, request: Search_request, n: int=5) -> list[Search_response]:
        
        search_word = self.search_words_generator(model=model, request=request)
        
        search_engine = GoogleSearch()
        urls = search_engine.search(query=search_word, n=n)
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            responses = list(executor.map(self.content_parser, urls))
        
        return responses
    
    def print_search_responses(self, responses: list[Search_response]) -> None:
        file_name = f"{random.randint(1000, 9999)}.txt"
    
        for i, response in enumerate(responses, 1):
                print(f"Result {i}:\n{response}\n\n")


if __name__ == "__main__":
    from RAG_manager import *
    
    searcher = Searcher()
    rag = RAG_manager()
    
    query = "戦後最も任期が長かった日本の首相は誰？"
    
    search_word = searcher.search_words_generator(model=LLM.gpt_4o_mini, request=Search_request(query=query, final_goal=query))
        
    search_engine = GoogleSearch()
    urls = search_engine.search(query=search_word, n=5)
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        responses = list(executor.map(searcher.content_parser, urls))
        
    for content in responses:
        print("#######################################################################")
        compressed_content = rag.search(query=query, doc=content.content, n=100)
        
        for text in compressed_content:
            print("--------------------------------------------------------")
            print(text)
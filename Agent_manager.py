from Chatbot_manager import *
from Agent_planner import *
from Agent_searcher import *
from Agent_LangModel import *
from Knowledge import *

from typing import List
from multiprocessing import Process, Manager

summarizer_system_prompt = """
- Role: 
   - You are an excellent writer.

- What's given:
   - prompt: what the user wants to know
   - knowledge: Sources you must use when generating your response

- Your output must be:
   - Summary: You must output a short answer to "prompt". This must be short summary of "knowledge.

- Format:
   - markdown format
   - Structure the response for readability and user engagement, presenting information clearly and methodically.
   - Avoid long paragraphs. Use lists, tables, and subheader to keep the structure concise and easy to read.

- Language:
   - Use the same language as the given prompt unless directed otherwise.
"""

class Agent_manager:
    class stream_response:
        def __init__(self, task: Task, role: str, text: str) -> None:
            self.task = task
            self.role = role
            self.text = text
    
    def __init__(self, planner_model: LLM = LLM.gpt_4o_mini, searcher_model: LLM=LLM.gpt_4o_mini, summarizer_model: LLM=LLM.gpt_4o_mini, lang_model: LLM=LLM.gpt_4o_mini, answer_model: LLM=LLM.gpt_4o_mini) -> None:
        self.planner = Planner()
        self.searcher = Searcher()
        self.llm = LangModel()
        self.knowledge = Knowledge(capacity=100)
        
        self.planner_model = planner_model
        self.searcher_model = searcher_model
        self.summarizer_model = summarizer_model
        self.lang_model = lang_model
        self.answer_model = answer_model
        
        self.response = None
    
    def planner_memory_update(self, memory: list):
        self.planner.import_memory(memory=memory)
        
    def langmodel_memory_update(self, memory: list):
        self.llm.import_memory(memory=memory)
        # self.llm.LangModel.print_memory()
        
    def invoke(self, model: LLM, query: Chat_request):
        tasks = self.planner.invoke(model=model, query=query)
        
        for task in tasks[:len(tasks)-1]:
            print("\n***************************************************************")
            print(f"No.{task.number} Task: {task.query}, Role: {task.agent_role}, Pre_result: {task.pre_result}")
            
            if task.agent_role == "Searcher":
                request = Search_request(query=task.query, final_goal=query.prompt, knowledge=self.knowledge, use_knowledge=task.pre_result)
                response = self.searcher.invoke(request=request)
                
                knowledge = [Knowledge.memory(title=res.title, link=res.link, content=res.content) for res in response]
                self.knowledge.add(content=knowledge, index=task.number)

                ai = Chatbot_manager(system_prompt="You are helpful assistant.")
                request = Chat_request(prompt=task.query+" \n\nPlease summarize given knowledge and answer", knowledge=self.knowledge)
                response = ai.invoke(model=model, query=request)
                self.knowledge.summarize(summary=response.text, index=task.number)
                
            elif task.agent_role == "LLM":
                ai = LangModel()
                request = Chat_request(prompt=task.query, knowledge=self.knowledge, use_knowledge=task.pre_result)
                response = ai.invoke(model=model, query=request)
                
                knowledge = [Knowledge.memory(title="", link="", content=response.text)]
                self.knowledge.add(content=knowledge, index=task.number)
                
        # Last task
        task = tasks[-1]
        print("\n***************************************************************")
        print(f"No.{task.number} Task: {task.query}, Role: {task.agent_role}, Pre_result: {task.pre_result}")
            
        request = Chat_request(prompt=task.query, knowledge=self.knowledge, use_knowledge=task.pre_result)
        response = self.llm.invoke_stream(model=model, query=request)
        
        for token in response:
            yield token
        
        self.response = self.llm.response
    
    def _searcher(self, task: Task, query: Chat_request):
        request = Search_request(query=task.query, final_goal=query.prompt, knowledge=self.knowledge, use_knowledge=task.pre_result)
        response = self.searcher.invoke(model=self.searcher_model, request=request)
        
        knowledge = [Knowledge.memory(title=res.title, link=res.link, content=res.content) for res in response]
        self.knowledge.add(content=knowledge, index=task.number)

        ai = Chatbot_manager(system_prompt=summarizer_system_prompt)
        request = Chat_request(prompt=task.query, knowledge=self.knowledge)
        response = ai.invoke_stream(model=self.summarizer_model, query=request)
        
        for token in response:
            yield self.stream_response(task=task, role="Searcher", text=token)
        
        self.knowledge.summarize(summary=ai.reply.text, index=task.number)
    
    def _LLM(self, task: Task, query: Chat_request):
        ai = LangModel()
        request = Chat_request(prompt=task.query, knowledge=self.knowledge, use_knowledge=task.pre_result)
        response = ai.invoke_stream(model=self.lang_model, query=request)
        
        for token in response:
            yield self.stream_response(task=task, role="LLM", text=token)
        
        knowledge = [Knowledge.memory(title="", link="", content=ai.reply.text)]
        self.knowledge.add(content=knowledge, index=task.number)
        
    def _answerer(self, task: Task, query: Chat_request):
        request = Chat_request(prompt=task.query, knowledge=self.knowledge, use_knowledge=task.pre_result)
        response = self.llm.invoke_stream(model=self.answer_model, query=request)
        
        for token in response:
            yield self.stream_response(task=task, role="Answerer", text=token)
        
        self.response = self.llm.reply
            
    def invoke_stream(self, query: Chat_request):
        tasks = self.planner.invoke(model=self.planner_model, query=query)
        
        for task in tasks[:len(tasks)-1]:
            if task.agent_role == "Searcher":
                response = self._searcher(task=task, query=query)
                
                for token in response:
                    yield self.stream_response(task=task, role="Searcher", text=token.text)
                
            elif task.agent_role == "LLM":
                response = self._LLM(task=task, query=query)
                
                for token in response:
                    yield self.stream_response(task=task, role="LLM", text=token.text)
                
        # Last task
        task = tasks[-1]
        response = self._answerer(task=task, query=query)
                
        for token in response:
            yield self.stream_response(task=task, role="Answerer", text=token.text)
            
            
if __name__ == "__main__":
    manager = Agent_manager()
    response = manager.invoke_stream(strong_model=LLM.gpt_4o_mini, weak_model=LLM.gpt_4o_mini, query=Chat_request(prompt="戦後日本で最も任期が長かった首相の奥様の出身大学はどこですか。"))
    
    for token in response:
        print(token.text, end="")
    
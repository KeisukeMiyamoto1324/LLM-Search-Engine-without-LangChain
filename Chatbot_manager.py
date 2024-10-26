# from Chat_Query import *
from LLM import *
from GPT import *
from Claude import *
from Genimi import *
from Chat_Query import *

from typing import List
from dotenv import load_dotenv
        

class Chatbot_manager:
    def __init__(self, system_prompt="") -> None:
        load_dotenv()
        self.memory = [Chat_request(prompt=system_prompt, role=Role.system)]
        self._total_cost = 0
        
        self.reply: Chat_response = None
        
    def print_memory(self):
        for memory in self.memory:
            print(f"role: {memory.role.value}\tprompt: {memory.prompt[:20]}")
    
    def system_prompt(self, prompt: str):
        self.memory[0] = Chat_request(prompt=prompt, role=Role.system)
        return self.memory[0]
    
    def total_cost(self):
        return self._total_cost
    
    def export_memory(self):
        return self.memory
    
    def import_memory(self, memory: list):
        self.memory = memory
        
    def invoke(self, model: LLM, query: Chat_request) -> Chat_response:
        self.memory.append(query)
        
        if model.value.company == Company.openai:
            client = ChatGPT()

        elif model.value.company == Company.anthropic:
            client = Claude()
        
        elif model.value.company == Company.google:
            client = Gemini()
        
        reply = client.invoke(model=model, querys=self.memory)
        self._total_cost += reply.total_cost
        self.memory.append(reply)
        
        return reply
    
    def invoke_stream(self, model: LLM, query: Chat_request):
        self.memory.append(query)
        
        if model.value.company == Company.openai:
            client = ChatGPT()
            
            for token in client.invoke_stream(model=model, querys=self.memory):
                yield token  
            
            self.reply = client.reply
            self._total_cost += self.reply.total_cost
            self.memory.append(self.reply)
            
        elif model.value.company == Company.anthropic:
            client = Claude()
            
            for token in client.invoke_stream(model=model, querys=self.memory):
                yield token  
            
            self.reply = client.reply
            self._total_cost += self.reply.total_cost
            self.memory.append(self.reply)
            
        elif model.value.company == Company.google:
            client = Gemini()
            
            for token in client.invoke_stream(model=model, querys=self.memory):
                yield token  
            
            self.reply = client.reply
            self._total_cost += self.reply.total_cost
            self.memory.append(self.reply)
            
    
    def streaming_print(self, stream_object) -> None:
        for token in stream_object:
            print(token, end="")
        

if __name__ == "__main__":
    ai = Chatbot_manager(system_prompt="Your name is Mike.")
    
    query = Chat_request(prompt="Tell me your history from your born to now.")
    response = ai.invoke_stream(model=LLM.gemini_1_5_flash, query=query)
    ai.streaming_print(response)
    
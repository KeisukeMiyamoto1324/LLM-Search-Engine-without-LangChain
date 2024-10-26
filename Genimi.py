from Chat_Query import *
from LLM import *

import google.generativeai as genai
import os, base64
from PIL import Image
from typing import List


class Gemini:
    def __init__(self) -> None:
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
        self.reply = None
        
    def decode_base64_image(self, base64_string):
        image_data = base64.b64decode(base64_string)
        image = Image.open(BytesIO(image_data))
        return image
    
    def make_prompt(self, querys: list[Chat_request]) -> list:
        messages = []
        
        for index, query in enumerate(querys):
            prompt = ""
            
            if query.knowledge != None:
                prompt += (
                    "\n***********************************************************"
                    "\nKnowledge section:"
                    "\nUse information below to generate beneficial answer."
                    "\n***********************************************************\n"
                )
                prompt += query.knowledge.decode_to_str(use_knowledge=query.use_knowledge)
                
                prompt += (
                    "\n***********************************************************"
                    "\nPrompt section:"
                    "\nBelow is a request from user. Your answer must follow the prompt."
                    "\n***********************************************************\n"
                )
                prompt += query.prompt
                
            else:
                prompt = query.prompt
                
            if query.images == None:
                if query.role == Role.user:
                    messages.append({"role": "user", "parts": prompt})
                elif query.role == Role.ai:
                    messages.append({"role": "model", "parts": prompt})
                
            else:
                parts = [self.decode_base64_image(image) for image in query.images[:100]] + [prompt]
                messages.append({"role": "user", "parts": parts})
                
        return messages
    
    def invoke_stream(self, model: LLM, querys: list[Chat_request]):
        
        client = genai.GenerativeModel(
                    model_name=model.value.name,
                    system_instruction=querys[0].prompt)
        chat = client.start_chat(history=self.make_prompt(querys=querys[1:-1]))
        
        prompt = self.make_prompt(querys=[querys[-1]])
        response = chat.send_message(prompt[0], stream=True)
        
        input_tokens = 0
        output_tokens = 0
        text = ""
        
        for token in response:
            if hasattr(token, "_result"):
                input_tokens = token._result.usage_metadata.prompt_token_count
                output_tokens = token._result.usage_metadata.candidates_token_count
                
                text += token._result.candidates[0].content.parts[0].text
                yield token._result.candidates[0].content.parts[0].text
                
        reply = Chat_response(text=text,
                              model=model,
                              input_token=input_tokens,
                              output_token=output_tokens,
                              input_cost=input_tokens * model.value.input_cost,
                              output_cost=output_tokens * model.value.output_cost,
                              total_cost=input_tokens * model.value.input_cost + output_tokens * model.value.output_cost)
        self.reply = reply
        
        return reply
        
    def invoke(self, model: LLM, querys: list[Chat_request]) -> Chat_response:
        
        client = genai.GenerativeModel(
                    model_name=model.value.name,
                    system_instruction=querys[0].prompt)
        chat = client.start_chat(history=self.make_prompt(querys=querys[1:-1]))
        
        prompt = self.make_prompt(querys=[querys[-1]])
        response = chat.send_message(prompt[0])
        
        reply = reply = Chat_response(text=response.text,
                              model=model,
                              input_token=response.usage_metadata.prompt_token_count,
                              output_token=response.usage_metadata.candidates_token_count,
                              input_cost=response.usage_metadata.prompt_token_count * model.value.input_cost,
                              output_cost=response.usage_metadata.candidates_token_count * model.value.output_cost,
                              total_cost=response.usage_metadata.prompt_token_count * model.value.input_cost + response.usage_metadata.candidates_token_count * model.value.output_cost)
        
        self.reply = reply
        
        return reply
    

if __name__ == "__main__":
    ai = Gemini()
    messages = [Chat_request(prompt="Your name is Mike. You are very good at playing teniss."),
                Chat_request(prompt="My name is Keisuke."),
                Chat_request(prompt="what are you good at?")]
    
    response = ai.invoke_stream(model=LLM.gemini_1_5_flash, querys=messages)
    
    for token in response:
        print(token, end="")
        
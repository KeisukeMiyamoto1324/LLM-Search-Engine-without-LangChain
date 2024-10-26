from Chat_Query import *
from LLM import *

from openai import OpenAI
from typing import List


class ChatGPT:
    def __init__(self) -> None:
        self.reply = None
    
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
                # print(prompt)
            else:
                prompt += query.prompt
            
            if query.images == None:
                messages.append({"role": query.role.value, "content": prompt})
            else:
                content = [{"type": "text", "text": prompt}]

                for image in query.images[:80]:
                    content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image}"}})
                
                messages.append({"role": "user", "content": content})
                
        return messages
    
        
    def invoke_stream(self, model: LLM, querys: list[Chat_request]):
        client = OpenAI()

        response = client.chat.completions.create(
            messages=self.make_prompt(querys=querys),
            model=model.value.name,
            stream=True,
            stream_options={
                "include_usage": True
            }
        )
        
        text = ""
        
        for chunk in response:
            if hasattr(chunk, 'choices') and chunk.choices and chunk.choices[0]:
                text += chunk.choices[0].delta.content or ""
                yield (chunk.choices[0].delta.content or "")
                
            if hasattr(chunk, 'usage') and chunk.usage is not None:
                usage = chunk.usage
                reply = Chat_response(text=text,
                              model=model,
                              input_token=usage.prompt_tokens,
                              output_token=usage.completion_tokens,
                              input_cost=usage.prompt_tokens * model.value.input_cost,
                              output_cost=usage.completion_tokens * model.value.output_cost,
                              total_cost=usage.prompt_tokens * model.value.input_cost + usage.completion_tokens * model.value.output_cost)
        
                self.reply = reply
        yield "\n"
    
    
    def invoke(self, model: LLM, querys: list[Chat_request]) -> Chat_response:
        client = OpenAI()
        
        response = client.chat.completions.create(
            messages=self.make_prompt(querys=querys),
            model=model.value.name
        )
        
        reply = Chat_response(text=response.choices[0].message.content,
                              model=model,
                              input_token=response.usage.prompt_tokens,
                              output_token=response.usage.completion_tokens,
                              input_cost=response.usage.prompt_tokens * model.value.input_cost,
                              output_cost=response.usage.completion_tokens * model.value.output_cost,
                              total_cost=response.usage.prompt_tokens * model.value.input_cost + response.usage.completion_tokens * model.value.output_cost)
        
        self.reply = reply
        
        return reply
        
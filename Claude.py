from Chat_Query import *
from LLM import *

from anthropic import Anthropic
from typing import List


class Claude:
    def __init__(self) -> None:
        self.reply = None
    
    def make_prompt(self, querys: list[Chat_request]) -> list:
        messages = []
        
        for index, query in enumerate(querys[1:]):
            prompt = ""
            
            if query.knowledge != None:
                prompt  = query.knowledge.decode_to_str(use_knowledge = query.use_knowledge)
                prompt += "Use the information above to generate your answer if they are necessary.\n\n"
                prompt += "----------------------------\nprompt:\n"
                prompt += query.prompt
            else:
                prompt = query.prompt
                
            if query.images == None:
                messages.append({"role": query.role.value, "content": prompt})
            else:
                content = []

                for index, image in enumerate(query.images[:100]):
                    content.append({"type": "text","text": f"image{index}"})
                    content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image}}) 
                
                content.append({"type": "text","text": prompt})
                messages.append({"role": "user", "content": content})
                
        return messages
    
    
    def invoke_stream(self, model: LLM, querys: list[Chat_request]):
        client = Anthropic()

        response = client.messages.create(
            max_tokens=1000,
            system=querys[0].prompt,
            messages=self.make_prompt(querys=querys),
            model=model.value.name,
            stream=True
        )
        
        text = ""
        
        for chunk in response:
            if hasattr(chunk, 'delta') and hasattr(chunk.delta, 'text'):
                text += chunk.delta.text
                yield chunk.delta.text

            if hasattr(chunk, "message") and hasattr(chunk.message, "usage"):
                input_tokens = chunk.message.usage.input_tokens
            
            if hasattr(chunk, "usage"):
                output_tokens = chunk.usage.output_tokens
        
        reply = Chat_response(text=text,
                              model=model,
                              input_token=input_tokens,
                              output_token=output_tokens,
                              input_cost=input_tokens * model.value.input_cost,
                              output_cost=output_tokens * model.value.output_cost,
                              total_cost=input_tokens * model.value.input_cost + output_tokens * model.value.output_cost)
        self.reply = reply
        
        yield "\n"
        
        
    def invoke(self, model: LLM, querys: list[Chat_request]) -> Chat_response:
        client = Anthropic()
        
        response = client.messages.create(
            max_tokens=1000,
            system=querys[0].prompt,
            messages=self.make_prompt(querys=querys),
            model=model.value.name
        )
        
        reply = Chat_response(text=response.content[0].text,
                              model=model,
                              input_token=response.usage.input_tokens,
                              output_token=response.usage.output_tokens,
                              input_cost=response.usage.input_tokens * model.value.input_cost,
                              output_cost=response.usage.output_tokens * model.value.output_cost,
                              total_cost=response.usage.input_tokens * model.value.input_cost + response.usage.output_tokens * model.value.output_cost)
        self.reply = reply
        
        return reply
        

if __name__ == "__main__":
    ai = Claude()
    messages = [Chat_request(prompt="you are great!"),
                Chat_request(prompt="tell me about the history of aviation shortly.")]
    
    for token in ai.invoke_stream(model=LLM.claude_3_5_sonnet, querys=messages):
        print(token, end="")
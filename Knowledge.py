from typing import List


class Knowledge:
    class memory:
        def __init__(self, content: str, title: str=None, link: str=None) -> None:
            self.title = title
            self.link = link
            self.content = content
            
        def __str__(self) -> str:
            return f"title:  {self.title}\nlink:   {self.link}\ncontent: {self.content}" 
    
    def __init__(self, capacity: int=100) -> None:
        self.memories: list[Knowledge.memory] = [None] * capacity
        self.summaries: list[str] = [None] * capacity
        
        
    def add(self, content: list[memory], index: int):
        if index >= len(self.memories):
            raise Exception(f"Knowledge.add: index out of range: {len(self.memories)}")
        
        self.memories[index] = content
        
        
    def summarize(self, summary: str, index: int):
        if index >= len(self.memories):
            raise Exception(f"Knowledge.add: index out of range: {len(self.memories)}")
        
        self.summaries[index] = summary
        
    
    def get(self, index: int) -> list[memory]:
        if index >= len(self.memories):
            raise Exception(f"Knowledge.get: index out of range: {len(self.memories)}")
        
        return self.memories[index]
    
    
    def decode_to_str(self, use_knowledge: list) -> str:
        if len(use_knowledge) == 0:
            return ""

        result = "------------------------------\n"
        for index in use_knowledge:
            memory = self.get(index=index)
            
            if memory is None:
                continue
            
            for i, memory in enumerate(memory):
                string = str(memory)
                result += f"index: {index}-{i}\n{string}\n\n------------------------------\n"
        
        return result
    
    def decode_to_str_all(self) -> str:
        result = ""
        
        for index, memory in enumerate(self.memories):
            if memory is not None:
                result += self.decode_to_str(index=index)
                
        return result
    

if __name__ == "__main__":
    pass
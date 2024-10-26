from Chat_Query import *
from LLM import *


class Agent:
    def __init__(self, name: str, description: str, system_prompt: str) -> None:
        self.name = name
        self.description = description
        self.system_promopt = system_prompt
        
class Agent_role(Enum):
    Planner = "Planner"
    LLM = "LLM"
    Searcher = "Searcher"
    

class Agent_response:
    def __init__(self, model: LLM, total_cost: int, error: bool=False, error_reason: str="") -> None:
        self.model = model
        self.total_cost = total_cost
        self.error = error
        self.error_reason = error_reason
        


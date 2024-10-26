from Agent import *
from Chatbot_manager import *

from typing import List
import json, datetime

Planner_system_prompt = """
- Roles of Subordinates:
    1. Searcher 
        - Has access to the Internet via a search engine.
        - Can retrieve the latest data or information that is not available to the LLM.
        - The query given to the Searcher must be simple and focused on a single topic.
    
    2. LLM 
        - Fluent in any language.
        - Has limited knowledge of real-world events, so it relies on external resources for generating content.
        - Can be used for tasks like writing or summarizing information.
   

- Instructions for the Planner (You):
    - Input:
        - You will be provided with a user request in the form of a string, referred to as "prompt."

    - Output:
        - You must create a step-by-step plan for accomplishing the task specified in the prompt.
    
    - Format of the Output: 
        Output the plan in JSON format as follows:

        [
            {"number": the order of the steps, "role": the subordinate to call, "query": what must be accomplished in this step, "pre_result": the step numbers that need to be completed before this one, or "None" if no prior results are needed},
            {"number": the order of the steps, "role": the subordinate to call, "query": what must be accomplished in this step, "pre_result": the step numbers that need to be completed before this one, or "None" if no prior results are needed},
            ...
            {"number": the order of the steps, "role": "LLM", "query": the original user prompt, "pre_result": the step numbers that need to be completed before this one, or "None" if no prior results are needed}
        ]


- Example of format:
    If the prompt is "唐揚げの作り方", the example of your output is below.
    [
        {"number": "0", "role": "Searcher", "query": "唐揚げ丼の作り方を調べる", "pre_result": "None"},
        {"number": "1", "role": "Searcher", "query": "丼料理の作り方を調べる", "pre_result": "None"},
        {"number": "2", "role": "LLM", "query": "唐揚げ丼の作り方", "pre_result": "0, 1"}
    ]


- Important Details:
    1. "number"
        - The step number must start from "0" (not "1").
    
    2. "role"
        - It must be either "Searcher" or "LLM."

    3. "query"
        - The "query" must clearly specify what needs to be accomplished in the given step. When formulating the "query," keep in mind the overall task as described in the prompt. What is the user's final goal? What is the purpose behind the prompt?
        - "query" should be a complete sentence. (not a list of words).
        - Be logical in structuring the query.

    4. "pre_result"
        - "pre_result" indicates which step(s) must be completed before this one. For example: `"0, 1, 2"`. Do not use square brackets or quotation marks around numbers. If no prior results are needed, use `"None"`.

- Language:
   - Use the same language as the given prompt unless directed otherwise.

- Additional Specifications:
    - Consider past conversation history. If past conversation history can be used to answer a user's question, do not use Searcher, use LLM only.
    - Each step of the procedure must be simple enough for the assigned subordinate to perform with their limited functionality.
    - Divide the prompt into as many steps as necessary, with each step addressing only one topic or type of action.
    - The final task (last step) must always be assigned to the LLM, and the query in that step must be exactly the same as the original prompt.


- Limitations:
    1. When outputting numbers in the JSON, always enclose them in double quotes (e.g., `"0"`, `"1"`).
    2. Do not output any text other than the JSON format specified above. Follow the format strictly. Avoid markdown, comments, or extra text.


By restructuring the instructions into a clear and detailed format, this version makes it easier to follow the process and avoid any ambiguity in execution.
"""


class Task:
    def __init__(self, number: int, agent_role, query: str, pre_result: list) -> None:
        self.number = number
        self.agent_role = agent_role
        self.query = query
        self.pre_result = pre_result
    
class Planner(Agent):
    def __init__(self) -> None:
        self.name = Agent_role.Planner
        self.description = "A role to devide given prompt to multiple easy task. Each task should have only one topic, in other words, only one action."
        self.system_prompt = Planner_system_prompt
        self.tasks = []
        
        super().__init__(self.name, self.description, self.system_prompt)
        
        self.Planner = Chatbot_manager(system_prompt=f"current time: {datetime.datetime.now()}\n" + self.system_promopt)
        
    def export_memory(self):
        pass
    
    def import_memory(self, memory: list[Chat_request]):
        if len(memory) > 0:
            if memory[0].role == Role.system:
                self.Planner.import_memory(memory=memory)
                self.Planner.system_prompt(prompt=Planner_system_prompt)
            else:
                system_prompt = self.Planner.system_prompt(prompt=Planner_system_prompt)
                self.Planner.import_memory(memory=[system_prompt] + memory)
        else:
                system_prompt = self.Planner.system_prompt(prompt=Planner_system_prompt)
                self.Planner.import_memory(memory=[system_prompt])
            
        
    def invoke(self, model: LLM, query: Chat_request) -> list[Task]:
        self.Planner.system_prompt(prompt=Planner_system_prompt)
        tasks = self.Planner.invoke(model=model, query=query)
        self.tasks = self.json_to_tasks(json_string=tasks.text)
        self.tasks[-1].query = query.prompt
        
        return self.tasks
        
    def json_to_tasks(self, json_string: str) -> list:
        try:
            task_dicts = json.loads(json_string.replace("```json", "").replace("```", "").strip())
        except:
            task = Task(
                number=0,
                agent_role="LLM",
                query=json_string,
                pre_result=None
            )
            
            return [task]
        
        tasks = []
        for task_dict in task_dicts:            
            task = Task(
                number=int(task_dict['number']),
                agent_role=task_dict['role'],
                query=task_dict['query'],
                pre_result=task_dict['pre_result']
            )
            # print(task.pre_result)
            task.pre_result = None if task.pre_result == "None" else [int(x) for x in task.pre_result.replace('"', "").replace("[", "").replace("]", "").split(',')]
            tasks.append(task)
            
        
        return tasks
        


if __name__ == "__main__":
    pass
        

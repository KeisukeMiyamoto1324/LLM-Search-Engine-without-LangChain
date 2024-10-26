from enum import Enum

class Company(Enum):
    openai = 1
    anthropic = 2
    google = 3

class Model:
    def __init__(self, company: Company, name: str, input_cost: float, output_cost: float, cashe_input_cost=None, cache_output_cost=None) -> None:
        self.company = company
        self.name = name
        self.input_cost = input_cost
        self.output_cost = output_cost
        self.cache_input_cost = cashe_input_cost
        self.cache_outut_cost = cache_output_cost

class LLM(Enum):
    gpt_4o = Model(company=Company.openai,
                   name='gpt-4o-2024-08-06',
                   input_cost=2.5/1000000,
                   output_cost=10.0/1000000)
    
    gpt_4o_mini = Model(company=Company.openai,
                   name='gpt-4o-mini',
                   input_cost=0.15/1000000,
                   output_cost=0.6/1000000)
    
    claude_3_5_sonnet = Model(company=Company.anthropic,
                   name='claude-3-5-sonnet-20240620',
                   input_cost=3.0/1000000,
                   output_cost=15.0/1000000,
                   cashe_input_cost=3.75/1000000,
                   cache_output_cost=0.3/1000000)
    
    gemini_1_5_flash = Model(company=Company.google,
                   name='gemini-1.5-flash',
                   input_cost=0,
                   output_cost=0)
    
    gemini_1_5_pro = Model(company=Company.google,
                   name='gemini-1.5-pro',
                   input_cost=0,
                   output_cost=0)
    
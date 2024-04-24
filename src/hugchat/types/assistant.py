from dataclasses import dataclass

@dataclass
class Assistant:
    assistant_id: str
    author: str
    name: str
    model_name: str
    pre_prompt: str
    description: str 

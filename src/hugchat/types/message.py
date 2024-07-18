from dataclasses import dataclass
from typing import List
from .model import Model

@dataclass
class MessageNode:
    '''
    huggingchat message node, currently only maintain id, role, date and content.
    '''
    id: str
    role: str  # "user", "system", or "assistant"
    content: str
    ancestors: List[str]
    children: List[str]
    created_at: float  # timestamp
    updated_at: float  # timestamp

    def __str__(self) -> str:
        return f"MessageNode(id={self.id}, role={self.role}, content={self.content}, created_at={self.created_at}, updated_at={self.updated_at})"


class Conversation:
    def __init__(
        self,
        id: str = None,
        title: str = None,
        model: Model = None,
        system_prompt: str = None,
        history: list = []
    ):
        """
        Returns a conversation object
        """

        self.id: str = id
        self.title: str = title
        self.model = model
        self.system_prompt: str = system_prompt
        self.history: List[MessageNode] = history

    def __str__(self) -> str:
        return self.id

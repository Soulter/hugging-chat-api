from dataclasses import dataclass


@dataclass
class Tool:
    '''
    Class used to represent tools used by the model
    '''

    uuid: str
    result: str

    def __str__(self) -> str:
        return f"Tool(uuid={self.uuid}, result={self.result})"

from dataclasses import  dataclass
import time
from typing import Generator, Union

class WebSearchSource:
    title: str
    link: str
    hostname: str

@dataclass
class Message(Generator):
    g: Generator
    web_search: bool = False
    web_search_sources: Union[list[WebSearchSource], None] = None
    final_answer: Union[str, None] = None

    def __next__(self):
        return next(self.g)

    def __iter__(self):
        return self

    def throw(
        self,
        __typ: type[BaseException],
        __val: BaseException | object = None,
        __tb = None,
    ):
        return self.g.throw(__typ, __val, __tb)

    def send(self, __value):
        return self.g.send(__value)

if __name__ == "__main__":
    def gen() -> Generator:
        n = 0
        c = 10
        while n < c:
            n += 1
            q = yield n
            time.sleep(0.5)
    a = Message(gen())
    for i in a:
        print(i)

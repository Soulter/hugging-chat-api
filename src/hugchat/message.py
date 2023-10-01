from dataclasses import  dataclass
import time
from typing import Generator, Union


MSGTYPE_FINAL = "finalAnswer"
MSGTYPE_STREAM = "stream"
MSGTYPE_WEB = "webSearch"
MSGTYPE_STATUS = "status"


class WebSearchSource:
    title: str
    link: str
    hostname: str


@dataclass
class Message(Generator):
    g: Generator
    web_search: bool = False
    web_search_sources: list[WebSearchSource] = list()
    final_answer: Union[str, None] = None
    web_search_done: bool = not web_search
    stream_done: bool = False

    def __next__(self):
        a: dict = next(self.g)
        t: str = a["type"]
        if t == MSGTYPE_FINAL:
            self.final_answer = a["text"]
            self.done = True
        elif t == MSGTYPE_STREAM:
            self.web_search_done = True
        elif t == MSGTYPE_WEB:
            self.web_search_sources = list()
            sources = a['sources']
            for source in sources:
                wss = WebSearchSource()
                wss.title = source['title']
                wss.link = source['link']
                wss.hostname = source['hostname']
                self.web_search_sources.append(wss)
            
        return a

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

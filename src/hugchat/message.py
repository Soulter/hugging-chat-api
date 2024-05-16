from typing import Generator, Union

from .exceptions import ChatError, ModelOverloadedError
import json

RESPONSE_TYPE_FINAL = "finalAnswer"
RESPONSE_TYPE_STREAM = "stream"
RESPONSE_TYPE_WEB = "webSearch"
RESPONSE_TYPE_STATUS = "status"
MSGTYPE_ERROR = "error"

MSGSTATUS_PENDING = 0
MSGSTATUS_RESOLVED = 1
MSGSTATUS_REJECTED = 2


class WebSearchSource:
    title: str
    link: str

    def __str__(self):
        return json.dumps({
            "title": self.title,
            "link": self.link,
        })


class Message(Generator):
    """
    :Args:
        * g: Generator
        * _stream_yield_all: bool = False
        * web_search: bool = False
        - web_search_sources: list[WebSearchSource] = list()
        - text: str = ""
        - web_search_done: bool = not web_search
        - msg_status: int = MSGSTATUS_PENDING
        - error: Union[Exception, None] = None

    A wrapper of `Generator` that receives and process the response

    :Example:
    .. code-block:: python

        msg = bot.chat(...)

        # stream process
        for res in msg:
            ... # process
        else:
            if msg.done() == MSGSTATUS_REJECTED:
                raise msg.error

        # or simply use:
        final = msg.wait_until_done()
    """

    g: Generator
    _stream_yield_all: bool = False
    web_search: bool = False

    web_search_sources: list = []
    # For backward compatibility, we have to reserve the `text` field.
    text: str = ""
    web_search_done: bool = not web_search
    msg_status: int = MSGSTATUS_PENDING
    error: Union[Exception, None] = None

    def __init__(
        self,
        g: Generator,
        _stream_yield_all: bool = False,
        web_search: bool = False,
    ) -> None:
        self.g = g
        self._stream_yield_all = _stream_yield_all
        self.web_search = web_search

    def _filterResponse(self, obj: dict):
        if not obj.__contains__("type"):
            if obj.__contains__("message"):
                raise ChatError(f"Server returns an error: {obj['message']}")
            else:
                raise ChatError(f"No `type` and `message` returned: {obj}")

    def __next__(self) -> dict:
        if self.msg_status == MSGSTATUS_RESOLVED:
            raise StopIteration
        elif self.msg_status == MSGSTATUS_REJECTED:
            if self.error is not None:
                raise self.error
            else:
                raise Exception(
                    "Message stauts is `Rejected` but no error found")

        try:
            a: dict = next(self.g)
            self._filterResponse(a)
            t: str = a["type"]
            message_type: str = ""
            if t == RESPONSE_TYPE_FINAL:
                self.text = a["text"]
                self.msg_status = MSGSTATUS_RESOLVED
            elif t == RESPONSE_TYPE_WEB:
                # gracefully pass unparseable webpages
                if message_type != MSGTYPE_ERROR and a.__contains__("sources"):
                    self.web_search_sources.clear()
                    sources = a["sources"]
                    for source in sources:
                        wss = WebSearchSource()
                        wss.title = source["title"]
                        wss.link = source["link"]
                        self.web_search_sources.append(wss)
            elif "messageType" in a:
                message_type: str = a["messageType"]
                if message_type == MSGTYPE_ERROR:
                    self.error = ChatError(a["message"])
                    self.msg_status = MSGSTATUS_REJECTED
                if t == RESPONSE_TYPE_STREAM:
                    self.web_search_done = True
                elif t == RESPONSE_TYPE_STATUS:
                    pass
            else:
                if "Model is overloaded" in str(a):
                    self.error = ModelOverloadedError(
                        "Model is overloaded, please try again later or switch to another model."
                    )
                    self.msg_status = MSGSTATUS_REJECTED
                elif a.__contains__(MSGTYPE_ERROR):
                    self.error = ChatError(a[MSGTYPE_ERROR])
                    self.msg_status = MSGSTATUS_REJECTED
                else:
                    self.error = ChatError(f"Unknown json response: {a}")

            # If _stream_yield_all is True, yield all responses from the server.
            if self._stream_yield_all or t == RESPONSE_TYPE_STREAM:
                return a
            else:
                return self.__next__()
        except StopIteration:
            if self.msg_status == MSGSTATUS_PENDING:
                self.error = ChatError(
                    "Stream of responses has abruptly ended (final answer has not been received)."
                )
                raise self.error
            pass
        except Exception as e:
            # print("meet error: ", str(e))
            self.error = e
            self.msg_status = MSGSTATUS_REJECTED
            raise self.error

    def __iter__(self):
        return self

    def throw(
        self,
        __typ,
        __val=None,
        __tb=None,
    ):
        return self.g.throw(__typ, __val, __tb)

    def send(self, __value):
        return self.g.send(__value)

    def get_final_text(self) -> str:
        """
        :Return:
            - self.text
        """
        return self.text

    def get_search_sources(self) -> list:
        """
        :Return:
            - self.web_search_sources
        """
        return self.web_search_sources

    def search_enabled(self) -> bool:
        """
        :Return:
            - self.web_search
        """
        return self.web_search

    def wait_until_done(self) -> str:
        """
        :Return:
            - self.text if resolved else raise error

        wait until every response is resolved
        """
        while not self.is_done():
            self.__next__()
        if self.is_done() == MSGSTATUS_RESOLVED:
            return self.text
        elif self.error is not None:
            raise self.error
        else:
            raise Exception("Rejected but no error captured!")

    def is_done(self):
        """
        :Return:
            - self.msg_status

        3 status:
        - MSGSTATUS_PENDING = 0    # running
        - MSGSTATUS_RESOLVED = 1   # done with no error(maybe?)
        - MSGSTATUS_REJECTED = 2   # error raised
        """
        return self.msg_status

    def is_done_search(self):
        """
        :Return:
            - self.web_search_done

        web search result will be set to `done` once the token is received
        """
        return self.web_search_done

    def __str__(self):
        return self.wait_until_done()

    def __getitem__(self, key: str) -> str:
        print("_getitem_")
        self.wait_until_done()
        print("done")
        if key == "text":
            return self.text
        elif key == "web_search":
            return self.web_search
        elif key == "web_search_sources":
            return self.web_search_sources

    def __add__(self, other: str) -> str:
        self.wait_until_done()
        return self.text + other

    def __radd__(self, other: str) -> str:
        self.wait_until_done()
        return other + self.text

    def __iadd__(self, other: str) -> str:
        self.wait_until_done()
        self.text += other
        return self.text


if __name__ == "__main__":
    pass

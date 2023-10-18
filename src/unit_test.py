"""
For test hugchat
"""

import os
import logging
from .hugchat import hugchat
from .hugchat.login import Login

logging.basicConfig(level=logging.DEBUG)

EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("PASSWORD")

chatbot: hugchat.ChatBot = None
my_conversation: hugchat.conversation = None

class TestAPI(object):
    """
    test hugchat api
    """
    def test_login(self):
        """
        test login module
        """
        global chatbot
        sign = Login(EMAIL, PASSWORD)
        cookies = sign.login()
        sign.saveCookiesToDir("./fortest")
        assert cookies is not None
        chatbot = hugchat.ChatBot(cookies=cookies.get_dict(), default_llm=0)

    def test_create_conversation(self):
        """
        test create conversation module
        """
        global my_conversation
        res = chatbot.new_conversation()
        assert res is not None
        chatbot.change_conversation(res)
        my_conversation = res
        print("Test create conversation:",str(res))
    
    def test_chat_without_web_search(self):
        """
        test chat module without web search
        """
        res = str(chatbot.chat("Just reply me `test_ok`"))
        assert res is not None

    def test_chat_web_search(self):
        """
        test chat module with web search
        """
        res = str(chatbot.chat("What's the weather like in London today?", web_search=True))
        assert res is not None

    def test_generator(self):
        """
        test generator module
        """
        res = chatbot.chat("What's the weather like in London today?", web_search=True, _stream_yield_all=True)
        for i in res:
            print(i, flush=True)

        assert res is not None

if __name__ == "__main__":
    test = TestAPI()
    test.test_login()
    test.test_create_conversation()
    test.test_chat_without_web_search()
    test.test_chat_web_search()
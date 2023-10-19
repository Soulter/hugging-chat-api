"""
For test hugchat
"""

import os
import logging
from .hugchat import hugchat, cli
from .hugchat.login import Login
from sys import argv
from unittest.mock import patch

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
        print("Test create conversation:", str(res))
    
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
    
    # def test_delete_conversation(self):
    #     """
    #     test delete conversation module
    #     """
    #     chatbot.delete_conversation(my_conversation)

    def test_delete_all_conversations(self):
        """
        test delete all conversations module
        """
        chatbot.delete_all_conversations()
    
    def test_cli(self):
        global times_run
        times_run = -1

        # many not enabled because the CLI is currently very broken
        return_strings = [
            "/help",
            "Hello!",
            # "/new",
            # "/ids",
            # "/sharewithauthor off"
        ]
        def input_callback(_):
            global times_run
            times_run += 1

            if times_run >= len(return_strings):
                raise KeyboardInterrupt()

            return return_strings[times_run]
        
        argv.append("-u")
        argv.append(EMAIL)
        try:
            with patch("getpass.getpass", side_effect=lambda _: PASSWORD):
                with patch('builtins.input', side_effect=input_callback):
                    cli.cli()
        except KeyboardInterrupt:
            print("Exited CLI")

if __name__ == "__main__":
    test = TestAPI()
    test.test_login()
    test.test_create_conversation()
    # test.test_delete_conversation()
    test.test_chat_without_web_search()
    test.test_chat_web_search()
    test.test_delete_all_conversations()
    test.test_cli()
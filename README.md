# hugging-chat-api
HuggingChat Python API

[![PyPi](https://img.shields.io/pypi/v/hugchat.svg)](https://pypi.python.org/pypi/hugchat)
[![Support_Platform](https://img.shields.io/pypi/pyversions/hugchat)](https://pypi.python.org/pypi/hugchat)
[![Downloads](https://static.pepy.tech/badge/hugchat)](https://pypi.python.org/pypi/hugchat)
- ChatGPT 平替！
- 无需任何账号，中国大陆的朋友无需梯子

Leave a star :)

# How to Use
```bash
pip install hugchat
```

```py
from hugchat import hugchat
chatbot = hugchat.ChatBot()
print(chatbot.chat("HI"))

# New a conversation (ignore error)
id = chatbot.new_conversation()
chatbot.change_conversation(id)

# Get conversation list
conversation_list = chatbot.get_conversation_list()
```


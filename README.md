# hugging-chat-api
HuggingChat Python API

[![PyPi](https://img.shields.io/pypi/v/hugchat.svg)](https://pypi.python.org/pypi/hugchat)
[![Support_Platform](https://img.shields.io/pypi/pyversions/hugchat)](https://pypi.python.org/pypi/hugchat)
[![Downloads](https://static.pepy.tech/badge/hugchat)](https://pypi.python.org/pypi/hugchat)

Leave a star :)

# How to Use

## Basic mode
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

The `chat()` function can receive many parameters:

- `text`: Required.
- `temperature`: Optional
- `top_p`: Optional
- `repetition_penalty`: Optional
- `top_k`: Optional
- `truncate`: Optional
- `watermark`: Optional
- `max_new_tokens`: Optional
- `stop`: Optional
- `return_full_text`: Optional
- `stream`: Optional
- `use_cache`: Optional
- `is_retry`: Optional
- `retry_count`: Optional. Number of retries for requesting huggingchat. Default is 5

## CLI mode

> `version 0.0.5.1` or newer

You can use `cli mode` to test the repo: 

```
from hugchat import hugchat
hugchat.cli()
```

some commands in cli mode:
- `/new`: new and change a coonversation.

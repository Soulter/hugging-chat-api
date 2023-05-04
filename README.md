# hugging-chat-api

HuggingChat Python API

[![PyPi](https://img.shields.io/pypi/v/hugchat.svg)](https://pypi.python.org/pypi/hugchat)
[![Support_Platform](https://img.shields.io/pypi/pyversions/hugchat)](https://pypi.python.org/pypi/hugchat)
[![Downloads](https://static.pepy.tech/badge/hugchat)](https://pypi.python.org/pypi/hugchat)

Leave a star :)

## How to Use

### Basic mode

```bash
pip install hugchat
```

```py
from hugchat import hugchat
chatbot = hugchat.ChatBot()
print(chatbot.chat("HI"))

# Create a new conversation
id = chatbot.new_conversation()
chatbot.change_conversation(id)

# Get conversation list
conversation_list = chatbot.get_conversation_list()
```

The `chat()` function can receive many parameters:

- `text`: Required[str].
- `temperature`: Optional[float]. Default is 0.9
- `top_p`: Optional[float]. Default is 0.95
- `repetition_penalty`: Optional[float]. Default is 1.2
- `top_k`: Optional[int]. Default is 50
- `truncate`: Optional[int]. Default is 1024
- `watermark`: Optional[bool]. Default is False
- `max_new_tokens`: Optional[int]. Default is 1024
- `stop`: Optional[list]. Default is ["</s>"]
- `return_full_text`: Optional[bool]. Default is False
- `stream`: Optional[bool]. Default is True
- `use_cache`: Optional[bool]. Default is False
- `is_retry`: Optional[bool]. Default is False
- `retry_count`: Optional[int]. Number of retries for requesting huggingchat. Default is 5

### CLI mode

> `version 0.0.5.2` or newer

Simply run the following command in your terminal to start the CLI mode

```bash
python -m hugchat.cli
```

Commands in cli mode:

- `/new` : Create and switch to a new conversation.
- `/ids` : Shows a list of all ID numbers and ID strings in current session.
- `/switch <id>` : Switches to the ID number passed.
- `/exit` : Closes CLI environment.

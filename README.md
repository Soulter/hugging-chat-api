# hugging-chat-api

English | [简体中文](README_cn.md)

Unofficial HuggingChat Python API, extensible for chatbots etc.

[![PyPi](https://img.shields.io/pypi/v/hugchat.svg)](https://pypi.python.org/pypi/hugchat)
[![Support_Platform](https://img.shields.io/pypi/pyversions/hugchat)](https://pypi.python.org/pypi/hugchat)
[![Downloads](https://static.pepy.tech/badge/hugchat)](https://pypi.python.org/pypi/hugchat)

Recently new updates:
- Memorize context
- Change LLMs supported. See more at https://github.com/Soulter/hugging-chat-api/issues/56 (v0.0.9)

## Installation
```bash
pip install hugchat
```
or `pip3 install hugchat`

## Usage

### API

```py
from hugchat import hugchat
from hugchat.login import Login

# Log in to huggingface and grant authorization to huggingchat
sign = Login(email, passwd)
cookies = sign.login()

# Save cookies to the local directory
cookie_path_dir = "./cookies_snapshot"
sign.saveCookiesToDir(cookie_path_dir)

# Load cookies when you restart your program:
# sign = login(email, None)
# cookies = sign.loadCookiesFromDir(cookie_path_dir) # This will detect if the JSON file exists, return cookies if it does and raise an Exception if it's not.

# Create a ChatBot
chatbot = hugchat.ChatBot(cookies=cookies.get_dict())  # or cookie_path="usercookies/<email>.json"
print(chatbot.chat("Hi!"))

# Create a new conversation
id = chatbot.new_conversation()
chatbot.change_conversation(id)

# Get conversation list
conversation_list = chatbot.get_conversation_list()

# Switch model (default: meta-llama/Llama-2-70b-chat-hf. )
chatbot.switch_llm(0) # Switch to `OpenAssistant/oasst-sft-6-llama-30b-xor`
chatbot.switch_llm(1) # Switch to `meta-llama/Llama-2-70b-chat-hf`
```

The `chat()` function receives these parameters:

- `text`: Required[str].
- `temperature`: Optional[float]. Default is 0.9
- `top_p`: Optional[float]. Default is 0.95
- `repetition_penalty`: Optional[float]. Default is 1.2
- `top_k`: Optional[int]. Default is 50
- `truncate`: Optional[int]. Default is 1024
- `watermark`: Optional[bool]. Default is False
- `max_new_tokens`: Optional[int]. Default is 1024
- `stop`: Optional[list]. Default is ["`</s>`"]
- `return_full_text`: Optional[bool]. Default is False
- `stream`: Optional[bool]. Default is True
- `use_cache`: Optional[bool]. Default is False
- `is_retry`: Optional[bool]. Default is False
- `retry_count`: Optional[int]. Number of retries for requesting huggingchat. Default is 5

### CLI

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
- `/llm`: get available models you can switch to
- `/llm [index]` switch model to given models

- AI is an area of active research with known problems such as biased generation and misinformation. Do not use this application for high-stakes decisions or advice.
- Server resources are precious, it is not recommended to request this API in a high frequency.
(`Hugging Face's CTO🤗` just liked the suggestion)
<div align="center"><img width=500 src="https://github.com/Soulter/hugging-chat-api/assets/37870767/06e64501-02fb-4d4a-ab6f-cf18d8638ace"></img></div>


## Disclaimers

This is not an official [Hugging Face](https://huggingface.co/) product. This is a **personal project** and is not affiliated with [Hugging Face](https://huggingface.co/) in any way. Don't sue us.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Soulter/hugging-chat-api&type=Date)](https://star-history.com/#Soulter/hugging-chat-api&Date)

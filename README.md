# hugging-chat-api

English | [简体中文](README_cn.md)

Unofficial HuggingChat Python API, extensible for chatbots etc.

[![PyPi](https://img.shields.io/pypi/v/hugchat.svg?style=for-the-badge&logo=pypi&logoColor=white)](https://pypi.python.org/pypi/hugchat)
[![Support_Platform](https://img.shields.io/badge/3.6+-%234ea94b.svg?style=for-the-badge&logo=python&logoColor=white)](https://pypi.python.org/pypi/hugchat)
[![DownloadsPW](https://img.shields.io/pypi/dw/hugchat?style=for-the-badge&logo=download&logoColor=white)](https://pypi.python.org/pypi/hugchat)
[![Status](https://img.shields.io/badge/status-operational-%234ea94b.svg?style=for-the-badge&logo=ok&logoColor=white)](https://pypi.python.org/pypi/hugchat)
[![Downloads](https://static.pepy.tech/badge/hugchat?style=for-the-badge&logo=download&logoColor=white)](https://www.pepy.tech/projects/hugchat)


> **Note**
>
> Some recent versions may no longer be fully backward compatible to some extent, a good idea is to review this README or issues promptly after any problem arise.
> 
> Recently new updates:
> - **Custom parameters(temprature, max_token, etc) is no longer supported**
> - Web search
> - Memorize context
> - Supports for changing LLMs ([#56](https://github.com/Soulter/hugging-chat-api/issues/56)) (v0.0.9)

## Installation
```bash
pip install hugchat
```
or
```bash
pip3 install hugchat
```

## Usage

### API

The following are all common usages of this repo, You may not necessarily use all of them, You can add or delete some as needed :)

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

# non stream response
query_result = chatbot.query("Hi!")
print(query_result) # or query_result.text or query_result["text"]

# stream response
for resp in chatbot.query(
    "Hello",
    stream=True
):
    print(resp)

# Use web search (new feature)
query_result = chatbot.query("Hi!", web_search=True)
print(query_result) # or query_result.text or query_result["text"]
for source in query_result.web_search_sources:
    print(source.link)
    print(source.title)
    print(source.hostname)

# Create a new conversation
id = chatbot.new_conversation()
chatbot.change_conversation(id)

# Get conversation list
conversation_list = chatbot.get_conversation_list()

# Get the available models (not hardcore)
models = chatbot.get_available_llm_models()

# Switch model to the given index
chatbot.switch_llm(0) # Switch to the first model
chatbot.switch_llm(1) # Switch to the second model

# Get information about the current conversation
info = chatbot.get_conversation_info()
print(info.id, info.title, info.model, info.system_prompt, info.history)

# Get conversations on the server that are not from the current session (all your conversations in huggingchat)
chatbot.get_remote_conversations(replace_conversation_list=True)

# [DANGER] Delete all the conversations for the logged in user
chatbot.delete_all_conversations()
```

The `query()` function receives these parameters:

- `text`: Required[str].
- `retry_count`: Optional[int]. Number of retries for requesting huggingchat. Default is 5
- `web_search` : Optional[bool]. Whether to use online search.

### CLI

> `version 0.0.5.2` or newer

Simply run the following command in your terminal to start the CLI mode

```bash
python -m hugchat.cli
```

CLI params:

- `-u <your huggingface email>` : Provide account email to login.
- `-p` : Force request password to login, ignores saved cookies.
- `-s` : Enable streaming mode output in CLI.

Commands in cli mode:

- `/new` : Create and switch to a new conversation.
- `/ids` : Shows a list of all ID numbers and ID strings in current session.
- `/switch <id>` : Switches to the ID number or ID string passed.
- `/del <id>` : Deletes the ID number or ID string passed. Will not delete active session.
- `/clear` : Clear the terminal.
- `/llm` : Get available models you can switch to.
- `/llm <index>` : Switches model to given model index based on `/llm`.
- `/sharewithauthor <on|off>` : Changes settings for sharing data with model author. On by default.
- `/exit` : Closes CLI environment.
- `/stream <on|off>`: streaming the response.
- `/web <on|off>`: web search.
- `/web-hint <on|off>`: display web search hint.

- AI is an area of active research with known problems such as biased generation and misinformation. Do not use this application for high-stakes decisions or advice.
- Server resources are precious, it is not recommended to request this API in a high frequency.
(`Hugging Face's CTO🤗` just liked the suggestion)
<div align="center"><img width=500 src="https://github.com/Soulter/hugging-chat-api/assets/37870767/06e64501-02fb-4d4a-ab6f-cf18d8638ace"></img></div>


## Disclaimers

This is not an official [Hugging Face](https://huggingface.co/) product. This is a **personal project** and is not affiliated with [Hugging Face](https://huggingface.co/) in any way. Don't sue us.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Soulter/hugging-chat-api&type=Date)](https://star-history.com/#Soulter/hugging-chat-api&Date)

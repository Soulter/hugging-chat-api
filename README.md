# hugging-chat-api

English | [简体中文](README_cn.md)

Unofficial HuggingChat Python API, extensible for chatbots etc.

[![PyPi](https://img.shields.io/pypi/v/hugchat.svg?logo=pypi&logoColor=white)](https://pypi.python.org/pypi/hugchat)
[![Support_Platform](https://img.shields.io/badge/3.6+-%234ea94b.svg?logo=python&logoColor=white)](https://pypi.python.org/pypi/hugchat)
[![DownloadsPW](https://img.shields.io/pypi/dw/hugchat?logo=download&logoColor=white)](https://pypi.python.org/pypi/hugchat)
[![Downloads](https://static.pepy.tech/badge/hugchat?logo=download&logoColor=white)](https://www.pepy.tech/projects/hugchat)

> **Note**
>
> For the personal reasons, the update of this repo will become slow, and we will ensure that the most basic features can be used normally
> 
> 
> Recently new updates:
> - Assistant(Image Generator, etc)
> - Web search
> - Memorize context
> - Supports for changing LLMs

## Installation
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
EMAIL = "your email"
PASSWD = "your password"
cookie_path_dir = "./cookies/" # NOTE: trailing slash (/) is required to avoid errors
sign = Login(EMAIL, PASSWD)
cookies = sign.login(cookie_dir_path=cookie_path_dir, save_cookies=True)

# Create your ChatBot
chatbot = hugchat.ChatBot(cookies=cookies.get_dict())  # or cookie_path="usercookies/<email>.json"

message_result = chatbot.chat("Hi!") # note: message_result is a generator, the method will return immediately.

# Non stream
message_str: str = message_result.wait_until_done() # you can also print(message_result) directly. 
# get files(such as images)
file_list = message_result.get_files_created() # must call wait_until_done() first!

# tips: model "CohereForAI/c4ai-command-r-plus" can generate images :)

# Stream response
for resp in chatbot.chat(
    "Hello",
    stream=True
):
    print(resp)

# Web search
query_result = chatbot.chat("Hi!", web_search=True)
print(query_result)
for source in query_result.web_search_sources:
    print(source.link)
    print(source.title)

# Create a new conversation
chatbot.new_conversation(switch_to = True) # switch to the new conversation

# Get conversations on the server that are not from the current session (all your conversations in huggingchat)
conversation_list = chatbot.get_remote_conversations(replace_conversation_list=True)
# Get conversation list(local)
conversation_list = chatbot.get_conversation_list()

# Get the available models (not hardcore)
models = chatbot.get_available_llm_models()

# Switch model with given index
chatbot.switch_llm(0) # Switch to the first model
chatbot.switch_llm(1) # Switch to the second model

# Get information about the current conversation
info = chatbot.get_conversation_info()
print(info.id, info.title, info.model, info.system_prompt, info.history)

# Assistant
ASSISTANT_ID = "66017fca58d60bd7d5c5c26c" # get the assistant id from https://huggingface.co/chat/assistants
chatbot.new_conversation(assistant=ASSISTANT_ID, switch_to=True) # create a new conversation with assistant

# [DANGER] Delete all the conversations for the logged in user
chatbot.delete_all_conversations()
```

### CLI

Simply run the following command in your terminal to start the CLI mode

```bash
python -m hugchat.cli
```

CLI params:

- `-u <your huggingface email>` : Provide account email to login.
- `-p` : Force request password to login, ignores saved cookies.
- `-s` : Enable streaming mode output in CLI.
- `-c` : Continue previous conversation in CLI ".

Commands in cli mode:

- `/new` : Create and switch to a new conversation.
- `/ids` : Shows a list of all ID numbers and ID strings in *current session*.
- `/switch` : Shows a list of all conversations' info in *current session*. Then you can choose one to switch to.
- `/switch all` : Shows a list of all conversations' info in *your account*. Then you can choose one to switch to. (not recommended if your account has a lot of conversations)
- `/del <index>` : Deletes the conversation linked with the index passed. Will not delete active session.
- `/delete-all` : Deletes all the conversations for the logged in user.
- `/clear` : Clear the terminal.
- `/llm` : Get available models you can switch to.
- `/llm <index>` : Switches model to given model index based on `/llm`.
- `/share` : Toggles settings for sharing data with model author. On by default.
- `/exit` : Closes CLI environment.
- `/stream` : Toggles streaming the response.
- `/web` : Toggles web search.
- `/web-hint` : Toggles display web search hint.

- AI is an area of active research with known problems such as biased generation and misinformation. Do not use this application for high-stakes decisions or advice.
- Server resources are precious, it is not recommended to request this API in a high frequency.

## Donations
❤

<a href="https://www.buymeacoffee.com/soulter" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="28" width="119"></a>

## Disclaimers

This is not an official [Hugging Face](https://huggingface.co/) product. This is a **personal project** and is not affiliated with [Hugging Face](https://huggingface.co/) in any way. Don't sue us.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Soulter/hugging-chat-api&type=Date)](https://star-history.com/#Soulter/hugging-chat-api&Date)

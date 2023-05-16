# hugging-chat-api

[English](README.md) | 简体中文

HuggingChat Python API

[![PyPi](https://img.shields.io/pypi/v/hugchat.svg)](https://pypi.python.org/pypi/hugchat)
[![Support_Platform](https://img.shields.io/pypi/pyversions/hugchat)](https://pypi.python.org/pypi/hugchat)
[![Downloads](https://static.pepy.tech/badge/hugchat)](https://pypi.python.org/pypi/hugchat)

给个星先😋

## 鉴权 (必需)

### Cookies

<details>
<summary>如何提取Cookies</summary>

- 安装 [Chrome](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm) 或 [Firefox](https://addons.mozilla.org/en-US/firefox/addon/cookie-editor/) 的 cookie editor 扩展
- 访问 [HuggingChat](https://huggingface.co/chat) 并 **登录**
- 打开扩展程序
- 点击右下角的"导出" (将会把内容保存到你的剪贴板上)
- 把你剪贴板上的内容粘贴到 `cookies.json` 文件中

</details>

## 使用方式

### Python调用

```bash
pip install hugchat
```

```py
from hugchat import hugchat
chatbot = hugchat.ChatBot(cookie_path="cookies.json")  # 或者 cookies=[...]
print(chatbot.chat("Hello!"))

# 创建一个新的会话
id = chatbot.new_conversation()
chatbot.change_conversation(id)

# 获取会话列表
conversation_list = chatbot.get_conversation_list()
```

`chat()` 函数接收以下参数:

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

### 命令行交互

> `0.0.5.2` 或更高版本

使用以下命令启动命令行交互模式

```bash
python -m hugchat.cli
```

CLI模式中的命令：

- `/new` : 创建一个新的会话
- `/ids` : 查看会话列表
- `/switch <id>` : 切换到指定会话
- `/exit` : 退出CLI模式

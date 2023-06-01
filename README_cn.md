# hugging-chat-api

[English](README.md) | 简体中文

HuggingChat Python API

[![PyPi](https://img.shields.io/pypi/v/hugchat.svg)](https://pypi.python.org/pypi/hugchat)
[![Support_Platform](https://img.shields.io/pypi/pyversions/hugchat)](https://pypi.python.org/pypi/hugchat)
[![Downloads](https://static.pepy.tech/badge/hugchat)](https://pypi.python.org/pypi/hugchat)

给个星先😋

## 鉴权 (必需)

### 获取Cookies

```python
from hugchat import login

# 登录
sign = login(email, passwd)
cookies = sign.login()
sign.saveCookies()

# 从 usercookies/<email>.json 中加载已保存的cookies
sign = login(email, None)
cookies = sign.loadCookies() # 这个方法会查询保存cookies的文件是否存在，存在就返回cookies，不存在就报错

```

## 使用方式

### Python调用

```bash
pip install hugchat
```

```py
from hugchat import hugchat
from hugchat.login import Login

# 登入huggingface授权huggingchat
sign = login.Login(email, passwd)
cookies = sign.login()

# 保存cookies至 usercookies/<email>.json
sign.saveCookies()

# 创建一个 ChatBot
chatbot = hugchat.ChatBot(cookies=cookies.get_dict())  # or cookie_path="usercookies/<email>.json"
print(chatbot.chat("HI"))

# 创建一个新会话
id = chatbot.new_conversation()
chatbot.change_conversation(id)

# 获取对话列表
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
- `stop`: Optional[list]. Default is ["`</s>`"]
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

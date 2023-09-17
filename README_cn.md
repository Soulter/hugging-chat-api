# hugging-chat-api

[English](README.md) | 简体中文

为聊天机器人等程序打造的非官方的 HuggingChat Python API。

[![PyPi](https://img.shields.io/pypi/v/hugchat.svg)](https://pypi.python.org/pypi/hugchat)
[![Support_Platform](https://img.shields.io/pypi/pyversions/hugchat)](https://pypi.python.org/pypi/hugchat)
[![Downloads](https://static.pepy.tech/badge/hugchat)](https://pypi.python.org/pypi/hugchat)

> **Note**  
> 近期更新
> - 上下文记忆  
> - 支持更改所使用的模型，见[#56](https://github.com/Soulter/hugging-chat-api/issues/56) (v0.0.9)

## 安装

```bash
pip install hugchat
```
或
```bash
pip3 install hugchat
```

## 用法

### API


```py
from hugchat import hugchat
from hugchat.login import Login

# 登录到 huggingface 并为 huggingchat 授权
sign = Login(email, passwd)
cookies = sign.login()

# 保存 cookies 到本地目录
cookie_path_dir = "./cookies_snapshot"
sign.saveCookiesToDir(cookie_path_dir)

# 在启动程序时加载 cookies：
# sign = login(email, None)
# cookies = sign.loadCookiesFromDir(cookie_path_dir) # 此步骤将检查指定的文件是否存在，若存在则返回cookies，不存在则报错

# 创建 ChatBot 对象
chatbot = hugchat.ChatBot(cookies=cookies.get_dict())  # or cookie_path="usercookies/<email>.json"
print(chatbot.chat("Hi!"))

# 创建新的对话
id = chatbot.new_conversation()
chatbot.change_conversation(id)

# 获取对话列表
conversation_list = chatbot.get_conversation_list()

# 切换模型 (默认: meta-llama/Llama-2-70b-chat-hf. )
chatbot.switch_llm(0) # 切换到 `OpenAssistant/oasst-sft-6-llama-30b-xor`
chatbot.switch_llm(1) # 切换到 `meta-llama/Llama-2-70b-chat-hf`
```


`chat()` 函数接受以下参数:

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
- `retry_count`: Optional[int]. 重试次数. Default is 5

### CLI

> `version 0.0.5.2` or newer

直接在终端执行以下命令将进入 HugChat 的命令行交互模式：

```bash
python -m hugchat.cli
```

CLI模式中的命令：

- `/new` : 创建并切换到新的对话
- `/ids` : 输出当前会话(Session)中的所有对话ID编号和完整ID字符串
- `/switch <id>` : 通过对话ID切换到指定的对话
- `/del <id>` : 删除指定的对话，不会删除活动的对话
- `/clear` : 清除终端内容
- `/llm` : 获取可用的模型列表
- `/llm <index>` : 通过编号切换到 `/llm` 中可用的某个模型
- `/sharewithauthor <on|off>` : 设置是否与模型作者共享对话数据，默认启用
- `/exit`: 退出CLI环境

- AI是一个活跃的研究领域，存在一些已知问题，例如生成偏见和错误信息。请不要将此应用用于重大决策或咨询。
- 服务器资源宝贵，不建议高频率请求此API。
(`Hugging Face's CTO🤗`点赞了这个建议)
<div align="center"><img width=500 src="https://github.com/Soulter/hugging-chat-api/assets/37870767/06e64501-02fb-4d4a-ab6f-cf18d8638ace"></img></div>

## 声明

此仓库不是 [Hugging Face](https://huggingface.co/) 官方产品. 这是一个**个人项目**，与[Hugging Face](https://huggingface.co/)没有任何关联。请不要起诉我们。

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Soulter/hugging-chat-api&type=Date)](https://star-history.com/#Soulter/hugging-chat-api&Date)
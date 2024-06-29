# hugging-chat-api

[English](README.md) | 简体中文

为聊天机器人等程序打造的非官方的 HuggingChat Python API。

[![PyPi](https://img.shields.io/pypi/v/hugchat.svg?logo=pypi&logoColor=white)](https://pypi.python.org/pypi/hugchat)
[![Support_Platform](https://img.shields.io/badge/3.6+-%234ea94b.svg?logo=python&logoColor=white)](https://pypi.python.org/pypi/hugchat)
[![DownloadsPW](https://img.shields.io/pypi/dw/hugchat?logo=download&logoColor=white)](https://pypi.python.org/pypi/hugchat)
[![Status](https://img.shields.io/badge/status-operational-%234ea94b.svg?logo=ok&logoColor=white)](https://pypi.python.org/pypi/hugchat)
[![Downloads](https://static.pepy.tech/badge/hugchat?logo=download&logoColor=white)](https://www.pepy.tech/projects/hugchat)

> **Note**
>
> 某些较新的版本可能包含不向后兼容的更新，建议在出现问题时查看此 README 或 issues。 
>  
> 近期更新
> - 联网搜索
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

以下展示了本库的常见用法，您不一定需要全部使用，可以根据需要添加或删除一些 :)

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

# 非流式响应
query_result = chatbot.query("Hi!")
print(query_result)  # 纯文本为 query_result["text"]

# 流式响应
for resp in chatbot.query(
    "Hello",
    stream=True
):
    print(resp)

# 使用联网搜索功能
query_result = chatbot.query("Hi!", web_search=True)
print(query_result) # or query_result.text or query_result["text"]
for source in query_result.web_search_sources:
    print(source.link)
    print(source.title)
    print(source.hostname)

# 创建新的对话
id = chatbot.new_conversation()
chatbot.change_conversation(id)

# 获取对话列表
conversation_list = chatbot.get_conversation_list()

# 获取可用的模型列表
models = chatbot.get_available_llm_models()

# 切换模型
chatbot.switch_llm(0) # 切换到第一个模型
chatbot.switch_llm(1) # 切换到第二个模型

# 从服务器获取所有回话列表
chatbot.get_remote_conversations(replace_conversation_list=True)

# [慎用]删除所有回话
chatbot.delete_all_conversations()
```

`query()` 函数接受以下参数:

- `text`: Required[str].
- `retry_count`: 重试次数. Optional[int]. Default is 5
- `web_search` : 是否使用联网搜索. Optional[bool]

### CLI

> `version 0.0.5.2` or newer

直接在终端执行以下命令将进入 HugChat 的命令行交互模式：

```bash
python -m hugchat.cli
```

CLI模式接受启动参数：

- `-u <your huggingface email>` : 提供账户邮箱以登录。
- `-p` : 重新输入密码，忽略已保存的cookies。
- `-s` : 在CLI模式中启用流式输出。

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
- `/stream <on|off>`: 启用或关闭流式输出
- `/web <on|off>`: 启用或关闭联网搜索
- `/web-hint <on|off>`: 启用或关闭显示web搜索提示

- AI是一个活跃的研究领域，存在一些已知问题，例如生成偏见和错误信息。请不要将此应用用于重大决策或咨询。
- 服务器资源宝贵，不建议高频率请求此API。
(`Hugging Face's CTO🤗`点赞了这个建议)
<div align="center"><img width=500 src="https://github.com/Soulter/hugging-chat-api/assets/37870767/06e64501-02fb-4d4a-ab6f-cf18d8638ace"></img></div>

## 部署到 Hugging Face 免费服务器

要将此项目部署到 Hugging Face 的免费服务器，请按照以下步骤操作：

1. 确保您的项目与 Hugging Face 服务器环境兼容。这包括使用支持的 Python 版本和库。
2. 设置特定于 Hugging Face 服务器的环境变量。这包括认证令牌和任何其他必要的配置。
3. 使用 Hugging Face CLI 或 GitHub 集成来部署您的项目。详细说明可以在 Hugging Face 文档中找到。

注意：部署到 Hugging Face 的免费服务器可能有特定的限制或要求，例如资源使用限制。请参阅 Hugging Face 文档以获取更多信息。

## 声明

此仓库不是 [Hugging Face](https://huggingface.co/) 官方产品. 这是一个**个人项目**，与[Hugging Face](https://huggingface.co/)没有任何关联。请不要起诉我们。

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Soulter/hugging-chat-api&type=Date)](https://star-history.com/#Soulter/hugging-chat-api&Date)

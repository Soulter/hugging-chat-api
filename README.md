# hugging-chat-api
HuggingChat Python API

# How to Use?
```
pip install hugchat
```

```
from hugchat import hugchat
chatbot = hugchat.ChatBot()
print(chatbot.chat("HI"))

# New a conversation (ignore error)
id = chatbot.new_conversation()
chatbot.change_conversation(id)

# Get conversation list
conversation_list = chatbot.get_conversation_list()
```

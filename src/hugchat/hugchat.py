from requests import Session
import json
import uuid

class ChatBot:
    def __init__(self) -> None:
        self.hf_base_url = "https://huggingface.co"
        self.json_header = {"Content-Type": "application/json"}
        self.session = self.get_hc_session()
        self.conversation_id_list = []
        self.active_model = "OpenAssistant/oasst-sft-6-llama-30b-xor"
        self.accepted_welcome_modal = False # Only when accepted, it can create a new conversation.
        self.current_conversation = self.new_conversation()


    def get_hc_session(self) -> Session:
        session = Session()
        session.get(self.hf_base_url + "/chat")
        return session
    
    def get_headers(self, ref=True) -> dict:
        _h = {
            "Accept": "*/*",
            "Connection": "keep-alive",

            "Host": "huggingface.co",
            "Origin": "https://huggingface.co",
            "sec-gpc": "1",

            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",

            "Accept-Encoding": "gzip, deflate, br",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        }
        if ref:
            _h["Referer"] = f"https://huggingface.co/chat/conversation/{self.current_conversation}"
        return _h
    
    def get_cookies(self) -> dict:
        return self.session.cookies.get_dict()
    

    # NOTE: To create a copy when calling this, call it inside of list().
    #       If not, when updating or altering the values in the variable will
    #       also be applied to this class's variable.
    #       This behaviour is with any function returning self.<var_name>. It
    #       acts as a pointer to the data in the object.
    #
    # Returns a pointer to this objects list that contains id of conversations.
    def get_conversation_list(self) -> list:
        return list(self.conversation_id_list)

    def accept_ethics_modal(self):
        response = self.session.post(self.hf_base_url + "/chat/settings", headers=self.get_headers(ref=False), cookies=self.get_cookies(), allow_redirects=True, data={
            "ethicsModalAccepted": "true",
            "shareConversationsWithModelAuthors": "true",
            "ethicsModalAcceptedAt": "",
            "activeModel": str(self.active_model)
        })

        if response.status_code != 200:
            raise Exception(f"Failed to accept ethics modal with status code {response.status_code}. {response.content.decode()}")
        
        return True
    
    def new_conversation(self) -> str:
        err_count = 0

        # Accept the welcome modal when init.
        if not self.accepted_welcome_modal:
            self.accept_ethics_modal()

        # Create new conversation and get a conversation id.
        resp = ""
        while True:
            try:
                resp = self.session.post(self.hf_base_url + "/chat/conversation", json={"model": self.active_model}, headers=self.json_header)
                # print(resp.text)
                cid = json.loads(resp.text)['conversationId']
                self.conversation_id_list.append(cid)
                return cid
            
            except BaseException as e:
                err_count += 1
                print(f"[Error] Failed to create new conversation. Retrying... ({err_count})")
                if err_count > 5:
                    raise e
                continue
    
    def change_conversation(self, conversation_id: str) -> bool:
        if conversation_id not in self.conversation_id_list:
            raise Exception("Invalid conversation id. Please check conversation id list.")
        self.current_conversation = conversation_id
        return True
    
        
    def summarize_conversation(self, conversation_id: str = None) -> str:
        if conversation_id is None:
            conversation_id = self.current_conversation
        
        headers = self.get_headers()

        r = self.session.post(f"{self.hf_base_url}/chat/conversation/{conversation_id}/summarize", headers=headers, cookies=self.get_cookies())
        
        if r.status_code != 200:
            raise Exception(f"Failed to send chat message with status code: {r.status_code}")
        
        response = r.json()
        if 'title' in response:
            return response['title']

        raise Exception(f"Unknown server response: {response}")
    
    def share_conversation(self, conversation_id: str = None) -> str:
        if conversation_id is None:
            conversation_id = self.current_conversation

        headers = self.get_headers()
        
        r = self.session.post(f"{self.hf_base_url}/chat/conversation/{conversation_id}/share", headers=headers, cookies=self.get_cookies())
        
        if r.status_code != 200:
            raise Exception(f"Failed to send chat message with status code: {r.status_code}")
        
        response = r.json()
        if 'url' in response:
            return response['url']

        raise Exception(f"Unknown server response: {response}")

    def chat(
        self,
        text: str,
        temperature: float=0.9,
        top_p: float=0.95,
        repetition_penalty: float=1.2,
        top_k: int=50,
        truncate: int=1024,
        watermark: bool=False,
        max_new_tokens: int=1024,
        stop: list=["</s>"],
        return_full_text: bool=False,
        stream: bool=True,
        use_cache: bool=False,
        is_retry: bool=False,
        retry_count: int=5,
    ):
        if retry_count <= 0:
            raise Exception("the parameter retry_count must be greater than 0.")
        if self.current_conversation == "":
            self.current_conversation = self.new_conversation()
        req_json = {
            "inputs": text,
            "parameters": {
                "temperature": temperature,
                "top_p": top_p,
                "repetition_penalty": repetition_penalty,
                "top_k": top_k,
                "truncate": truncate,
                "watermark": watermark,
                "max_new_tokens": max_new_tokens,
                "stop": stop,
                "return_full_text": return_full_text,
                "stream": stream,
            },
            "options": {
                    "use_cache": use_cache,
                    "is_retry": is_retry,
                    "id": str(uuid.uuid4()),
            },
        }
        # print(req_json)
        # print(self.session.cookies.get_dict())
        # print(f"https://huggingface.co/chat/conversation/{self.now_conversation}")
        headers = self.get_headers(ref=True)

        while retry_count > 0:
            resp = self.session.post(self.hf_base_url + f"/chat/conversation/{self.current_conversation}", json=req_json, stream=True, headers=headers, cookies=self.session.cookies.get_dict())
            res_text = ""

            if resp.status_code != 200:
                retry_count -= 1
                if retry_count <= 0:
                    raise Exception(f"Failed to chat. ({resp.status_code})")

            for line in resp.iter_lines():
                if line:
                    res = line.decode("utf-8")
                    obj = json.loads(res[1:-1])
                    if "generated_text" in obj:
                        res_text += obj["generated_text"]
                    elif "error" in obj:
                        raise Exception(obj["error"])
            return res_text

def cli():
    print("-------HuggingChat-------")
    print("1. AI is an area of active research with known problems such as biased generation and misinformation. Do not use this application for high-stakes decisions or advice.\n2. Your conversations will be shared with model authors.\nContinuing to use means that you accept the above points")
    chatbot = ChatBot()
    running = True
    while running:
        question = input("> ")
        if question == "/new":
            cid = chatbot.new_conversation()
            print("The new conversation ID is: " + cid)
            chatbot.change_conversation(cid)
            print("Conversation changed successfully.")
            continue
        
        elif question.startswith("/switch"):
            try:
                conversations = chatbot.get_conversation_list()
                conversation_id = str(question.split(" ")[1] if len(question.split(" ")) > 1 else "")
                if conversation_id not in conversations:
                    print("# Please enter a valid ID number.")
                    print(f"# Sessions include: {conversations}")
                else:
                    chatbot.change_conversation(conversation_id)
                    print(f"# Conversation switched successfully to {conversation_id}")
            except ValueError:
                print("# Please enter a valid ID number\n")
            
            
        
        elif question == "/ids":
            id_list = list(chatbot.get_conversation_list())
            [print(f"{id_list.index(i)+1} : {i}{' <active>' if chatbot.current_conversation == i else ''}") for i in id_list]
        
        elif question in ["/exit", "/quit","/close"]:
            running = False
        
        elif question.startswith("/"):
            print("# Invalid command")
        
        elif question == "":
            pass

        else:
            res = chatbot.chat(question)
            print("< " + res)
    

if __name__ == "__main__":
    bot = ChatBot()
    message_content = bot.chat("Hello", max_new_tokens=10)
    print(message_content)
    summary = bot.summarize_conversation()
    print(summary)
    sharelink = bot.share_conversation()
    print(sharelink)

    cli()
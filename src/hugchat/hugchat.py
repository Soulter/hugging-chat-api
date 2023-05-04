from requests import Session
import json
import uuid

hf_url = "https://huggingface.co/chat"


class ChatBot:
    def __init__(self) -> None:
        self.session = self.get_hc_session()
        self.conversation_id_list = []
        self.current_conversation = self.new_conversation()

    def get_hc_session(self) -> Session:
        session = Session()
        session.get(hf_url)
        return session
    
    def change_conversation(self, conversation_id: str) -> bool:
        if conversation_id not in self.conversation_id_list:
            raise Exception("Invalid conversation id. Please check conversation id list.")
        self.current_conversation = conversation_id
        return True
    

    # NOTE: To create a copy when calling this, call it inside of list().
    #       If not, when updating or altering the values in the variable will
    #       also be applied to this class's variable.
    #       This behaviour is with any function returning self.<var_name>. It
    #       acts as a pointer to the data in the object.
    #
    # Returns a pointer to this objects list that contains id of conversations.
    def get_conversation_list(self) -> list:
        return list(self.conversation_id_list)
    
    def new_conversation(self) -> str:
        err_count = 0
        resp = ""
        while True:
            try:
                resp = self.session.post(hf_url + "/conversation", json={"model": "OpenAssistant/oasst-sft-6-llama-30b-xor"}, headers={"Content-Type": "application/json"})
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

    def get_cookies(self) -> dict:
        return self.session.cookies.get_dict()
        

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
        headers = {
            "Origin": "https://huggingface.co",
            "Referer": f"https://huggingface.co/chat/conversation/{self.current_conversation}",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.64",
            "Content-Type": "application/json",
            "Accept": "*/*",
        }

        while retry_count > 0:
            resp = self.session.post(hf_url + f"/conversation/{self.current_conversation}", json=req_json, stream=True, headers=headers, cookies=self.session.cookies.get_dict())
            res_text = ""
            if resp.status_code == 200:
                for line in resp.iter_lines():
                    if line:
                        res = line.decode("utf-8")
                        obj = json.loads(res[1:-1])
                        if "generated_text" in obj:
                            res_text += obj["generated_text"]
                        elif "error" in obj:
                            raise Exception(obj["error"])
                return res_text
            else:
                retry_count -= 1
                if retry_count <= 0:
                    raise Exception(f"Failed to chat. ({resp.status_code})")

def cli():
    chatbot = ChatBot()
    print("-------HuggingChat-------")
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
                _index = int(question.split(" ")[1])
            except ValueError:
                print("# Please enter a valid ID number\n")
            
            if len(chatbot.get_conversation_list()) < _index-1:
                print("# Please enter a valid ID number")
            else:
                chatbot.change_conversation(list(chatbot.get_conversation_list())[_index-1])
        
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
    cli()
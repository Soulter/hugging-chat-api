from requests import Session
import json

hf_url = "https://huggingface.co/chat"


class ChatBot:
    def __init__(self) -> None:
        self.session = self.get_hc_session()
        self.conversation_list = []
        self.now_conversation = self.new_conversation()

    def get_hc_session(self) -> Session:
        session = Session()
        session.get(hf_url)
        return session
    
    def change_conversation(self, conversation_id: str) -> bool:
        if conversation_id not in self.conversation_list:
            raise Exception("Invalid conversation id. Please check conversation id list.")
        self.now_conversation = conversation_id
        return True
    
    def get_conversation_list(self) -> list:
        return self.conversation_list
    
    def new_conversation(self) -> str:
        err_count = 0
        resp = ""
        while True:
            try:
                resp = self.session.post(hf_url + "/conversation")
                return json.loads(resp.text)['conversationId']
            except BaseException as e:
                err_count += 1
                print(f"[Error] Failed to create new conversation. Retrying... ({err_count})")
                if err_count > 5:
                    raise e
                continue
        

    def chat(self, text: str, temperature=0.9, top_p=0.95, repetition_penalty=1.2, top_k=50, truncate=1024) -> str:
        if self.now_conversation == "":
            self.now_conversation = self.new_conversation()
        req_json = {
            "inputs": text,
            "parameters": {
                "temperature": temperature,
                "top_p": top_p,
                "repetition_penalty": repetition_penalty,
                "top_k": top_k,
                "truncate": truncate,
                "watermark": False,
                "max_new_tokens": 1024,
                "stop": ["<|endoftext|>"],
                "return_full_text": False,
                "stream": True,
                "options": {"use_cache": False},
            }
        }
        resp = self.session.post(hf_url + f"/conversation/{self.now_conversation}", json=req_json, stream=True)
        
        if resp.status_code == 200:
            for line in resp.iter_lines():
                if line:
                    line = json.loads(line)
                    if "generated_text" in line:
                        self.conversation_list.append(line["generated_text"])
                        return line["generated_text"]
                    elif "error" in line:
                        raise Exception(line["error"])
    

if __name__ == "__main__":
    chatbot = ChatBot()
    chatbot.chat("Hello, I am a robot.")

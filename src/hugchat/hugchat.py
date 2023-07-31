from requests import Session
import requests
import json
import os
import uuid
import logging
import re
import getpass

from .exceptions import *

class ChatBot:
    
    cookies: dict
    """Cookies for authentication"""

    session: Session
    """HuggingChat session"""

    def __init__(
        self,
        cookies: dict = None,
        cookie_path: str = ""
    ) -> None:
        if cookies is None and cookie_path == "":
            raise ChatBotInitError("Authentication is required now, but no cookies provided. See tutorial at https://github.com/Soulter/hugging-chat-api")
        elif cookies is not None and cookie_path != "":
            raise ChatBotInitError("Both cookies and cookie_path provided")
        
        if cookies is None and cookie_path != "":
            # read cookies from path
            if not os.path.exists(cookie_path):
                raise ChatBotInitError(f"Cookie file {cookie_path} not found. Note: The file must be in JSON format and must contain a list of cookies. See more at https://github.com/Soulter/hugging-chat-api")
            with open(cookie_path, "r") as f:
                cookies = json.load(f)

        # convert cookies to KV format
        if isinstance(cookies, list):
            cookies = {cookie["name"]: cookie["value"] for cookie in cookies}

        self.cookies = cookies

        self.hf_base_url = "https://huggingface.co"
        self.json_header = {"Content-Type": "application/json"}
        self.session = self.get_hc_session()
        self.conversation_id_list = []
        self.active_model = "OpenAssistant/oasst-sft-6-llama-30b-xor"
        self.accepted_welcome_modal = False # Only when accepted, it can create a new conversation.
        self.current_conversation = self.new_conversation()


    def get_hc_session(self) -> Session:
        session = Session()
        # set cookies
        session.cookies.update(self.cookies)
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
        '''
        [Deprecated Method]
        '''
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
        '''
        Create a new conversation. Return the new conversation id. You should change the conversation by calling change_conversation() after calling this method.
        '''
        err_count = 0

        # Accept the welcome modal when init.
        # 17/5/2023: This is not required anymore.
        # if not self.accepted_welcome_modal:
        #     self.accept_ethics_modal()

        # Create new conversation and get a conversation id.
        resp = ""
        while True:
            try:
                resp = self.session.post(self.hf_base_url + "/chat/conversation", json={"model": self.active_model}, headers=self.json_header)
                # print(resp.text)
                logging.debug(resp.text)
                cid = json.loads(resp.text)['conversationId']
                self.conversation_id_list.append(cid)
                return cid
            
            except BaseException as e:
                err_count += 1
                logging.debug(f" Failed to create new conversation. Retrying... ({err_count})")
                if err_count > 5:
                    raise CreateConversationError(f"Failed to create new conversation. ({err_count})")
                continue
    
    def change_conversation(self, conversation_id: str) -> bool:
        '''
        Change the current conversation to another one. Need a valid conversation id.
        '''
        if conversation_id not in self.conversation_id_list:
            raise InvalidConversationIDError("Invalid conversation id, not in conversation list.")
        self.current_conversation = conversation_id
        return True
    
        
    def summarize_conversation(self, conversation_id: str = None) -> str:
        '''
        Return a summary of the conversation.
        '''
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
        '''
        Return a share link of the conversation.
        '''
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

    def delete_conversation(self, conversation_id: str = None) -> bool:
        '''
        Delete a HuggingChat conversation by conversation_id.
        '''

        if conversation_id is None:
            raise DeleteConversationError("conversation_id is required.")

        headers = self.get_headers()

        r = self.session.delete(f"{self.hf_base_url}/chat/conversation/{conversation_id}", headers=headers, cookies=self.get_cookies())

        if r.status_code != 200:
            raise DeleteConversationError(f"Failed to delete conversation with status code: {r.status_code}")
    
    
    # def get_available_llm_models() {
    #     '''
    #     Get all available models that exists in huggingface.co/chat.
    #     Returns a hard-code array. The array is up to date.
    #     '''
    #     return ['OpenAssistant/oasst-sft-6-llama-30b-xor', 'meta-llama/Llama-2-70b-chat-hf']
    # }

    def switch_llm(self, to: int) -> bool:
        '''
        Attempts to change current conversation's Large Language Model.
        Requires an index to indicate the model you want to switch.
        For now, 0 is `OpenAssistant/oasst-sft-6-llama-30b-xor`, 1 is `meta-llama/Llama-2-70b-chat-hf` :)
        
        * llm 1 is the latest LLM.
        * REMEMBER: For flexibility, the effect of switch just limited to *current conversation*. You can manually switch llm when you change a conversasion.
        '''

        llms = ['OpenAssistant/oasst-sft-6-llama-30b-xor', 'meta-llama/Llama-2-70b-chat-hf']

        mdl = ""
        if to == 0:
            mdl = "OpenAssistant/oasst-sft-6-llama-30b-xor",
        elif to == 1:
            mdl = "meta-llama/Llama-2-70b-chat-hf"
        else:
            raise BaseException("Can't switch llm, unexpected index. For now, 0 is `OpenAssistant/oasst-sft-6-llama-30b-xor`, 1 is `meta-llama/Llama-2-70b-chat-hf` :)")

        response = self.session.post(self.hf_base_url + "/chat/settings", headers=self.get_headers(ref=True), cookies=self.get_cookies(), allow_redirects=True, data={
            "shareConversationsWithModelAuthors": "true",
            "ethicsModalAcceptedAt": "",
            "searchEnabled": "true",
            "activeModel": mdl,
        })

        check = self.check_operation()
        if check:
            return True
        else:
            print(f"Switch LLM {llms[to]} failed. Please submit an issue to https://github.com/Soulter/hugging-chat-api")
            return False

    def check_operation(self) -> bool:
        r = self.session.post(self.hf_base_url + f"/chat/conversation/{self.current_conversation}/__data.json?x-sveltekit-invalidated=1_1", headers=self.get_headers(ref=True), cookies=self.get_cookies())
        return r.status_code == 200

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
        '''
        Send a message to the current conversation. Return the response text.
        '''
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
                    raise ChatError(f"Failed to chat. ({resp.status_code})")

            for line in resp.iter_lines():
                if line:
                    res = line.decode("utf-8")
                    try:
                        obj = json.loads(res[1:-1])
                    except:
                        if "{\"error\":\"Model is overloaded\"" in res:
                            raise ModelOverloadedError("Model is overloaded, please try again later.")
                        raise ChatError(f"Failed to parse response: {res}")
                    if "generated_text" in obj:
                        res_text += obj["generated_text"]
                    elif "error" in obj:
                        raise ChatError(obj["error"])
            return res_text


if __name__ == "__main__":
    bot = ChatBot()
    message_content = bot.chat("Hello", max_new_tokens=10)
    print(message_content)
    summary = bot.summarize_conversation()
    print(summary)
    sharelink = bot.share_conversation()
    print(sharelink)


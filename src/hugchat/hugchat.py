from requests import Session
import requests
import json
import os
import uuid
import logging
from typing import Union

from .exceptions import *

class ChatBot:
    
    cookies: dict
    """Cookies for authentication"""

    session: Session
    """HuggingChat session"""

    def __init__(
        self,
        cookies: dict = None,
        cookie_path: str = "",
        default_llm: Union[int, str] = 1,
    ) -> None:
        """
        default_llm: 
        0: `OpenAssistant/oasst-sft-6-llama-30b-xor`
        1: `meta-llama/Llama-2-70b-chat-hf`
        2: `codellama/CodeLlama-34b-Instruct-hf`
        3: `tiiuae/falcon-180B-chat`
        """
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
        self.__not_summarize_cids = []
        self.accepted_welcome_modal = False # Only when accepted, it can create a new conversation.
        self.switch_llm(default_llm)
        self.current_conversation = self.new_conversation()


    def get_hc_session(self) -> Session:
        session = Session()
        # set cookies
        session.cookies.update(self.cookies)
        session.get(self.hf_base_url + "/chat")
        return session
    
    def get_headers(self, ref=True, ref_cid = None) -> dict:
        _h = {
            "Accept": "*/*",
            "Connection": "keep-alive",
            "Host": "huggingface.co",
            "Origin": "https://huggingface.co",
            "Sec-Fetch-Site": "same-origin",
            "Content-Type": "application/json",
            "Sec-Ch-Ua-Platform": "Windows",
            "Sec-Ch-Ua": "Chromium\";v=\"116\", \"Not)A;Brand\";v=\"24\", \"Microsoft Edge\";v=\"116",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Accept-Encoding": "gzip, deflate, br",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        }
        if ref:
            if ref_cid is None:
                ref_cid = self.current_conversation
            _h["Referer"] = f"https://huggingface.co/chat/conversation/{ref_cid}"
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

        _header = self.get_headers(ref = False)
        _header['Referer'] = "https://huggingface.co/chat"

        resp = ""
        while True:
            try:
                resp = self.session.post(self.hf_base_url + "/chat/conversation", json={"model": self.active_model}, headers=_header, cookies = self.get_cookies())
                # print("new conversation")
                # print(resp.text)
                logging.debug(resp.text)
                cid = json.loads(resp.text)['conversationId']
                self.conversation_id_list.append(cid)
                self.__not_summarize_cids.append(cid) # For the 1st chat, the conversation needs to be summarized.
                self.__preserve_context(cid = cid, ending = "1_1")
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
        
        headers = self.get_headers(ref = True)
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
    
    
    def get_available_llm_models(self) -> list:
        '''
        Get all available models that exists in huggingface.co/chat.
        Returns a hard-code array. The array is up to date.
        '''
        return ['OpenAssistant/oasst-sft-6-llama-30b-xor',
                'meta-llama/Llama-2-70b-chat-hf', 
                'codellama/CodeLlama-34b-Instruct-hf', 
                'tiiuae/falcon-180B-chat']

    def set_share_conversations(self, val: bool = True):
        setting = {
            "ethicsModalAcceptedAt": "",
            "searchEnabled": "true",
            "activeModel": 'tiiuae/falcon-180B-chat',#'meta-llama/Llama-2-70b-chat-hf',
        }
        if val:
            setting['shareConversationsWithModelAuthors'] = 'on'

        self.session.post(self.hf_base_url + "/chat/settings", headers=self.get_headers(ref=True), cookies=self.get_cookies(), allow_redirects=True, data=setting)


    def switch_llm(self, to: Union[int, str]) -> bool:
        '''
        Attempts to change current conversation's Large Language Model.
        Requires an index to indicate the model you want to switch.
        0: `OpenAssistant/oasst-sft-6-llama-30b-xor`
        1: `meta-llama/Llama-2-70b-chat-hf`
        2: `codellama/CodeLlama-34b-Instruct-hf`
        3: `tiiuae/falcon-180B-chat`

        Note: 1. The effect of switch is limited to the current conversation,
        You can manually switch the llm when you start a new conversation.

        2. Only works *after creating a new conversation.*
        :)
        '''

        llms = ['OpenAssistant/oasst-sft-6-llama-30b-xor', 
                'meta-llama/Llama-2-70b-chat-hf', 
                'codellama/CodeLlama-34b-Instruct-hf', 
                'tiiuae/falcon-180B-chat']
        flag = True
        if isinstance(to, str):
            if to not in llms:
                flag = False
            else:
                to = llms.index(to)
        if to < 0 or to > len(llms):
            flag = False
        if not flag:
            raise BaseException("Can't switch llm, unexpected index. For now, 0 is `OpenAssistant/oasst-sft-6-llama-30b-xor`, 1 is `meta-llama/Llama-2-70b-chat-hf`, 2 is 'codellama/CodeLlama-34b-Instruct-hf', 3 is 'tiiuae/falcon-180B-chat':)")
        mdl = llms[to]
        self.active_model = mdl
        return True

        # response = self.session.post(self.hf_base_url + "/chat/settings", headers=self.get_headers(ref=True), cookies=self.get_cookies(), allow_redirects=True, data={
        #     "shareConversationsWithModelAuthors": "on",
        #     "ethicsModalAcceptedAt": "",
        #     "searchEnabled": "true",
        #     "activeModel": mdl,
        # })
        # check = self.check_operation()
        # if check:
        #     self.active_model = mdl
        #     return True
        # else:
        #     print(f"Switch LLM {llms[to]} failed. Please submit an issue to https://github.com/Soulter/hugging-chat-api")
        #     return False

    def check_operation(self) -> bool:
        r = self.session.post(self.hf_base_url + f"/chat/conversation/{self.current_conversation}/__data.json?x-sveltekit-invalidated=1_1", headers=self.get_headers(ref=True), cookies=self.get_cookies())
        return r.status_code == 200

    # def _web_search(self, prompt: str) -> bool:
    #     print("searching on web ...")
    #     r = self.session.get(self.hf_base_url + f"/chat/conversation/{self.current_conversation}/web-search?prompt={prompt}", headers=self.get_headers(ref=True), cookies=self.get_cookies(), timeout=300)
    #     print("done")
    #     return r.status_code == 200

    def chat(
        self,
        text: str,
        # web_search: bool=False,
        temperature: float=0.1,
        top_p: float=0.95,
        repetition_penalty: float=1.2,
        top_k: int=50,
        truncate: int=1000,
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
        You can customize these optional parameters.
        You can turn on the web search by set the parameter `web_search` to True
        '''
        
        if retry_count <= 0:
            raise Exception("the parameter retry_count must be greater than 0.")
        if self.current_conversation == "":
            self.current_conversation = self.new_conversation()
        if text == "":
            raise Exception("the prompt can not be empty.")

        # Invoke Web Search API
        # if web_search:
        #     res = self._web_search(text)
        #     if not res:
        #         print("Web search may failed.")

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
            "stream": True,
        }
        
        # if web_search:
        #     req_json["options"]["web_search_id"] = str(uuid.uuid4()).replace("-","")[0:24]
        # print(req_json)
        # print(self.session.cookies.get_dict())
        # print(f"https://huggingface.co/chat/conversation/{self.now_conversation}")
        headers = {
            "Origin": "https://huggingface.co",
            "Referer": f"https://huggingface.co/chat/conversation/{self.current_conversation}",
            "Content-Type": "application/json",
            "Sec-ch-ua": '"Chromium";v="94", "Microsoft Edge";v="94", ";Not A Brand";v="99"',
            "Sec-ch-ua-mobile": "?0",
            "Sec-ch-ua-platform": '"Windows"',
            "Accept": "*/*",
            "Accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        }

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
                        # print(f"line: {res}")
                        obj = json.loads(res[5:])
                    except:
                        if "Model is overloaded" in res:
                            raise ModelOverloadedError("Model is overloaded, please try again later or switch to another model.")
                        raise ChatError(f"Failed to parse response: {res}")
                    if "generated_text" in obj:
                        if obj["token"]["text"].endswith("</s>"):
                            res_text += obj["token"]["text"][:-5]
                        else:
                            res_text += obj["token"]["text"]
                    elif "error" in obj:
                        raise ChatError(obj["error"])
            # try to summarize the conversation and preserve the context.
            try:
                if self.current_conversation in self.__not_summarize_cids:
                    self.summarize_conversation()
                    self.__not_summarize_cids.remove(self.current_conversation)
                self.__preserve_context(ref_cid = self.current_conversation)
            except:
                pass

            return res_text.strip()

    def __preserve_context(self, cid: str = None, ending: str = "1_", ref_cid: str = ""):
        # print("preserve_context")
        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203",
            'Accept': "*/*",
        }
        if ref_cid == "":
            headers["Referer"] = "https://huggingface.co/chat"
        else:
            headers["Referer"] = f"https://huggingface.co/chat/conversation/{ref_cid}"
        # print(headers)
        cookie = {
            'hf-chat': self.get_cookies()['hf-chat'],
        }
        if cid is None:
            cid = self.current_conversation
        url = f"https://huggingface.co/chat/conversation/{cid}/__data.json?x-sveltekit-invalidated={ending}"
        response = self.session.get(url, cookies = cookie, headers = headers, data = {})
        if response.status_code == 200:
            return {'message': "Context Successfully Preserved", "status":200}
        else:
            return {'message': "Internal Error", "status": 500}


if __name__ == "__main__":
    bot = ChatBot()
    message_content = bot.chat("Hello", max_new_tokens=10)
    print(message_content)
    summary = bot.summarize_conversation()
    print(summary)
    sharelink = bot.share_conversation()
    print(sharelink)


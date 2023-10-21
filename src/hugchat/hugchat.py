from requests import Session
import requests
import json
import os
import uuid
import logging
import typing
import traceback
from typing import Union

from requests.sessions import RequestsCookieJar

from .message import Message
from .exceptions import *


class conversation:
    def __init__(
        self,
        id: str = None,
        title: str = None,
        model=None,
        system_prompt: str = None,
        history: list = [],
    ):
        """
        Returns a conversation object
        """

        self.id: str = id
        self.title: str = title
        self.model = model
        self.system_prompt: str = system_prompt
        self.history: list = history

    def __str__(self) -> str:
        return self.id


class model:
    def __init__(
        self,
        id: str = None,
        name: str = None,
        displayName: str = None,
        preprompt: str = None,
        promptExamples: list = None,
        websiteUrl: str = None,
        description: str = None,
        datasetName: str = None,
        datasetUrl: str = None,
        modelUrl: str = None,
        parameters: dict = None,
    ):
        """
        Returns a model object
        """

        self.id: str = id
        self.name: str = name
        self.displayName: str = displayName

        self.preprompt: str = preprompt
        self.promptExamples: list = promptExamples
        self.websiteUrl: str = websiteUrl
        self.description: str = description

        self.datasetName: str = datasetName
        self.datasetUrl: str = datasetUrl
        self.modelUrl: str = modelUrl
        self.parameters: dict = parameters

    def __str__(self) -> str:
        return self.id


class ChatBot:
    cookies: dict
    """Cookies for authentication"""

    session: Session
    """HuggingChat session"""

    def __init__(
        self,
        cookies: Union[dict, None, RequestsCookieJar] = None,
        cookie_path: str = "",
        default_llm: Union[int, str] = 0,
        system_prompt: str = "",
    ) -> None:
        """
        Returns a ChatBot object
        """
        if cookies is None and cookie_path == "":
            raise ChatBotInitError(
                "Authentication is required now, but no cookies provided. See tutorial at https://github.com/Soulter/hugging-chat-api"
            )
        elif cookies is not None and cookie_path != "":
            raise ChatBotInitError("Both cookies and cookie_path provided")

        if cookies is None and cookie_path != "":
            # read cookies from path
            if not os.path.exists(cookie_path):
                raise ChatBotInitError(
                    f"Cookie file {cookie_path} not found. Note: The file must be in JSON format and must contain a list of cookies. See more at https://github.com/Soulter/hugging-chat-api"
                )
            with open(cookie_path, "r", encoding="utf-8") as f:
                cookies = json.load(f)

        # convert cookies to KV format
        if isinstance(cookies, list):
            cookies = {cookie["name"]: cookie["value"] for cookie in cookies}

        self.cookies = cookies

        self.hf_base_url = "https://huggingface.co"
        self.json_header = {"Content-Type": "application/json"}
        self.session = self.get_hc_session()
        self.conversation_list = []
        self.__not_summarize_cids = []
        self.accepted_welcome_modal = (
            False  # It is no longer required to accept the welcome modal
        )

        self.llms = self.get_remote_llms()

        if type(default_llm) == str:
            self.active_model = self.get_llm_from_name(default_llm)
            if self.active_model is None:
                raise Exception(
                    f"Given model is not in llms list. LLM list: {[model.id for model in self.llms]}"
                )
        else:
            self.active_model = self.llms[default_llm]

        self.current_conversation = self.new_conversation(system_prompt=system_prompt)

    def get_hc_session(self) -> Session:
        session = Session()
        # set cookies
        session.cookies.update(self.cookies)
        session.get(self.hf_base_url + "/chat")
        return session

    def get_headers(self, ref=True, ref_cid: conversation = None) -> dict:
        _h = {
            "Accept": "*/*",
            "Connection": "keep-alive",
            "Host": "huggingface.co",
            "Origin": "https://huggingface.co",
            "Sec-Fetch-Site": "same-origin",
            "Content-Type": "application/json",
            "Sec-Ch-Ua-Platform": "Windows",
            "Sec-Ch-Ua": 'Chromium";v="116", "Not)A;Brand";v="24", "Microsoft Edge";v="116',
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
    #       This behavior is with any function returning self.<var_name>. It
    #       acts as a pointer to the data in the object.
    #
    # Returns a pointer to this objects list that contains id of conversations.
    def get_conversation_list(self) -> list:
        return list(self.conversation_list)

    def get_active_llm_index(self) -> int:
        return self.llms.index(self.active_model)

    def accept_ethics_modal(self):
        """
        [Deprecated Method]
        """
        response = self.session.post(
            self.hf_base_url + "/chat/settings",
            headers=self.get_headers(ref=False),
            cookies=self.get_cookies(),
            allow_redirects=True,
            data={
                "ethicsModalAccepted": "true",
                "shareConversationsWithModelAuthors": "true",
                "ethicsModalAcceptedAt": "",
                "activeModel": str(self.active_model),
            },
        )

        if response.status_code != 200:
            raise Exception(
                f"Failed to accept ethics modal with status code: {response.status_code}. {response.content.decode()}"
            )

        return True

    def new_conversation(
        self, modelIndex: int = None, system_prompt: str = "", switch_to: bool = False
    ) -> str:
        """
        Create a new conversation. Return the conversation object. You should change the conversation by calling change_conversation() after calling this method.
        """
        err_count = 0

        if modelIndex == None:
            model = self.active_model
        else:
            if modelIndex < 0 or modelIndex >= len(self.llms):
                raise IndexError("Out of range of llm index")

            model = self.llms[modelIndex]

        # Accept the welcome modal when init.
        # 17/5/2023: This is not required anymore.
        # if not self.accepted_welcome_modal:
        #     self.accept_ethics_modal()

        # Create new conversation and get a conversation id.

        _header = self.get_headers(ref=False)
        _header["Referer"] = "https://huggingface.co/chat"

        resp = ""
        while True:
            try:
                resp = self.session.post(
                    self.hf_base_url + "/chat/conversation",
                    json={
                        "model": model.id,
                        "preprompt": system_prompt
                        if system_prompt != ""
                        else model.preprompt,
                    },
                    headers=_header,
                    cookies=self.get_cookies(),
                )

                logging.debug(resp.text)
                cid = json.loads(resp.text)["conversationId"]

                c = conversation(id=cid, system_prompt=system_prompt, model=model)

                self.conversation_list.append(c)
                self.__not_summarize_cids.append(
                    cid
                )  # For the 1st chat, the conversation needs to be summarized.
                self.__preserve_context(cid=cid, ending="1_1")

                if switch_to:
                    self.change_conversation(c)

                return c

            except BaseException as e:
                err_count += 1
                logging.debug(
                    f" Failed to create new conversation. Retrying... ({err_count})"
                )
                if err_count > 5:
                    raise CreateConversationError(
                        f"Failed to create new conversation with status code: {resp.status_code}. ({err_count})"
                    )
                continue

    def change_conversation(self, conversation_object: conversation) -> bool:
        """
        Change the current conversation to another one. Need a valid conversation id.
        """

        for conversation in self.conversation_list:
            if conversation.id == conversation_object.id:
                self.current_conversation = conversation_object
                return True

        raise InvalidConversationIDError(
            "Invalid conversation id, not in conversation list."
        )

    def share_conversation(self, conversation_object: conversation = None) -> str:
        """
        Return a share link of the conversation.
        """
        if conversation_object is None:
            conversation_object = self.current_conversation

        headers = self.get_headers()

        r = self.session.post(
            f"{self.hf_base_url}/chat/conversation/{conversation_object}/share",
            headers=headers,
            cookies=self.get_cookies(),
        )

        if r.status_code != 200:
            raise Exception(
                f"Failed to share conversation with status code: {r.status_code}"
            )

        response = r.json()
        if "url" in response:
            return response["url"]

        raise Exception(f"Unknown server response: {response}")

    def delete_all_conversations(self) -> None:
        """
        Deletes ALL conversations on the HuggingFace account
        """

        settings = {"": ("", "")}

        r = self.session.post(
            f"{self.hf_base_url}/chat/conversations?/delete",
            headers={"Referer": "https://huggingface.co/chat"},
            cookies=self.get_cookies(),
            allow_redirects=True,
            files=settings,
        )

        if r.status_code != 200:
            raise DeleteConversationError(
                f"Failed to delete ALL conversations with status code: {r.status_code}"
            )

        self.conversation_list = []
        self.current_conversation = None

    def delete_conversation(self, conversation_object: conversation = None) -> None:
        """
        Delete a HuggingChat conversation by conversation.
        """

        if conversation_object is None:
            conversation_object = self.current_conversation

        headers = self.get_headers()

        r = self.session.delete(
            f"{self.hf_base_url}/chat/conversation/{conversation_object}",
            headers=headers,
            cookies=self.get_cookies(),
        )

        if r.status_code != 200:
            raise DeleteConversationError(
                f"Failed to delete conversation with status code: {r.status_code}"
            )
        else:
            self.conversation_list.pop(
                self.conversation_list.index(conversation_object)
            )

            if conversation_object is self.current_conversation:
                self.current_conversation = None

    def get_available_llm_models(self) -> list:
        """
        Get all available models that are available in huggingface.co/chat.
        """
        return self.llms

    def set_share_conversations(self, val: bool = True):
        """
        Sets the "Share Conversation with Model Authors setting" to the given val variable
        """
        settings = {"shareConversationsWithModelAuthors": ("", "on" if val else "")}

        r = self.session.post(
            self.hf_base_url + "/chat/settings",
            headers={"Referer": "https://huggingface.co/chat"},
            cookies=self.get_cookies(),
            allow_redirects=True,
            files=settings,
        )

        if r.status_code != 200:
            raise Exception(
                f"Failed to set share conversation with status code: {r.status_code}"
            )

    def switch_llm(self, index: int) -> bool:
        """
        Attempts to change current conversation's Large Language Model.
        Requires an index to indicate the model you want to switch.
        See self.llms for available models.

        Note: 1. The effect of switch is limited to the current conversation,
        You can manually switch the llm when you start a new conversation.

        2. Only works *after creating a new conversation.*
        :)
        """
        # TODO: I will work on making it have a model for each conversation that is changeable. - @Zekaroni

        if index < len(self.llms) and index >= 0:
            self.active_model = self.llms[index]
            return True
        else:
            raise IndexError("Out of range of llm index")

        # flag = True
        # if isinstance(to, str):
        #     if to not in self.llms:
        #         flag = False
        #     else:
        #         to = self.llms.index(to)
        # if to < 0 or to > len(self.llms):
        #     flag = False
        # if not flag:
        #     raise BaseException("Can't switch llm, unexpected index. For now, 0 is `meta-llama/Llama-2-70b-chat-hf`, 1 is `OpenAssistant/oasst-sft-6-llama-30b-xor`, 2 is 'codellama/CodeLlama-34b-Instruct-hf', 3 is 'tiiuae/falcon-180B-chat':)")
        # self.active_model = to
        # return True

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

    def get_llm_from_name(self, name: str) -> Union[model, None]:
        for model in self.llms:
            if model.name == name:
                return model

    # Gives information such as name, websiteUrl, description, displayName, parameters, etc.
    # We can use it in the future if we need to get information about models
    def get_remote_llms(self) -> list:
        """
        Fetches all possible LLMs that could be used. Returns the LLMs in a list
        """

        r = self.session.post(
            self.hf_base_url + f"/chat/__data.json",
            headers=self.get_headers(ref=False),
            cookies=self.get_cookies(),
        )

        if r.status_code != 200:
            raise Exception(
                f"Failed to get remote LLMs with status code: {r.status_code}"
            )

        data = r.json()["nodes"][0]["data"]
        modelsIndices = data[data[0]["models"]]
        model_list = []

        return_data_from_index = lambda index: None if index == -1 else data[index]

        for modelIndex in modelsIndices:
            model_data = data[modelIndex]

            m = model(
                id=return_data_from_index(model_data["id"]),
                name=return_data_from_index(model_data["name"]),
                displayName=return_data_from_index(model_data["displayName"]),
                preprompt=return_data_from_index(model_data["preprompt"]),
                # promptExamples = return_data_from_index(model_data["promptExamples"]),
                websiteUrl=return_data_from_index(model_data["websiteUrl"]),
                description=return_data_from_index(model_data["description"]),
                datasetName=return_data_from_index(model_data["datasetName"]),
                datasetUrl=return_data_from_index(model_data["datasetUrl"]),
                modelUrl=return_data_from_index(model_data["modelUrl"]),
                # parameters = return_data_from_index(model_data["parameters"]),
            )

            prompt_list = return_data_from_index(model_data["promptExamples"])
            if prompt_list is not None:
                _promptExamples = [
                    return_data_from_index(index) for index in prompt_list
                ]
                m.promptExamples = [
                    {"title": data[prompt["title"]], "prompt": data[prompt["prompt"]]}
                    for prompt in _promptExamples
                ]

            indices_parameters_dict = return_data_from_index(model_data["parameters"])
            out_parameters_dict = {}
            for key in indices_parameters_dict.keys():
                value = indices_parameters_dict[key]

                if value == -1:
                    out_parameters_dict[key] = None
                    continue

                if type(data[value]) == list:
                    out_parameters_dict[key] = [data[index] for index in data[value]]
                    continue

                out_parameters_dict[key] = data[value]

            m.parameters = out_parameters_dict

            model_list.append(m)

        return model_list

    def get_remote_conversations(self, replace_conversation_list=True):
        """
        Returns all the remote conversations for the active account. Returns the conversations in a list.
        """

        r = self.session.post(
            self.hf_base_url + f"/chat/__data.json",
            headers=self.get_headers(ref=False),
            cookies=self.get_cookies(),
        )

        if r.status_code != 200:
            raise Exception(
                f"Failed to get remote conversations with status code: {r.status_code}"
            )

        data = r.json()["nodes"][0]["data"]
        conversationIndices = data[data[0]["conversations"]]
        conversations = []

        for index in conversationIndices:
            conversation_data = data[index]
            c = conversation(
                id=data[conversation_data["id"]],
                title=data[conversation_data["title"]],
                model=data[conversation_data["model"]],
            )

            conversations.append(c)

        if replace_conversation_list:
            self.conversation_list = conversations

        return conversations

    def get_conversation_info(self, conversation: conversation = None):
        """
        Fetches information related to the specified conversation. Returns the conversation object.
        """

        if conversation is None:
            conversation = self.current_conversation

        r = self.session.post(
            self.hf_base_url + f"/chat/conversation/{conversation.id}/__data.json",
            headers=self.get_headers(ref=False),
            cookies=self.get_cookies(),
        )

        if r.status_code != 200:
            raise Exception(
                f"Failed to get conversation from id with status code: {r.status_code}"
            )

        data = r.json()["nodes"][1]["data"]

        conversation.model = data[data[0]["model"]]
        conversation.system_prompt = data[data[0]["preprompt"]]
        conversation.title = data[data[0]["title"]]

        messages = data[data[0]["messages"]]
        conversation.history = []

        for index in messages:
            message = data[data[index]["content"]].strip()

            conversation.history.append(message)

        return conversation

    def get_conversation_from_id(self, conversation_id: str) -> conversation:
        """
        Returns a conversation object from the given conversation_id.
        """

        c = conversation(id=conversation_id)

        return self.get_conversation_info(c)

    def check_operation(self) -> bool:
        r = self.session.post(
            self.hf_base_url
            + f"/chat/conversation/{self.current_conversation}/__data.json?x-sveltekit-invalidated=1_1",
            headers=self.get_headers(ref=True),
            cookies=self.get_cookies(),
        )
        return r.status_code == 200

    def _stream_query(
        self,
        text: str,
        web_search: bool = False,
        temperature: float = 0.1,
        top_p: float = 0.95,
        repetition_penalty: float = 1.2,
        top_k: int = 50,
        truncate: int = 1000,
        watermark: bool = False,
        max_new_tokens: int = 1024,
        stop: list = ["</s>"],
        return_full_text: bool = False,
        use_cache: bool = False,
        is_retry: bool = False,
        retry_count: int = 5,
        _stream_yield_all: bool = False,  # yield all responses from the server.
        conversation: conversation = None,
    ) -> typing.Generator[dict, None, None]:
        if conversation is None:
            conversation = self.current_conversation

        if retry_count <= 0:
            raise Exception("the parameter retry_count must be greater than 0.")
        if text == "":
            raise Exception("the prompt can not be empty.")

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
                "stream": True,
            },
            "options": {
                "use_cache": use_cache,
                "is_retry": is_retry,
                "id": str(uuid.uuid4()),
            },
            "stream": True,
            "web_search": web_search,
        }
        headers = {
            "Origin": "https://huggingface.co",
            "Referer": f"https://huggingface.co/chat/conversation/{conversation}",
            "Content-Type": "application/json",
            "Sec-ch-ua": '"Chromium";v="94", "Microsoft Edge";v="94", ";Not A Brand";v="99"',
            "Sec-ch-ua-mobile": "?0",
            "Sec-ch-ua-platform": '"Windows"',
            "Accept": "*/*",
            "Accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        }
        last_obj = {}

        break_label = False

        while retry_count > 0:
            resp = self.session.post(
                self.hf_base_url + f"/chat/conversation/{conversation}",
                json=req_json,
                stream=True,
                headers=headers,
                cookies=self.session.cookies.get_dict(),
            )

            if resp.status_code != 200:
                retry_count -= 1
                if retry_count <= 0:
                    raise ChatError(f"Failed to chat. ({resp.status_code})")

            try:
                for line in resp.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    res = line
                    obj = json.loads(res)
                    if obj.__contains__("type"):
                        _type = obj["type"]

                        if _type == "finalAnswer":
                            last_obj = obj
                            break_label = True
                            break
                    else:
                        logging.error(f"No `type` found in response: {obj}")
                    yield obj
                    # if _stream_yield_all:
                    # else:
                    #     if _type == "status":
                    #         continue
                    #     elif _type == "stream":
                    #         yield obj
                    #     elif _type == "finalAnswer":
                    #         last_obj = obj
                    #         break_label = True
                    #         break
                    #     elif _type == "webSearch":
                    #         continue
                    #     elif "error" in obj:
                    #         raise ChatError(obj["error"])
                    #     else:
                    #         raise ChatError(obj)
            except requests.exceptions.ChunkedEncodingError:
                pass
            except BaseException as e:
                traceback.print_exc()
                if "Model is overloaded" in str(e):
                    raise ModelOverloadedError(
                        "Model is overloaded, please try again later or switch to another model."
                    )
                logging.debug(resp.headers)
                raise ChatError(f"Failed to parse response: {res}")
            if break_label:
                break

        try:
            # if self.current_conversation in self.__not_summarize_cids:
            #     self.summarize_conversation()
            #     self.__not_summarize_cids.remove(self.current_conversation)
            self.__preserve_context(ref_cid=conversation.id)
        except:
            pass

        yield last_obj

    def query(
        self,
        text: str,
        web_search: bool = False,
        temperature: float = 0.1,
        top_p: float = 0.95,
        repetition_penalty: float = 1.2,
        top_k: int = 50,
        truncate: int = 1000,
        watermark: bool = False,
        max_new_tokens: int = 1024,
        stop: list = ["</s>"],
        return_full_text: bool = False,
        stream: bool = False,
        _stream_yield_all: bool = False,  # For stream mode, yield all responses from the server.
        use_cache: bool = False,
        is_retry: bool = False,
        retry_count: int = 5,
        conversation: conversation = None,
    ) -> Message:
        """
        **Deprecated**
        Same as chat now
        """
        if conversation is None:
            conversation = self.current_conversation

        return self.chat(
            text=text,
            web_search=web_search,
            _stream_yield_all=_stream_yield_all,
            retry_count=retry_count,
            conversation=conversation,
        )

    def chat(
        self,
        text: str,
        web_search: bool = False,
        _stream_yield_all: bool = False,  # For stream mode, yield all responses from the server.
        retry_count: int = 5,
        conversation: conversation = None,
        *args,
        **kvargs,
    ) -> Message:
        """
        Send a message to the current conversation. Return a Message object.
        You can customize these optional parameters (**Deprecated**).
        You can turn on the web search by set the parameter `web_search` to True

        Stream is now the default mode, you can call Message.wait_until_done()

        About class `Message`:
        - `wait_until_done()`: Block until the response done processing or an error raised.
        - `__iter__()`: For loop call this Generator and get response.
        - `get_search_sources()`: The web search results. It is a list of WebSearchSource objects.

        For more detail please see Message documentation(Message.__doc__)
        """
        if conversation is None:
            conversation = self.current_conversation

        msg = Message(
            g=self._stream_query(
                text=text,
                web_search=web_search,
                _stream_yield_all=_stream_yield_all,  # For stream mode, yield all responses from the server.
                retry_count=retry_count,
                conversation=conversation,
            ),
            _stream_yield_all=_stream_yield_all,
            web_search=web_search,
        )
        return msg

    def __preserve_context(
        self, cid: str = None, ending: str = "1_", ref_cid: str = ""
    ) -> bool:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203",
            "Accept": "*/*",
        }
        if ref_cid == "":
            headers["Referer"] = "https://huggingface.co/chat"
        else:
            headers["Referer"] = f"https://huggingface.co/chat/conversation/{ref_cid}"
        # print(headers)
        cookie = {
            "hf-chat": self.get_cookies()["hf-chat"],
        }
        if cid is None:
            cid = self.current_conversation
        url = f"https://huggingface.co/chat/conversation/{cid}/__data.json?x-sveltekit-invalidated={ending}"
        response = self.session.get(url, cookies=cookie, headers=headers, data={})
        return response.status_code == 200


if __name__ == "__main__":
    bot = ChatBot()
    message_content = bot.chat("Hello")
    print(message_content)
    sharelink = bot.share_conversation()
    print(sharelink)

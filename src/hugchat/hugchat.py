import requests
import json
import os
import datetime
import logging
import typing
import traceback

from typing import Union, List
from requests import Session
from requests.sessions import RequestsCookieJar

from .message import Message
from . import exceptions
from .types.assistant import Assistant
from .types.model import Model
from .types.message import MessageNode, Conversation


conversation = Conversation
model = Model


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
        default_llm: name or index
        """
        if cookies is None and cookie_path == "":
            raise exceptions.ChatBotInitError(
                "Authentication is required now, but no cookies provided. See tutorial at https://github.com/Soulter/hugging-chat-api"
            )
        elif cookies is not None and cookie_path != "":
            raise exceptions.ChatBotInitError(
                "Both cookies and cookie_path provided")

        if cookies is None and cookie_path != "":
            # read cookies from path
            if not os.path.exists(cookie_path):
                raise exceptions.ChatBotInitError(
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
        self.sharing = True
        self.accepted_welcome_modal = (
            False  # It is no longer required to accept the welcome modal
        )

        self.llms = self.get_remote_llms()

        if isinstance(default_llm, str):
            self.active_model = self.get_llm_from_name(default_llm)
            if self.active_model is None:
                raise Exception(
                    f"Given model is not in llms list. LLM list: {[model.id for model in self.llms]}"
                )
        else:
            self.active_model = self.llms[default_llm]

        self.current_conversation = self.new_conversation(
            system_prompt=system_prompt)

    def get_hc_session(self) -> Session:
        session = Session()
        # set cookies
        session.cookies.update(self.cookies)
        session.get(self.hf_base_url + "/chat")
        return session

    def get_headers(self, ref=True, ref_cid: Conversation = None) -> dict:
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
        self,
        modelIndex: int = None,
        system_prompt: str = "",
        switch_to: bool = False,
        assistant: Union[str, Assistant] = None,
    ) -> Conversation:
        """
        Create a new conversation. Return a conversation object. 

        modelIndex: int, get it from get_available_llm_models(). If None, use the default model.
        assistant: str or Assistant, the assistant **id** or assistant object. Use search_assistant() to get the assistant object.

        - You should change the conversation by calling change_conversation() after calling this method. Or set param switch_to to True.
        - if you use assistant, the parameter `system_prompt` will be ignored.

        """
        err_count = 0

        if modelIndex is None:
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

        request = {
            "model": model.id,
        }

        # get assistant id
        if assistant is not None:
            assistant_id = None
            if isinstance(assistant, str):
                assistant_id = assistant
            elif isinstance(assistant, Assistant):
                assistant_id = assistant.assistant_id
            else:
                raise ValueError(
                    "param assistant must be a string or Assistant object.")
            request["assistantId"] = assistant_id
        else:
            request["preprompt"] = system_prompt if system_prompt != "" else model.preprompt

        while True:
            try:
                resp = self.session.post(
                    self.hf_base_url + "/chat/conversation",
                    json=request,
                    headers=_header,
                    cookies=self.get_cookies(),
                )

                logging.debug(resp.text)
                cid = json.loads(resp.text)["conversationId"]

                c = Conversation(
                    id=cid, system_prompt=system_prompt, model=model)

                self.conversation_list.append(c)
                if switch_to:
                    self.change_conversation(c)

                # we need know the root message id (a.k.a system prompt message id).
                self.get_conversation_info(c)

                return c

            except BaseException as e:
                err_count += 1
                logging.debug(
                    f" Failed to create new conversation ({e}). Retrying... ({err_count})"
                )
                if err_count > 5:
                    raise exceptions.CreateConversationError(
                        f"Failed to create new conversation with status code: {resp.status_code}. Error: {e}. Retries: {err_count}."
                    )
                continue

    def change_conversation(self, conversation_object: Conversation):
        """
        Change the current conversation to another one.
        """

        local_conversation = self.get_conversation_from_id(
            conversation_object.id)

        if local_conversation is None:
            raise exceptions.InvalidConversationIDError(
                "Invalid conversation id, not in conversation list."
            )

        self.get_conversation_info(local_conversation)

        self.current_conversation = local_conversation
        
        return self.current_conversation

    def share_conversation(self, conversation_object: Conversation = None) -> str:
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
            headers={"Referer": "https://huggingface.co/chat", "Origin": "https://huggingface.co", "Content-Type": "multipart/form-data; boundary=----WebKitFormBoundarywrIEW0Ame78HYisT"},
            cookies=self.get_cookies(),
            allow_redirects=True,
            files=settings,
        )

        if r.status_code != 200:
            raise exceptions.DeleteConversationError(
                f"Failed to delete ALL conversations with status code: {r.status_code}"
            )

        self.conversation_list = []
        self.current_conversation = None

    def delete_conversation(self, conversation_object: Conversation = None) -> None:
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
            raise exceptions.DeleteConversationError(
                f"Failed to delete conversation with status code: {r.status_code}"
            )
        else:
            self.conversation_list.pop(
                self.get_conversation_from_id(
                    conversation_object.id, return_index=True)
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
        settings = {"shareConversationsWithModelAuthors": (
            "", "on" if val else "")}

        r = self.session.post(
            self.hf_base_url + "/chat/settings",
            headers={"Referer": "https://huggingface.co/chat", "Origin":"https://huggingface.co"},
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

    def get_llm_from_name(self, name: str) -> Union[Model, None]:
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
            self.hf_base_url + "/chat/__data.json",
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

        def return_data_from_index(
            index): return None if index == -1 else data[index]

        for modelIndex in modelsIndices:
            model_data = data[modelIndex]

            # Model is unlisted, skip it
            if data[model_data["unlisted"]]:
                continue

            m = Model(
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
                    {"title": data[prompt["title"]],
                        "prompt": data[prompt["prompt"]]}
                    for prompt in _promptExamples
                ]

            indices_parameters_dict = return_data_from_index(
                model_data["parameters"])
            out_parameters_dict = {}
            for key, value in indices_parameters_dict.items():
                if value == -1:
                    out_parameters_dict[key] = None
                    continue

                if isinstance(type(data[value]), list):
                    out_parameters_dict[key] = [data[index]
                                                for index in data[value]]
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
            self.hf_base_url + "/chat/__data.json",
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
            c = Conversation(
                id=data[conversation_data["id"]],
                title=data[conversation_data["title"]],
                model=data[conversation_data["model"]],
            )

            conversations.append(c)

        if replace_conversation_list:
            self.conversation_list = conversations

        return conversations

    def get_conversation_info(self, conversation: Union[Conversation, str] = None) -> Conversation:
        """
        Fetches information related to the specified conversation. Returns the conversation object.
        conversation: Conversation object that has the conversation id Or None to use the current conversation.
        """

        if conversation is None:
            conversation = self.current_conversation

        if isinstance(conversation, str):
            conversation = Conversation(id=conversation)

        r = self.session.get(
            self.hf_base_url +
            f"/chat/conversation/{conversation.id}/__data.json?x-sveltekit-invalidated=01",
            headers=self.get_headers(ref=False),
            cookies=self.get_cookies(),
        )

        if r.status_code != 200:
            raise Exception(
                f"Failed to get conversation info with status code: {r.status_code}"
            )
            
        # you'll never understand the following codes until you try to debug huggingchat in person.
        data = r.json()["nodes"][1]["data"]

        conversation.model = data[data[0]["model"]]
        conversation.system_prompt = data[data[0]["preprompt"]]
        conversation.title = data[data[0]["title"]]

        messages: list = data[data[0]["messages"]]
        conversation.history = []

        # parse all message nodes (history) in the conversation
        for index in messages:  # node's index
            _node_meta = data[index]
            # created_at and updated_at may not in the metadata of a message node.
            created_at = datetime.datetime.strptime(
                    data[_node_meta["createdAt"]][1], "%Y-%m-%dT%H:%M:%S.%fZ").timestamp() if 'createdAt' in _node_meta else None
            updated_at = datetime.datetime.strptime(
                    data[_node_meta["updatedAt"]][1], "%Y-%m-%dT%H:%M:%S.%fZ").timestamp() if 'updatedAt' in _node_meta else None
            ancestors = []
            children = []
            for a_idx in data[_node_meta["ancestors"]]:
                ancestors.append(data[a_idx])
            for c_idx in data[_node_meta["children"]]:
                children.append(data[c_idx])
            conversation.history.append(MessageNode(
                id=data[_node_meta["id"]],
                role=data[_node_meta["from"]],
                content=data[_node_meta["content"]],
                ancestors=ancestors,
                children=children,
                created_at=created_at,
                updated_at=updated_at,
            ))

        logging.debug(
            f"conversation {conversation.id} history: {conversation.history}")

        return conversation

    def get_conversation_from_id(self, conversation_id: str, return_index=False) -> Conversation:
        """
        Returns a conversation object that is already in the conversation list.
        """

        for i, conversation in enumerate(self.conversation_list):
            if conversation.id == conversation_id:
                if return_index:
                    return i
                return conversation

    def _parse_assistants(self, nodes_data: list) -> List[Assistant]:
        '''
        parse the assistants data from the response.
        '''
        index = nodes_data[1]
        ret = []
        for i in index:
            attribute_map: dict = nodes_data[i]
            assistant_id = nodes_data[attribute_map['_id']]
            author = nodes_data[attribute_map['createdByName']]
            name = nodes_data[attribute_map['name']].strip()
            model_name = nodes_data[attribute_map['modelId']]
            pre_prompt = nodes_data[attribute_map['preprompt']]
            description = nodes_data[attribute_map['description']]
            ret.append(Assistant(
                assistant_id,
                author,
                name,
                model_name,
                pre_prompt,
                description
            ))
        return ret

    def get_assistant_list_by_page(self, page: int) -> List[Assistant]:
        '''
        get assistant list by page number.
        if page < 0 or page > max_page then return `None`.
        '''
        url_cache = f"https://api.soulter.top/hugchat/assistants/__data.json?p={page}"
        url = f"https://huggingface.co/chat/assistants/__data.json?p={page}&x-sveltekit-invalidated=01"
        try:
            res = requests.get(url_cache, timeout=5)
        except BaseException:
            res = self.session.get(url, timeout=10)
        res = res.json()
        if res['nodes'][1]['type'] == 'error':
            return None
        # here we parse the result
        return self._parse_assistants(res['nodes'][1]['data'])

    def search_assistant(self, assistant_name: str = None, assistant_id: str = None) -> Assistant:
        '''
        - If you created an assistant by your own, you should pass the assistant_id here but not the assistant_name. You can pass your assistant_id into the new_conversation() directly.
        - Search an available assistant by assistant name or assistant id.
        - Will search on api.soulter.top/hugchat because offifial api doesn't support search.
        - Return the `Assistant` object if found, return None if not found.
        '''
        if not assistant_name and not assistant_id:
            raise ValueError(
                "assistant_name and assistant_id can not be both None.")
        if assistant_name:
            url = f"https://api.soulter.top/hugchat/assistant?name={assistant_name}"
        else:
            url = f"https://api.soulter.top/hugchat/assistant?id={assistant_id}"
        res = requests.get(url, timeout=10)
        if res.status_code != 200:
            raise Exception(
                f"Failed to search assistant with status code: {res.status_code}, please commit an issue to https://github.com/Soulter/hugging-chat-api/issues")
        res = res.json()
        if not res['data']:
            # empty dict
            return None
        if res['code'] != 0:
            raise Exception(
                f"Failed to search assistant with server's error: {res['message']}, please commit an issue to https://github.com/Soulter/hugging-chat-api/issues")
        return Assistant(**res['data'])

    def _stream_query(
        self,
        text: str,
        web_search: bool = False,
        is_retry: bool = False,
        retry_count: int = 5,
        conversation: Conversation = None,
        message_id: str = None,
    ) -> typing.Generator[dict, None, None]:
        if conversation is None:
            conversation = self.current_conversation

        if retry_count <= 0:
            raise Exception(
                "the parameter retry_count must be greater than 0.")
        if len(conversation.history) == 0:
            raise Exception(
                "conversation history is empty, but we need the root message id of this conversation to continue.")
            
        if not message_id:
            # get last message id
            message_id = conversation.history[-1].id
            
        logging.debug(f'message_id: {message_id}')

        req_json = {
            "id": message_id,
            "inputs": text,
            "is_continue": False,
            "is_retry": is_retry,
            "web_search": web_search,
            "tools": []
        }
        headers = {
            'authority': 'huggingface.co',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,en-GB;q=0.6',
            'origin': 'https://huggingface.co',
            'sec-ch-ua': '"Microsoft Edge";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
        }
        final_answer = {}

        break_flag = False

        while retry_count > 0:
            resp = self.session.post(
                self.hf_base_url + f"/chat/conversation/{conversation}",
                files={ "data": (None, json.dumps(req_json)) },
                stream=True,
                headers=headers,
                cookies=self.session.cookies.get_dict(),
            )
            resp.encoding = 'utf-8'

            if resp.status_code != 200:
                
                retry_count -= 1
                if retry_count <= 0:
                    raise exceptions.ChatError(
                        f"Failed to chat. ({resp.status_code})")

            try:
                for line in resp.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    res = line
                    obj = json.loads(res)
                    if obj.__contains__("type"):
                        _type = obj["type"]

                        if _type == "finalAnswer":
                            final_answer = obj
                            break_flag = True
                            break
                    else:
                        logging.error(f"No `type` found in response: {obj}")
                    yield obj
            except requests.exceptions.ChunkedEncodingError:
                pass
            except BaseException as e:
                traceback.print_exc()
                if "Model is overloaded" in str(e):
                    raise exceptions.ModelOverloadedError(
                        "Model is overloaded, please try again later or switch to another model."
                    )
                logging.debug(resp.headers)
                if "Conversation not found" in str(res):
                    raise exceptions.InvalidConversationIDError("Conversation id invalid")
                raise exceptions.ChatError(f"Failed to parse response: {res}")
            if break_flag:
                break

        # update the history of current conversation
        self.get_conversation_info(conversation)
        yield final_answer

    def query(self) -> Message:
        """
        **Deprecated**
        Please use `chat()`. The function will raise an error immediately.
        """
        raise Exception("The function is deprecated. Please use `chat()`")
    
    def get_message_node(self, conversation: Conversation, message_id: str):
        for node in conversation.history:
            if node.id == message_id:
                return node
        raise Exception(f"no node found which id is {message_id}")

    def chat(
        self,
        text: str,
        web_search: bool = False,
        # For stream mode, yield all responses from the server.
        _stream_yield_all: bool = False,
        retry_count: int = 5,
        conversation: Conversation = None,
        edit_user_node: MessageNode = None,
        *args,
        **kvargs,
    ) -> Message:
        """
        - Send a message to the current conversation. Return a Message object.

        - You can turn on the web search by set the parameter `web_search` to True.

        - Stream is now the default mode, you can call Message.wait_until_done() to get the result text.
        
        - `Edit history`: pass `edit_user_node`. The history can be retrieved from `conversation.history`. 

        - About class `Message`:
            - `wait_until_done()`: Block until the response done processing or an error raised.
            - `__iter__()`: For loop call this Generator and get response.
            - `get_search_sources()`: The web search results. It is a list of WebSearchSource objects.

        - For more detail please see Message documentation(Message.__doc__)
        """
        if conversation is None:
            conversation = self.current_conversation
        
        if not text:
            raise Exception("don't support an empty string(I'm sure LLM cannot understand it)")
        if edit_user_node and edit_user_node.role != 'user':
            raise Exception("you must pass a user's message node to edit message")

        is_retry = True if edit_user_node else False
        edit_message_id = edit_user_node.id if is_retry else None

        msg = Message(
            g=self._stream_query(
                text=text,
                web_search=web_search,
                retry_count=retry_count,
                conversation=conversation,
                is_retry=is_retry,
                message_id=edit_message_id
            ),
            _stream_yield_all=_stream_yield_all,
            web_search=web_search,
            conversation=conversation
        )
        return msg


if __name__ == "__main__":
    bot = ChatBot()
    message_content = bot.chat("Hello")
    print(message_content)
    sharelink = bot.share_conversation()
    print(sharelink)

"""Entry for the hugchat command line interface.

simply type 
```bash
python -m hugchat.cli
```
to start cli.
"""

from .hugchat import ChatBot
from .login import Login
import getpass
import argparse
import os
import traceback

EMAIL = os.getenv("EMAIL")
PASSWD = os.getenv("PASSWD")
CHECK_BEFORE_PASSWORD = True


# COOKIE_PATH_DIR = os.path.abspath(os.path.dirname(__file__)) + "/usercookies"

def cli():
    global EMAIL
    global PASSWD
    global CHECK_BEFORE_PASSWORD
    print("-------HuggingChat-------")
    print("Official Site: https://huggingface.co/chat")
    print(
        "1. AI is an area of active research with known problems such as biased generation and misinformation.\n2. Do not use this application for high-stakes decisions or advice.\nContinuing to use means that you accept the above point(s)")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-u",
        type=str,
        help="Your huggingface account's email"
    )
    parser.add_argument(
        "-p",
        action="store_true",
        help="Require Password to login"
    )
    args = parser.parse_args()
    email = args.u
    inputpass = args.p
    cookies = None
    if CHECK_BEFORE_PASSWORD:
        if not email:
            email = EMAIL
        try:
            cookies = Login(email, None).loadCookiesFromDir()
        except Exception as e:
            pass
    if not cookies or inputpass:
        if not email:
            if EMAIL:
                if not PASSWD or inputpass:
                    PASSWD = getpass.getpass("Password: ")
                email = EMAIL
                passwd = PASSWD
            else:
                raise Exception("No email specified. Please use '-u' or set it in cli.py")
        else:
            if inputpass or not PASSWD:
                passwd = getpass.getpass("Password: ")
            else:
                passwd = PASSWD
        
        print(f"Sign in as :{email}")
        sign = Login(email, passwd)
        try:
            cookies = sign.loadCookiesFromDir()
        except Exception as e:
            print(e)
            print("Logging in...")
            cookies = sign.login()
            sign.saveCookiesToDir()
    
    chatbot = ChatBot(cookies=cookies)
    running = True
    print("Login successfully🎉 You can input `/help` to open the command menu.")
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
                conversation_id = question.split(" ")[1] if len(question.split(" ")) > 1 else ""
                try:
                    conversation_id = int(conversation_id)
                except Exception:
                    pass
                if type(conversation_id) == int:
                    if conversation_id <= len(conversations) and conversation_id > 0:
                        new_conversation_id = conversations[conversation_id-1]
                        if chatbot.current_conversation != new_conversation_id:
                            chatbot.change_conversation(new_conversation_id)
                            print(f"# Conversations switched successsfully to {new_conversation_id}")
                        else:
                            print("# Session already active")
                    else:
                        raise ValueError
                elif str(conversation_id) not in conversations:
                    print("# Please enter a valid ID number.")
                    print(f"# Sessions include: {', '.join(conversations)}")
                else:
                    if str(conversation_id) == chatbot.current_conversation:
                        print("# Session already active")
                    else:
                        chatbot.change_conversation(conversation_id)
                        print(f"# Conversation switched successfully to {conversation_id}")
            except ValueError:
                print("# Please enter a valid ID number")
        
        elif question.startswith("/del"):
            try:
                conversations = chatbot.get_conversation_list()
                conversation_id = question.split(" ")[1] if len(question.split(" ")) > 1 else ""
                try:
                    conversation_id = int(conversation_id)
                except Exception:
                    pass
                if type(conversation_id) == int:
                    if conversation_id <= len(conversations) and conversation_id > 0:
                        new_conversation_id = conversations[conversation_id-1]
                        if chatbot.current_conversation != new_conversation_id:
                            chatbot.delete_conversation(new_conversation_id)
                            print(f"# Conversations successfully deleted")
                        else:
                            print("# Cannot delete active session")
                    else:
                        raise ValueError
                elif str(conversation_id) not in conversations:
                    print("# Please enter a valid ID number.")
                    print(f"# Sessions include: {', '.join([conversations])}")
                else:
                    if str(conversation_id) == chatbot.current_conversation:
                        print("# Cannot delete active session")
                    else:
                        chatbot.delete_conversation(conversation_id)
                        print(f"# Conversation successfully deleted")
            except ValueError:
                print("# Please enter a valid ID number")

        elif question == "/ids":
            id_list = list(chatbot.get_conversation_list())
            [print(f"# {id_list.index(i) + 1} : {i}{' <active>' if chatbot.current_conversation == i else ''}") for i in
             id_list]
        
        elif question in ["/exit", "/quit", "/close"]:
            running = False
        
        elif question.startswith("/llm"):
            command = question.split(" ")[1] if len(question.split(" ")) > 1 else ""
            llms = chatbot.get_available_llm_models()
            if command:
                try:
                    index = int(command) - 1
                    if index >= 0 and index < len(llms):
                        if chatbot.get_active_llm_index() != index:
                            chatbot.switch_llm(index)
                            print(f"# Successfully switched llm to {chatbot.get_available_llm_models()[index]}")
                        else:
                            print("# This is already the active model")

                    else:
                        print("# Invaild index. Run /llm so see all models.")
                except ValueError:
                    print("# Invalid parameter. Enter a valid index number.")
            else:
                print("# Available llm:")
                [print(f"# {i+1} : {'<active> ' if i == chatbot.get_active_llm_index() else ''}{llms[i]}") for i in range(len(llms))]
                print("# Use /llm <index> to change model.")

        elif question.startswith("/sharewithauthor"):
            command = question.split(" ")[1] if len(question.split(" ")) > 1 else ""
            if command:
                if command in ["on","off"]:
                    chatbot.set_share_conversations(True if command == "on" else False)
                else:
                    print('# Invalid argument. Expected "on" or "off"')
            else:
                print("# Argument needed. (on|off)")

        elif question == "/clear":
            os.system('cls' if os.name == 'nt' else 'clear')

        elif question.startswith("/help"):
            command = question.split(" ")[1] if len(question.split(" ")) > 1 else ""
            if command:
                # TODO: Add specific examples for each command - @Zekaroni
                pass
            else:
                print(
                    "/new : Create and switch to a new conversation.\n"
                    "/ids : Shows a list of all ID numbers and ID strings in current session.\n"
                    "/switch <id> : Switches to the ID number or ID string passed.\n"
                    "/del <id> : Deletes the ID number or ID string passed. Will not delete active session.\n"
                    "/clear : Clear the terminal.\n"
                    "/llm : Get available models you can switch to.\n"
                    "/llm <index> : Switches model to given model index based on /llm.\n"
                    "/exit : Closes CLI environment.\n"
                )

        elif question.startswith("/"):
            print("# Invalid command")
        
        else:
            try:
                res = chatbot.chat(question)
                print("< " + res)
            except Exception as e:
                print(traceback.format_exc())
                print(f"[Error] {str(e)}")


if __name__ == '__main__':
    cli()

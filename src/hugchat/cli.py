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
        "1. AI is an area of active research with known problems such as biased generation and misinformation. Do not use this application for high-stakes decisions or advice.\nContinuing to use means that you accept the above point(s)")
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
            [print(f"{id_list.index(i) + 1} : {i}{' <active>' if chatbot.current_conversation == i else ''}") for i in
             id_list]
        
        elif question in ["/exit", "/quit", "/close"]:
            running = False
        
        elif question.startswith("/llm"):
            l = question.split(" ")
            if len(l) < 2:
                res = ""
                index = 0
                for i in chatbot.get_available_llm_models():
                    res += f"\n{index}. {i}"
                    index+=1
                
                print(f"Available llm:{res}\nUse /llm [index] to change.")
            elif len(l) == 2:
                try:
                    index = int(l[1])
                    if index > len(chatbot.get_available_llm_models()):
                        print("# wrong index")
                    else:
                        chatbot.switch_llm(index)
                        print(f"Succeed to switch llm to {chatbot.get_available_llm_models()[index]}")
                except BaseException:
                    print("# Invalid parameter")

        elif question.startswith("/sharewithauthor on"):
            chatbot.set_share_conversations(True)

        elif question.startswith("/sharewithauthor off"):
            chatbot.set_share_conversations(False)

        elif question.endswith("/clear"):
            os.system('cls' if os.name == 'nt' else 'clear')

        elif question.startswith("/"):
            print("# Invalid command")
        
        elif question == "":
            pass
        
        else:
            res = chatbot.chat(question)
            print("< " + res)


if __name__ == '__main__':
    cli()

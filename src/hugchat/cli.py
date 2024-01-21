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

ENVIRONMENT_EMAIL = os.getenv("EMAIL")
ENVIRONMENT_PASSWORD = os.getenv("PASSWD")
stream_output = False
is_web_search = False
web_search_hint = False
continued_conv = False

EXIT_COMMANDS = [
    "/exit",
    "/quit",
    "/stop",
    "/close"
]

# COOKIE_PATH_DIR = os.path.abspath(os.path.dirname(__file__)) + "/usercookies"


def handle_command(chatbot: ChatBot, userInput: str) -> None:
    global stream_output, is_web_search, web_search_hint , continued_conv

    arguments = userInput.lower().split(" ")
    command = arguments[0][1:] # Remove the '/' at the start of the input
    arguments = arguments[1:]

    if command == "help" or command == "commands":
        print("""
/new: Create and switch to a new conversation.
/ids: Shows a list of all ID numbers and ID strings in *current session*.
/switch <id>: Switches to the ID number or ID string passed.
/switch: Shows a list of all conversations' info in *current session*. Then you can choose one to switch to.
/switch all: Shows a list of all conversations' info in *your account*. Then you can choose one to switch to. (not recommended if your account has a lot of conversations)
/del <id>: Deletes the ID number or ID string passed. Will not delete active session.
/delete-all: Deletes all the conversations for the logged in user.
/clear: Clear the terminal.
/llm: Get available models you can switch to.
/llm <index>: Switches model to given model index based on /llm.
/sharewithauthor <on|off>: Changes settings for sharing data with model author. On by default.
/exit : Closes CLI environment.
/stream <on|off>: streaming the response.
/web <on|off>: web search.
/web-hint <on|off>: display web search hint.
        """)

    elif command == "new":
        new_conversation = chatbot.new_conversation(switch_to=True)
        print(f"# Created and switched to a new conversation\n# New conversation ID: {new_conversation.id}")

    elif command == "ids":
        print(f"# Conversations: {[conversation.id for conversation in chatbot.get_conversation_list()]}")

    elif command == "switch":
        try:
            if arguments[0] == "all":
                id = chatbot.get_remote_conversations(replace_conversation_list=True)
            else:
                id = chatbot.get_conversation_list()

            conversation_dict = {i+1: id_string for i, id_string in enumerate(id)}

            for i, id_string in conversation_dict.items():
                info = chatbot.get_conversation_info(id_string)
                print(f"{i}: ID: {info.id}\nTitle: {info.title[:43]}...\nModel: {info.model}.\nSystem Prompt: {info.system_prompt}\n--------------------------------------------------------")

            index_value = int(input("Choose conversation ID(input the index): "))
            target_id = conversation_dict.get(index_value)

            if target_id:
                chatbot.change_conversation(target_id)
                print(f"Switched to conversation with ID: {target_id}\n")
            else:
                print("Invalid conversation ID")
        except Exception as e:
            print(f"Error: {e}")

    elif command == "del" or command == "delete":
        try:
            to_delete_conversation = chatbot.get_conversation_from_id(arguments[0])
        except Exception:
            print("# Unable to delete conversation with ID. Conversation ID not found.")
            return

        chatbot.delete_conversation(to_delete_conversation)

        print("# Deleted conversation successfully")

    elif command == "delete-all" or command == "deleteall":
        chatbot.delete_all_conversations()
        print("# Deleted all conversations successfully")

        new_conversation = chatbot.new_conversation(switch_to=True)
        print(f"# Created and switched to a new conversation\n# New conversation ID: {new_conversation.id}")

    elif command == "clear" or command == "cls":
        os.system('cls' if os.name == 'nt' else 'clear')

    elif command == "llm":
        if len(arguments) == 0:
            print(f"# Available Models: {[model.id for model in chatbot.get_available_llm_models()]}")
            return

        try:
            chatbot.switch_llm(int(arguments[0]))
        except ValueError:
            print("# Invalid LLM index")
            return

        print(f"# Switched to LLM {chatbot.active_model.id}\n# Please note that you have to create a new conversation for this to take effect")

    elif command == "sharewithauthor":
        sharing = arguments[0] == "on"
        chatbot.set_share_conversations(sharing)

        print(f"# {'Now sharing conversations with model author' if sharing else 'No longer sharing conversations with model author'}")

    elif command == "stream" or command == "streamoutput":
        stream_output = arguments[0] == "on"

        print(f"# {'Now streaming responses' if stream_output else 'No longer streaming responses'}")

    elif command == "web" or command == "websearch":
        is_web_search = arguments[0] == "on"

        print(f"# {'Web searching activated' if is_web_search else 'We searching deactivated'}")

    elif command == "web-hint" or command == "webhint":
        web_search_hint = arguments[0] == "on"

        print(f"# {'Enabled web hint' if web_search_hint else 'Disabled web hint'}")

    else:
        print("# Unrecognized command")


def stream_response(generator) -> None:
    print("<", end="", flush=True)

    for chunk in generator:
        if chunk is None:
            continue
        print(chunk["token"], end="", flush=True)

    print()


def web_search(generator) -> None:
    print("<", end="", flush=True)

    sources = []
    for chunk in generator:
        if web_search_hint and chunk['type'] == 'webSearch' and chunk['messageType'] == 'update':
            args = chunk['args'][0] if 'args' in chunk else ""
            print(f"🌍 Web Searching | {chunk['message']} {args}")

        elif web_search_hint and chunk['type'] == 'webSearch' and chunk['messageType'] == 'sources' and "sources" in chunk:
            sources = chunk['sources']

        elif chunk['type'] == 'stream':
            print(chunk['token'], end="", flush=True)

    if web_search_hint and len(sources) > 0:
        print("\n# Sources:")
        for i in range(len(sources)):
            print(f"  {i+1}. {sources[i]['title']} - {sources[i]['link']}")

    print()


def get_arguments() -> tuple:
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
    parser.add_argument(
        "-s",
        action="store_true",
        help="Option to enable streaming mode output"
    )
    parser.add_argument(
        "-c",
        action="store_true",
        help="Continue the previous conversation"
    )
    args = parser.parse_args()
    return args.u, args.p, args.s, args.c

# ...


def cli():
    global stream_output, is_web_search, web_search_hint , continued_conv

    print("""
-------HuggingChat-------
Official Site: https://huggingface.co/chat
1. AI is an area of active research with known problems such as biased generation and misinformation.
2. Do not use this application for high-stakes decisions or advice.
Continuing to use means that you accept the above point(s)
    """)

    EMAIL, FORCE_INPUT_PASSWORD, stream_output, continued_conv = get_arguments()

    # Check if the email is in the environment variables or given as an argument
    if EMAIL is None:
        EMAIL = os.getenv("EMAIL")

        if EMAIL is None:
            raise Exception("No email specified. Please use '-u' or set the EMAIL environment variable.")

    # Attempt to load cookies from directory
    try:
        cookies = Login(EMAIL).loadCookiesFromDir()
    except Exception:
        cookies = None

    # If we could not find cookies or the "inputpass" argument is true
    # then ask for the password
    if cookies is None or FORCE_INPUT_PASSWORD:
        if ENVIRONMENT_PASSWORD is not None and not FORCE_INPUT_PASSWORD:
            PASSWORD = ENVIRONMENT_PASSWORD
        else:
            PASSWORD = getpass.getpass("Password: ")

        print("Logging in...")
        sign = Login(EMAIL, PASSWORD)
        cookies = sign.login()
        sign.saveCookiesToDir()

    print(f"Signed in as {EMAIL} .. attempting to login")

    chatbot = ChatBot(cookies=cookies)

    print("Login successfully! 🎉\nYou can input `/help` to open the command menu.\n")

    if continued_conv:
        ids = chatbot.get_remote_conversations(replace_conversation_list=True)

        conversation_dict = dict(enumerate(ids, start=1))

        # delete the conversation that was initially created on chatbot init
        target_id = conversation_dict[1]
        chatbot.delete_conversation(target_id)

        # switch to the most recent remote conversation
        target_id = conversation_dict[2]
        chatbot.change_conversation(target_id)

        print(f"Switched to Previous conversation with ID: {target_id}\n")

    while True:
        userInput = input("> ").strip()

        if len(userInput) == 0:
            continue
        if userInput.lower() in EXIT_COMMANDS:
            break

        # If the input starts with a slash then we know it is a command
        if userInput.startswith("/"):
            try:
                handle_command(chatbot, userInput)
            except Exception as e:
                print("An error occurred while processing your command: " + str(e))
                traceback.print_exc()

            continue

        # either start a web search or a normal response
        if is_web_search:
            res = chatbot.chat(userInput, stream=True, _stream_yield_all=True, web_search=is_web_search)
            web_search(res)

        else:
            if stream_output:
                res = chatbot.chat(userInput)
                stream_response(res)
            else:
                print("< " + chatbot.chat(userInput).wait_until_done().strip())

if __name__ == '__main__':
    cli()

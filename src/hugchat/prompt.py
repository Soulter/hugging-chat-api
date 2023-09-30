class Prompt:
    """
    This is the base prompt class.
    You can use it as default prompt.
    !!! This prompt can only be used once in each conversation !!!
    """

    _prefix: str = ""

    def __init__(self, system: str = "", user: str = "") -> None:
        self.system: str = system
        self.user: str = user

    def toText(self) -> str:
        p = self._prefix
        p += f"System: {self.system}\n"
        p += f"User: {self.user}"
        return p


class PromptFalcon(Prompt):
    """
    Prompt for `falcon` in huggingface.co/chat.
    Extend class<Prompt> and inject `system prompt` with prefix.
    !!! This prompt can only be use once in each conversation !!!
    """

    _prefix: str = "None\nFalcon:\n"


class PromptLlama(Prompt):
    """
    Prompt for `meta-llama & codellama` in huggingface.co/chat.
    Extend class<Prompt> and inject `system prompt` with prefix.
    !!! This prompt can only be use once in each conversation !!!
    """

    _prefix: str = "  [/INST]  </s>\n\n"

    def toText(self) -> str:
        return (
            self._prefix + f"<s>[INST] <<SYS>>{self.system}\n\n<</SYS>>\n\n{self.user}"
        )


if __name__ == "__main__":
    cc = PromptFalcon(system="sys", user="user")
    print(cc.toText())

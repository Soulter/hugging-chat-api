from .message import Conversation


class File:
    '''
    Class used to represent files created by the model
    '''

    def __init__(self, sha: str, name: str, mime: str, conversation: Conversation):
        self.sha = sha
        self.name = name
        self.mime = mime

        self.conversation = conversation
        self.url = self.get_url()

    def get_url(self) -> str:
        """
        Gets the url for the given file
        """

        return f"https://huggingface.co/chat/conversation/{self.conversation.id}/output/{self.sha}"

    def download_file(self, chatBot) -> bytes:
        """
        Downloads the given file
        """

        r = chatBot.session.get(self.url)
        return r.content

    def __str__(self) -> str:
        return f"File(url={self.url}, sha={self.sha}, name={self.name}, mime={self.mime})"

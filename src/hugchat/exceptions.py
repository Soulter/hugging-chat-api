class ModelOverloadedError(Exception):
    """
    HF Model Overloaded Error
    
    Raised when hf return response `{"error":"Model is overloaded","error_type":"overloaded"}`
    """
    pass


class ChatBotInitError(Exception):
    """
    ChatBot Init Error
    
    Raised when chatbot init failed
    """
    pass


class CreateConversationError(Exception):
    """
    Create Conversation Error
    
    Raised when create conversation failed
    """
    pass


class InvalidConversationIDError(Exception):
    """
    Invalid Conversation ID Error
    
    Raised when using a invalid conversation id
    """
    pass


class DeleteConversationError(Exception):
    """
    Delete Conversation Error
    
    Raised when delete conversation failed
    """
    pass


class ChatError(Exception):
    """
    Chat Error
    
    Raised when chat failed
    """
    pass

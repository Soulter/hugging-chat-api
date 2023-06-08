class ModelOverloadedError(Exception):
    """Raised when hf return response `{"error":"Model is overloaded","error_type":"overloaded"}`"""
    pass
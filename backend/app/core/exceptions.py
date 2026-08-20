class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class DocumentParsingError(AppException):
    def __init__(self, message: str, details: dict = None):
        super().__init__(f"Document parsing failed: {message}", status_code=422, details=details)

class EmbeddingError(AppException):
    def __init__(self, message: str, details: dict = None):
        super().__init__(f"Embedding generation error: {message}", status_code=502, details=details)

class LLMProviderError(AppException):
    def __init__(self, message: str, details: dict = None):
        super().__init__(f"LLM Provider error: {message}", status_code=502, details=details)

class ResourceNotFoundError(AppException):
    def __init__(self, resource: str, resource_id: str):
        super().__init__(f"{resource} with ID {resource_id} was not found", status_code=404)

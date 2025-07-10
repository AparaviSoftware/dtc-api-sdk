"""
Exception classes for the DTC API SDK.
"""


class DTCApiError(Exception):
    """Base exception for all DTC API errors."""
    
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


class AuthenticationError(DTCApiError):
    """Raised when authentication fails."""
    pass


class ValidationError(DTCApiError):
    """Raised when request validation fails."""
    pass


class PipelineError(DTCApiError):
    """Raised when pipeline operations fail."""
    pass


class TaskError(DTCApiError):
    """Raised when task operations fail."""
    pass


class NetworkError(DTCApiError):
    """Raised when network operations fail."""
    pass 
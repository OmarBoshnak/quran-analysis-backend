"""
Custom exceptions for the Quran Analysis API
"""


class QuranAPIException(Exception):
    """Base exception for all API errors"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class InvalidSurahException(QuranAPIException):
    """Raised when an invalid surah number is provided"""
    def __init__(self, surah: int):
        super().__init__(
            f"Invalid surah number: {surah}. Must be between 1-114",
            status_code=400
        )


class InvalidVerseException(QuranAPIException):
    """Raised when an invalid verse number is provided"""
    def __init__(self, surah: int, verse: int, max_verses: int):
        super().__init__(
            f"Invalid verse number: {verse} for surah {surah}. "
            f"Must be between 1-{max_verses}",
            status_code=400
        )


class AuthenticationException(QuranAPIException):
    """Raised when authentication fails"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class AuthorizationException(QuranAPIException):
    """Raised when user is not authorized to access a resource"""
    def __init__(self, message: str = "Not authorized to access this resource"):
        super().__init__(message, status_code=403)


class ResourceNotFoundException(QuranAPIException):
    """Raised when a requested resource is not found"""
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            f"{resource} with identifier '{identifier}' not found",
            status_code=404
        )


class InvalidJuzException(QuranAPIException):
    """Raised when an invalid juz number is provided"""
    def __init__(self, juz: int):
        super().__init__(
            f"Invalid juz number: {juz}. Must be between 1-30",
            status_code=400
        )


class ValidationException(QuranAPIException):
    """Raised when request validation fails"""
    def __init__(self, message: str):
        super().__init__(message, status_code=422)

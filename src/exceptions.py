# ----- CUSTOM EXCEPTIONS -----


class BumiException(Exception):
    """base exception for all bumi errors"""

    pass


class ProfileNotFoundError(BumiException):
    """raised when a letterboxd profile cannot be found"""

    def __init__(self, username, message=None):
        self.username = username
        self.message = message or f"Profile not found: {username}"
        super().__init__(self.message)


class RateLimitedError(BumiException):
    """raised when rate limited by letterboxd"""

    def __init__(self, url, retry_after=None, message=None):
        self.url = url
        self.retry_after = retry_after
        self.message = message or f"Rate limited when accessing: {url}"
        super().__init__(self.message)


class NetworkError(BumiException):
    """raised for network-related failures"""

    def __init__(self, url, original_error=None, message=None):
        self.url = url
        self.original_error = original_error
        self.message = message or f"Network error accessing: {url}"
        super().__init__(self.message)


class TimeoutError(BumiException):
    """raised when a request times out"""

    def __init__(self, url, timeout_ms, message=None):
        self.url = url
        self.timeout_ms = timeout_ms
        self.message = message or f"Timeout ({timeout_ms}ms) loading: {url}"
        super().__init__(self.message)


class ParseError(BumiException):
    """raised when page content cannot be parsed"""

    def __init__(self, url, selector=None, message=None):
        self.url = url
        self.selector = selector
        self.message = message or f"Failed to parse content at: {url}"
        super().__init__(self.message)


class InvalidURLError(BumiException):
    """raised for invalid letterboxd URLs"""

    def __init__(self, url, message=None):
        self.url = url
        self.message = message or f"Invalid Letterboxd URL: {url}"
        super().__init__(self.message)


class FilmNotFoundError(BumiException):
    """raised when a film cannot be found"""

    def __init__(self, film_slug, message=None):
        self.film_slug = film_slug
        self.message = message or f"Film not found: {film_slug}"
        super().__init__(self.message)


class ListNotFoundError(BumiException):
    """raised when a list cannot be found"""

    def __init__(self, list_url, message=None):
        self.list_url = list_url
        self.message = message or f"List not found: {list_url}"
        super().__init__(self.message)


class StorageError(BumiException):
    """raised for storage-related errors"""

    def __init__(self, operation, message=None):
        self.operation = operation
        self.message = message or f"Storage error during: {operation}"
        super().__init__(self.message)


class ConfigurationError(BumiException):
    """raised for configuration-related errors"""

    def __init__(self, config_key, message=None):
        self.config_key = config_key
        self.message = message or f"Configuration error for: {config_key}"
        super().__init__(self.message)

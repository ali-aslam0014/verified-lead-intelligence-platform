class SourceError(Exception):
    """Base exception for external source adapter errors."""
    def __init__(self, message: str, source_name: str):
        super().__init__(f"[{source_name}] {message}")
        self.source_name = source_name
        self.message = message


class SourceRateLimitError(SourceError):
    """Raised when source adapter hits rate limit bounds."""
    pass


class SourceAuthenticationError(SourceError):
    """Raised when API key or credentials fail authentication."""
    pass


class SourceTimeoutError(SourceError):
    """Raised when source request times out."""
    pass


class SourceFetchError(SourceError):
    """Raised when source payload fetching or parsing fails."""
    pass

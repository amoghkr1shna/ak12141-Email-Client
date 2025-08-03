"""
Interface module defining protocols and contracts for the email client system.

Flow: identity -> ingest -> message -> analyzer
"""

from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Protocol

# identity protocols


class AuthStatus(Enum):
    AUTHENTICATED = "authenticated"
    UNAUTHENTICATED = "unauthenticated"
    EXPIRED = "expired"
    REFRESHING = "refreshing"
    FAILED = "failed"  # Add FAILED status


@dataclass
class TokenInfo:
    """OAuth token information."""

    access_token: str
    refresh_token: str | None = None
    expires_at: float | None = None  # Change to float for timestamp
    token_type: str = "Bearer"
    scope: str | None = None  # Add scope field


class OAuthHandler(Protocol):
    def authenticate(self, credentials: dict[str, Any]) -> AuthStatus: ...

    def refresh_token(self, refresh_token: str) -> TokenInfo: ...

    def validate_token(self, token: TokenInfo) -> bool: ...


class TokenManager(Protocol):
    def store_token(self, token: TokenInfo) -> None: ...

    def retrieve_token(self) -> TokenInfo | None: ...

    def clear_token(self) -> None: ...

    def is_token_expired(self, token: TokenInfo) -> bool: ...


# message and attachment protocols


class Attachment(Protocol):
    @property
    def filename(self) -> str: ...

    @property
    def content_type(self) -> str: ...

    @property
    def size(self) -> int: ...

    def get_content(self) -> bytes: ...


class Message(Protocol):
    @property
    def id(self) -> str: ...

    @property
    def from_(self) -> str: ...

    @property
    def to(self) -> str: ...

    @property
    def date(self) -> datetime: ...

    @property
    def subject(self) -> str: ...

    @property
    def body(self) -> str: ...

    @property
    def attachments(self) -> list[Attachment]: ...

    @property
    def is_read(self) -> bool: ...

    def mark_as_read(self) -> None: ...

    def mark_as_unread(self) -> None: ...


# ingest protocols


class Ingestor(Protocol):
    """Protocol for ingesting emails from a mail backend."""

    def get_messages(
        self, limit: int | None = None, folder: str = "INBOX"
    ) -> Iterator[Message]: ...

    def search_messages(
        self, query: str, folder: str = "INBOX"
    ) -> Iterator[Message]: ...

    def get_folders(self) -> list[str]: ...


def get_ingestor() -> Ingestor:
    """Return an instance of an Ingestor.
    This function should be overridden by the implementation module.
    """
    raise NotImplementedError()


# analyzer protocols


class AnalysisResult(Protocol):
    @property
    def sentiment(self) -> float | None: ...

    @property
    def topics(self) -> list[str]: ...

    @property
    def entities(self) -> list[str]: ...

    @property
    def summary(self) -> str: ...

    @property
    def confidence(self) -> float: ...

    @property
    def metadata(self) -> dict[str, Any]: ...


class Analyzer(Protocol):
    def analyze(self, message: Message) -> AnalysisResult: ...

    def analyze_conversation(self, messages: list[Message]) -> AnalysisResult: ...

    def get_insights(
        self, analysis_results: list[AnalysisResult]
    ) -> dict[str, Any]: ...


# error classes


class AuthenticationError(Exception):
    pass


class ParsingError(Exception):
    pass


class AnalysisError(Exception):
    pass


class ConnectionError(Exception):
    pass


# exports


__all__ = [
    "AuthStatus",
    "TokenInfo",
    "OAuthHandler",
    "TokenManager",
    "Attachment",
    "Message",
    "Ingestor",
    "get_ingestor",
    "AnalysisResult",
    "Analyzer",
    "AuthenticationError",
    "ParsingError",
    "AnalysisError",
    "ConnectionError",
]

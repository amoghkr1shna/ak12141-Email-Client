"""
Interface module defining protocols and contracts for the email client system.

Flow: identity -> ingest -> message -> analyzer
"""

from typing import Protocol, List, Iterator, Optional, Dict, Any
from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

# identity protocols

class AuthStatus(Enum):
    AUTHENTICATED = "authenticated"
    UNAUTHENTICATED = "unauthenticated"
    EXPIRED = "expired"
    REFRESHING = "refreshing"

@dataclass
class TokenInfo:
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[int] = None
    token_type: str = "Bearer"

class OAuthHandler(Protocol):
    def authenticate(self, credentials: Dict[str, Any]) -> AuthStatus: ...
    def refresh_token(self, refresh_token: str) -> TokenInfo: ...
    def validate_token(self, token: TokenInfo) -> bool: ...

class TokenManager(Protocol):
    def store_token(self, token: TokenInfo) -> None: ...
    def retrieve_token(self) -> Optional[TokenInfo]: ...
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
    def attachments(self) -> List[Attachment]: ...
    @property
    def is_read(self) -> bool: ...
    def mark_as_read(self) -> None: ...
    def mark_as_unread(self) -> None: ...


# ingest protocols


class Ingestor(Protocol):
    """Protocol for ingesting emails from a mail backend."""
    def get_messages(
        self, 
        limit: Optional[int] = None, 
        folder: str = "INBOX"
    ) -> Iterator[Message]:
        ...
    def search_messages(
        self, 
        query: str, 
        folder: str = "INBOX"
    ) -> Iterator[Message]:
        ...
    def get_folders(self) -> List[str]:
        ...

def get_ingestor() -> Ingestor:
    """Return an instance of an Ingestor.
    This function should be overridden by the implementation module.
    """
    raise NotImplementedError()

# analyzer protocols

class AnalysisResult(Protocol):
    @property
    def sentiment(self) -> Optional[float]: ...
    @property
    def topics(self) -> List[str]: ...
    @property
    def entities(self) -> List[str]: ...
    @property
    def summary(self) -> str: ...
    @property
    def confidence(self) -> float: ...
    @property
    def metadata(self) -> Dict[str, Any]: ...

class Analyzer(Protocol):
    def analyze(self, message: Message) -> AnalysisResult: ...
    def analyze_conversation(self, messages: List[Message]) -> AnalysisResult: ...
    def get_insights(self, analysis_results: List[AnalysisResult]) -> Dict[str, Any]: ...


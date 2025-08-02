# Email Client Interface Module

This module defines the core protocols and contracts for the email client system, establishing the interface between all components in the pipeline flow: **identity → ingest → message → analyzer**.

## Overview

The interface module provides protocol definitions that ensure consistent communication between different components of the email client system. All implementations must conform to these protocols to maintain compatibility and interoperability.

## Pipeline Flow

```
Identity → Ingest → Message → Analyzer
```

## Protocols

### Identity Protocols

#### `OAuthHandler`
Defines OAuth authentication operations:
- `authenticate(credentials)`: Authenticate using provided credentials
- `refresh_token(refresh_token)`: Refresh an expired access token
- `validate_token(token)`: Validate if a token is still valid

#### `TokenManager`
Manages token storage and lifecycle:
- `store_token(token)`: Store authentication token
- `retrieve_token()`: Retrieve stored token
- `clear_token()`: Remove stored token
- `is_token_expired(token)`: Check if token has expired

### Message Protocols

#### `Message`
Represents an email message:
- Properties: `id`, `from_`, `to`, `date`, `subject`, `body`, `attachments`, `is_read`
- Methods: `mark_as_read()`, `mark_as_unread()`

#### `Attachment`
Represents an email attachment:
- Properties: `filename`, `content_type`, `size`
- Methods: `get_content()` - returns attachment content as bytes

### Ingest Protocols

#### `Ingestor`
Handles email retrieval and search:
- `get_messages(limit, folder)`: Retrieve messages from specified folder
- `search_messages(query, folder)`: Search for messages matching query
- `get_folders()`: Get list of available folders

### Analyzer Protocols

#### `Analyzer`
Provides email analysis capabilities:
- `analyze(message)`: Analyze a single message
- `analyze_conversation(messages)`: Analyze multiple related messages
- `get_insights(analysis_results)`: Generate insights from analysis results

#### `AnalysisResult`
Contains analysis output:
- Properties: `sentiment`, `topics`, `entities`, `summary`, `confidence`, `metadata`

## Data Classes

### `TokenInfo`
```python
@dataclass
class TokenInfo:
    access_token: str
    refresh_token: str | None = None
    expires_at: int | None = None
    token_type: str = "Bearer"
```

### `AuthStatus`
```python
class AuthStatus(Enum):
    AUTHENTICATED = "authenticated"
    UNAUTHENTICATED = "unauthenticated"
    EXPIRED = "expired"
    REFRESHING = "refreshing"
```

## Exception Classes

- `AuthenticationError`: OAuth and authentication related errors
- `ParsingError`: Email parsing and content extraction errors
- `AnalysisError`: Email analysis and processing errors
- `ConnectionError`: Network and connection related errors

## Usage Examples

### Implementing OAuth Handler

```python
from interface import OAuthHandler, AuthStatus, TokenInfo

class MyOAuthHandler(OAuthHandler):
    def authenticate(self, credentials: dict[str, Any]) -> AuthStatus:
        # Implementation here
        return AuthStatus.AUTHENTICATED
    
    def refresh_token(self, refresh_token: str) -> TokenInfo:
        # Implementation here
        return TokenInfo(access_token="new_token")
    
    def validate_token(self, token: TokenInfo) -> bool:
        # Implementation here
        return True
```

### Implementing Message

```python
from interface import Message, Attachment
from datetime import datetime

class MyMessage(Message):
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def from_(self) -> str:
        return self._from_addr
    
    # Implement other required properties and methods
```

### Implementing Ingestor

```python
from interface import Ingestor, Message
from collections.abc import Iterator

class MyIngestor(Ingestor):
    def get_messages(self, limit: int | None = None, folder: str = "INBOX") -> Iterator[Message]:
        # Implementation here
        yield from self._fetch_messages(limit, folder)
    
    def search_messages(self, query: str, folder: str = "INBOX") -> Iterator[Message]:
        # Implementation here
        yield from self._search_implementation(query, folder)
    
    def get_folders(self) -> list[str]:
        # Implementation here
        return ["INBOX", "Sent", "Drafts"]
```

### Implementing Analyzer

```python
from interface import Analyzer, AnalysisResult, Message

class MyAnalyzer(Analyzer):
    def analyze(self, message: Message) -> AnalysisResult:
        # Implementation here
        return self._create_analysis_result(message)
    
    def analyze_conversation(self, messages: list[Message]) -> AnalysisResult:
        # Implementation here
        return self._analyze_multiple_messages(messages)
    
    def get_insights(self, analysis_results: list[AnalysisResult]) -> dict[str, Any]:
        # Implementation here
        return {"insights": "data"}
```

## Factory Functions

### `get_ingestor()`
Factory function that should be overridden by implementation modules to return an `Ingestor` instance.

```python
def get_ingestor() -> Ingestor:
    """Return an instance of an Ingestor.
    This function should be overridden by the implementation module.
    """
    raise NotImplementedError()
```

## Type Safety

All protocols use proper type hints and are compatible with:
- **mypy**: Static type checking
- **Protocol**: Runtime type checking via `typing.Protocol`
- **Generic types**: Support for parameterized types where appropriate

## Integration

This interface module serves as the contract layer between:
1. **Identity module**: OAuth authentication and token management
2. **Ingest module**: Email fetching and parsing
3. **Message module**: Email message representation
4. **Analyzer module**: Email analysis and insights

Each implementation module should import from this interface and implement the required protocols to ensure system-wide compatibility.

## Dependencies

- Standard library: `collections.abc`, `dataclasses`, `datetime`, `enum`, `typing`
- External: `requests>=2.31.0`, `types-requests>=2.31.0`
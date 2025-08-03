# ak12141-Email-Client

[![CircleCI](https://dl.circleci.com/status-badge/img/gh/amoghkr1shna/ak12141-Email-Client/tree/main.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/gh/amoghkr1shna/ak12141-Email-Client/tree/main)

## Overview

A modular email client system built with Python 3.10+ that implements a microservice-like architecture with clear separation of concerns. The system follows a pipeline flow: **Identity → Ingest → Message → Analyzer**, where each component is independently developed and communicates through well-defined protocols.

## Architecture

The system consists of five core modules:

- **Interface**: Protocol definitions and contracts
- **Identity**: OAuth authentication and token management
- **Ingest**: Email fetching and parsing from local sources
- **Message**: Email message representation and manipulation
- **Analyzer**: Semantic analysis and metadata extraction

## Project Structure

```
.
├── src/
│   ├── interface/          # Protocol definitions
│   ├── identity/           # OAuth authentication
│   ├── ingest/             # Email fetching/parsing
│   ├── message/            # Message representation
│   └── analyzer/           # Email analysis
├── tests/
│   ├── integration/        # Integration tests
│   └── e2e/               # End-to-end tests
├── docs/                   # Documentation
├── .circleci/             # CI/CD configuration
└── pyproject.toml         # Project configuration
```

## Features

### Core Functionality
- **Modular design**: Each component can be developed and tested independently
- **Protocol-based interfaces**: Type-safe contracts between modules
- **OAuth 2.0 authentication**: Gmail integration with token management
- **Local email ingestion**: Maildir format support
- **Message standardization**: Uniform message representation
- **Email analysis**: Sentiment analysis, topic extraction, entity recognition

### Authentication Features
- Gmail OAuth 2.0 flow with PKCE
- Automatic token refresh
- Secure token storage
- Authentication state management

### Message Processing
- Support for multipart emails
- Attachment handling with various content types
- Read/unread status tracking
- Email search across subjects and bodies
- Folder-based organization

### Analysis Capabilities
- Sentiment analysis with confidence scoring
- Topic and entity extraction
- Text summarization
- Conversation thread analysis
- Aggregate insights generation

## Installation

### Prerequisites
- Python 3.10 or higher
- UV package manager

### Setup

1. **Install UV** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone and install dependencies**:
   ```bash
   git clone https://github.com/amoghkr1shna/ak12141-Email-Client.git
   cd ak12141-Email-Client
   uv sync --all-extras
   ```

## Usage

### Basic Pipeline Flow

```python
from identity import create_identity_manager
from ingest import get_ingestor
from message import create_message
from analyzer import EmailAnalyzer
from datetime import datetime

# Step 1: Setup authentication
identity_manager = create_identity_manager(
    provider="gmail",
    client_id="your_client_id",
    client_secret="your_client_secret",
    redirect_uri="http://localhost:8080/callback"
)

# Step 2: Ingest emails
ingestor = get_ingestor()
messages = list(ingestor.get_messages(limit=10))

# Step 3: Process messages
analyzer = EmailAnalyzer()
for msg in messages:
    # Convert to standard format
    standard_msg = create_message(
        msg_id=msg.id,
        from_addr=msg.from_,
        to_addr=msg.to,
        date=msg.date,
        subject=msg.subject,
        body=msg.body
    )
    
    # Analyze message
    analysis = analyzer.analyze(standard_msg)
    print(f"Sentiment: {analysis.sentiment}")
    print(f"Topics: {analysis.topics}")
```

### Authentication Example

```python
from identity import create_identity_manager
from interface import TokenInfo
import time

# Create identity manager
identity_manager = create_identity_manager(
    provider="gmail",
    client_id="your_client_id",
    client_secret="your_client_secret",
    redirect_uri="http://localhost:8080/callback"
)

# Check if authenticated
if identity_manager.is_authenticated():
    print("Already authenticated")
else:
    # Get authorization URL
    auth_url = identity_manager.oauth_handler.get_authorization_url()
    print(f"Visit: {auth_url}")
    
    # After user authorization, store token
    token = TokenInfo(
        access_token="your_access_token",
        refresh_token="your_refresh_token",
        expires_at=int(time.time()) + 3600
    )
    identity_manager.store_token(token)
```

### Email Ingestion Example

```python
from ingest import LocalIngestor
from pathlib import Path

# Setup local mail directory
mail_dir = Path.home() / "mail"
ingestor = LocalIngestor(mail_dir)

# Get available folders
folders = ingestor.get_folders()
print(f"Available folders: {folders}")

# Get messages from INBOX
for message in ingestor.get_messages(folder="INBOX", limit=5):
    print(f"From: {message.from_}")
    print(f"Subject: {message.subject}")
    print(f"Date: {message.date}")
    print(f"Attachments: {len(message.attachments)}")
    print("-" * 50)

# Search for specific messages
results = list(ingestor.search_messages("meeting", folder="INBOX"))
print(f"Found {len(results)} messages containing 'meeting'")
```

### Message Creation Example

```python
from message import create_message, SimpleAttachment
from datetime import datetime

# Create a simple message
msg = create_message(
    msg_id="msg_001",
    from_addr="sender@example.com",
    to_addr="recipient@example.com",
    date=datetime.now(),
    subject="Hello World",
    body="This is a test message."
)

# Create message with attachments
attachment_data = [{
    "filename": "document.pdf",
    "content_type": "application/pdf",
    "content": b"PDF content here"
}]

msg_with_attachment = create_message(
    msg_id="msg_002",
    from_addr="sender@example.com",
    to_addr="recipient@example.com",
    date=datetime.now(),
    subject="Document Attached",
    body="Please find the attached document.",
    attachments=attachment_data
)

# Mark message as read
msg.mark_as_read()
print(f"Message read status: {msg.is_read}")
```

### Analysis Example

```python
from analyzer import EmailAnalyzer
from message import create_message
from datetime import datetime

analyzer = EmailAnalyzer()

# Create sample message
message = create_message(
    msg_id="analysis_test",
    from_addr="boss@company.com",
    to_addr="employee@company.com",
    date=datetime.now(),
    subject="Great job on the project!",
    body="I wanted to congratulate you on the excellent work. The client was very impressed."
)

# Analyze single message
result = analyzer.analyze(message)
print(f"Sentiment: {result.sentiment}")
print(f"Topics: {result.topics}")
print(f"Summary: {result.summary}")
print(f"Confidence: {result.confidence}")

# Analyze conversation thread
messages = [message]  # Add more related messages
conversation_result = analyzer.analyze_conversation(messages)
print(f"Conversation metadata: {conversation_result.metadata}")

# Generate insights from multiple analyses
analysis_results = [result]  # Add more analysis results
insights = analyzer.get_insights(analysis_results)
print(f"Average sentiment: {insights['average_sentiment']}")
print(f"Common topics: {insights['common_topics']}")
```

## API Reference

### Interface Module

The interface module defines all protocols that other modules must implement:

- **Message Protocol**: Email message representation
- **Attachment Protocol**: Email attachment handling
- **Ingestor Protocol**: Email fetching and searching
- **Analyzer Protocol**: Email analysis capabilities
- **OAuth/Token Protocols**: Authentication management

### Factory Functions

Each module provides factory functions for easy instantiation:

- `create_identity_manager()`: Create authentication manager
- `get_ingestor()`: Create email ingestor
- `create_message()`: Create standardized message
- `EmailAnalyzer()`: Create email analyzer

## Development

### Running Tests

Run all tests:
```bash
uv run pytest
```

Run specific test suites:
```bash
# Integration tests
uv run pytest tests/integration/

# End-to-end tests  
uv run pytest tests/e2e/

# Module-specific tests
uv run pytest src/message/tests/
```

Run with coverage:
```bash
uv run pytest --cov=src --cov-report=html
```

### Code Quality

Format code:
```bash
uv run ruff format .
```

Lint code:
```bash
uv run ruff check .
```

Type checking:
```bash
uv run mypy src/
```

### Building Documentation

```bash
uv run mkdocs build
uv run mkdocs serve  # For development
```

## Directory Structure for Local Email

The ingestor expects a maildir-style directory structure:

```
~/mail/
├── INBOX/
│   ├── message1.eml
│   └── message2.eml
├── Sent/
│   └── sent1.eml
└── Drafts/
    └── draft1.eml
```

## CI/CD

The project uses CircleCI for continuous integration with the following pipeline:

1. **Setup**: Install UV and dependencies
2. **Code Quality**: Ruff formatting and linting checks
3. **Type Checking**: MyPy static analysis
4. **Testing**: Pytest with coverage reporting
5. **Documentation**: MkDocs build verification
6. **Artifacts**: Coverage reports and documentation

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes following the existing code style
4. Add tests for new functionality
5. Run the test suite: `uv run pytest`
6. Check code quality: `uv run ruff check .`
7. Commit your changes: `git commit -m 'Add amazing feature'`
8. Push to the branch: `git push origin feature/amazing-feature`
9. Open a Pull Request

### Development Guidelines

- Follow the existing protocol-based architecture
- Add comprehensive tests for new features
- Update documentation for any API changes
- Ensure all CI checks pass
- Use type hints throughout

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Module Documentation

For detailed documentation of each module:

- **Interface Module** - Protocol definitions
- **Identity Module** - OAuth authentication
- **Ingest Module** - Email fetching
- **Message Module** - Message representation
- **Analyzer Module** - Email analysis
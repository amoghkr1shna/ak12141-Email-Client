# Email Client Message Module

## Component Overview

This module provides message structuring and indexing functionality for the email client.

## Features

- Simple message and attachment implementations
- Factory functions for creating message objects
- Support for email attachments with various content types
- Message read/unread status tracking


## Scope

### What This Component Provides
- **Standardized Message Representation**: Uniform Message objects with guaranteed property access patterns
- **Immutable Data Structures**: Thread-safe message objects that prevent accidental modification
- **Attachment Management**: Structured attachment handling with content type detection and access methods
- **State Management**: Read/unread status tracking with atomic state transitions
- **Factory Pattern**: Consistent object creation with validation and error handling
- **Type Safety**: Full type annotation support for static analysis and IDE integration

### What This Component Doesn't Do
- **Message Storage**: Does not persist messages - operates purely on in-memory objects
- **Email Fetching**: Does not retrieve emails from external sources (handled by Ingest)
- **Content Analysis**: Does not interpret or analyze message content (handled by Analyzer)
- **Authentication**: Does not manage credentials or access tokens (handled by Identity)
- **Format Conversion**: Does not transform between email storage formats
- **Network Operations**: No remote communication or external service integration
- **Encryption/Decryption**: Raw content handling only - no cryptographic operations


## Classes

- `SimpleMessage`: Basic implementation of the Message protocol
- `SimpleAttachment`: Basic implementation of the Attachment protocol

## Functions

### Factory Functions
- **`create_message(**kwargs)`**: Creates standardized Message instances with validation and attachment processing

## Usage

### Basic Message Creation

```python
from message import create_message
from datetime import datetime

# Create simple message
msg = create_message(
    msg_id="msg_001",
    from_addr="sender@example.com",
    to_addr="recipient@example.com",
    date=datetime.now(),
    subject="Hello World",
    body="This is a test message."
)

print(f"Message ID: {msg.id}")
print(f"From: {msg.from_}")
print(f"Subject: {msg.subject}")
print(f"Read status: {msg.is_read}")
```

### Message with Attachments

```python
# Create message with attachments
attachment_data = [
    {
        'filename': 'document.pdf',
        'content_type': 'application/pdf',
        'content': b'PDF content here...'
    },
    {
        'filename': 'image.jpg',
        'content_type': 'image/jpeg',
        'content': b'JPEG content here...'
    }
]

msg_with_attachments = create_message(
    msg_id="msg_002",
    from_addr="sender@example.com",
    to_addr="recipient@example.com",
    date=datetime.now(),
    subject="Documents Attached",
    body="Please find the attached documents.",
    attachments=attachment_data
)

# Access attachments
for attachment in msg_with_attachments.attachments:
    print(f"Attachment: {attachment.filename}")
    print(f"Type: {attachment.content_type}")
    print(f"Size: {attachment.size} bytes")
    
    # Get content when needed
    content = attachment.get_content()
    print(f"Content preview: {content[:50]}...")
```
## Dependencies

### Workspace Dependencies
- **`email-client-interface`**: Provides `MessageProtocol` and `AttachmentProtocol` definitions

### External Dependencies
- **`dataclasses`**: For structured data objects with automatic method generation
- **`datetime`**: For message timestamp handling and timezone management
- **`typing`**: For type annotations and protocol compliance verification

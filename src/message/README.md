# Email Client Message Module

This module provides message structuring and indexing functionality for the email client.

## Features

- Simple message and attachment implementations
- Factory functions for creating message objects
- Support for email attachments with various content types
- Message read/unread status tracking

## Classes

- `SimpleMessage`: Basic implementation of the Message protocol
- `SimpleAttachment`: Basic implementation of the Attachment protocol

## Functions

- `create_message()`: Factory function to create Message instances

## Usage

```python
from message import create_message
from datetime import datetime

msg = create_message(
    msg_id="123",
    from_addr="sender@example.com",
    to_addr="recipient@example.com",
    date=datetime.now(),
    subject="Test Subject",
    body="Test Body"
)
```
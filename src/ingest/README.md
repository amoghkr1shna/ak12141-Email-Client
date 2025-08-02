# Email Client Ingest Module

This module provides email fetching and parsing functionality for the email client.

## Features

- Local file-based email ingestion from maildir format
- Email message parsing and content extraction
- Attachment handling with various content types
- Email search functionality across subjects and bodies
- Multi-folder support (INBOX, Sent, Drafts, etc.)
- Factory functions for creating ingestor instances

## Classes

- `LocalIngestor`: File-based implementation for reading emails from local directories
- `EmailMessage`: Implementation of Message protocol for parsed email content
- `EmailAttachment`: Implementation of Attachment protocol for email attachments

## Functions

- `get_ingestor()`: Factory function to create Ingestor instances

## Usage

### Basic Setup

```python
from ingest import get_ingestor
from pathlib import Path

# Create ingestor using default mail directory (~/mail)
ingestor = get_ingestor()

# Or create with custom mail directory
from ingest import LocalIngestor
custom_ingestor = LocalIngestor(Path("/path/to/mail"))
```

### Reading Messages

```python
# Get all messages from INBOX
messages = list(ingestor.get_messages())
for message in messages:
    print(f"From: {message.from_}")
    print(f"Subject: {message.subject}")
    print(f"Date: {message.date}")

# Get limited number of messages
recent_messages = list(ingestor.get_messages(limit=10))

# Get messages from specific folder
sent_messages = list(ingestor.get_messages(folder="Sent"))
```

### Searching Messages

```python
# Search for messages containing specific terms
search_results = list(ingestor.search_messages("meeting"))
for message in search_results:
    print(f"Found: {message.subject}")

# Search in specific folder
inbox_results = list(ingestor.search_messages("project", folder="INBOX"))
```

### Working with Folders

```python
# Get all available folders
folders = ingestor.get_folders()
print(f"Available folders: {folders}")

# Iterate through all folders
for folder in folders:
    messages = list(ingestor.get_messages(folder=folder))
    print(f"{folder}: {len(messages)} messages")
```

### Working with Attachments

```python
# Check for messages with attachments
for message in ingestor.get_messages():
    if message.attachments:
        print(f"Message '{message.subject}' has {len(message.attachments)} attachments")
        
        for attachment in message.attachments:
            print(f"  - {attachment.filename} ({attachment.content_type})")
            print(f"    Size: {attachment.size} bytes")
            
            # Get attachment content
            content = attachment.get_content()
            # Process attachment content as needed
```

### Message Properties

```python
for message in ingestor.get_messages(limit=1):
    print(f"ID: {message.id}")
    print(f"From: {message.from_}")
    print(f"To: {message.to}")
    print(f"Subject: {message.subject}")
    print(f"Date: {message.date}")
    print(f"Body: {message.body[:100]}...")
    print(f"Read status: {message.is_read}")
    
    # Mark as read/unread
    message.mark_as_read()
    print(f"Now read: {message.is_read}")
```

## Email Format Support

- **Local email files**: Reads emails from .eml files in directory structure
- **Standard email parsing**: Uses Python's built-in email library for message parsing
- **Multipart messages**: Handles HTML content and attachments
- **Content encoding**: Properly decodes message content and attachments

## Error Handling

- **ConnectionError**: Raised when specified folder doesn't exist
- **ParsingError**: Raised when email content cannot be parsed
- **Missing data**: Graceful handling of emails with missing headers

## Directory Structure

The ingestor expects a mail directory structure like:
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

## Dependencies

- `email`: Python standard library for email parsing
- `pathlib`: For file system operations
- `datetime`: For date/time handling
- `email-client-interface`: For protocol definitions and interfaces
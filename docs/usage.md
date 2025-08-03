# KYMail Usage Guide

## Basic Pipeline Flow

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

## Authentication Example

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

## Email Ingestion Example

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

## Message Creation Example

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

## Analysis Example

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
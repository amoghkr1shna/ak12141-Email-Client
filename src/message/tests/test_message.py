"""
Tests for message implementation module.
"""

from datetime import datetime
import pytest
from interface import ParsingError
from message import SimpleAttachment, SimpleMessage, create_message


def test_simple_attachment():
    """Test SimpleAttachment class."""
    filename = "test.txt"
    content_type = "text/plain"
    content = b"Hello, World!"
    
    attachment = SimpleAttachment(filename, content_type, content)
    
    assert attachment.filename == filename
    assert attachment.content_type == content_type
    assert attachment.size == len(content)
    assert attachment.get_content() == content


def test_simple_message():
    """Test SimpleMessage class."""
    msg_id = "123"
    from_addr = "sender@example.com"
    to_addr = "recipient@example.com"
    date = datetime.now()
    subject = "Test Subject"
    body = "Test Body"
    
    message = SimpleMessage(msg_id, from_addr, to_addr, date, subject, body)
    
    assert message.id == msg_id
    assert message.from_ == from_addr
    assert message.to == to_addr
    assert message.date == date
    assert message.subject == subject
    assert message.body == body
    assert message.attachments == []
    assert not message.is_read


def test_message_read_status():
    """Test message read/unread status functionality."""
    message = SimpleMessage("123", "sender@example.com", "recipient@example.com",
                          datetime.now(), "Subject", "Body")
    
    assert not message.is_read
    message.mark_as_read()
    assert message.is_read
    message.mark_as_unread()
    assert not message.is_read


def test_message_with_attachments():
    """Test message with attachments."""
    attachment = SimpleAttachment("test.txt", "text/plain", b"Hello, World!")
    message = SimpleMessage("123", "sender@example.com", "recipient@example.com",
                          datetime.now(), "Subject", "Body", [attachment])
    
    assert len(message.attachments) == 1
    assert message.attachments[0].filename == "test.txt"
    assert message.attachments[0].content_type == "text/plain"
    assert message.attachments[0].get_content() == b"Hello, World!"


def test_create_message():
    """Test create_message factory function."""
    msg_id = "123"
    from_addr = "sender@example.com"
    to_addr = "recipient@example.com"
    date = datetime.now()
    subject = "Test Subject"
    body = "Test Body"
    attachments = [{
        "filename": "test.txt",
        "content_type": "text/plain",
        "content": b"Hello, World!"
    }]
    
    message = create_message(msg_id, from_addr, to_addr, date, subject, body, attachments)
    
    assert message.id == msg_id
    assert message.from_ == from_addr
    assert message.to == to_addr
    assert message.date == date
    assert message.subject == subject
    assert message.body == body
    assert len(message.attachments) == 1
    assert message.attachments[0].filename == "test.txt"


def test_create_message_invalid_attachment():
    """Test create_message with invalid attachment data."""
    attachments = [{
        "filename": "test.txt",
        # Missing content_type and content
    }]
    
    with pytest.raises(ParsingError) as exc_info:
        create_message("123", "sender@example.com", "recipient@example.com",
                      datetime.now(), "Subject", "Body", attachments)
    
    assert "Invalid attachment data: missing" in str(exc_info.value)

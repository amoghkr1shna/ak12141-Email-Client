"""
Integration tests for ingest and message modules.
"""

import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest
from ingest import EmailAttachment, EmailMessage, LocalIngestor, get_ingestor
from interface import Attachment, Message, ParsingError
from message import SimpleAttachment, SimpleMessage, create_message


class TestIngestMessageIntegration:
    """Integration tests for ingest and message modules."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create temporary directory for mail files
        self.temp_dir = tempfile.mkdtemp()
        self.mail_dir = Path(self.temp_dir) / "mail"
        self.mail_dir.mkdir(parents=True, exist_ok=True)
        
        # Create INBOX folder
        (self.mail_dir / "INBOX").mkdir(exist_ok=True)
        
        # Create sample email files with different formats
        self._create_simple_email()
        self._create_multipart_email()
        self._create_email_with_attachment()

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_simple_email(self):
        """Create a simple text email."""
        simple_email = """From: sender@example.com
To: recipient@example.com
Subject: Simple Test Email
Date: Wed, 01 Aug 2025 10:00:00 +0000

This is a simple test email body.
"""
        (self.mail_dir / "INBOX" / "simple.eml").write_text(simple_email)

    def _create_multipart_email(self):
        """Create a multipart email."""
        multipart_email = """From: sender@example.com
To: recipient@example.com
Subject: Multipart Test Email
Date: Wed, 01 Aug 2025 11:00:00 +0000
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="boundary123"

--boundary123
Content-Type: text/plain

This is the plain text part of the email.

--boundary123
Content-Type: text/html

<html><body><h1>HTML Part</h1></body></html>

--boundary123--
"""
        (self.mail_dir / "INBOX" / "multipart.eml").write_text(multipart_email)

    def _create_email_with_attachment(self):
        """Create an email with attachment."""
        email_with_attachment = """From: sender@example.com
To: recipient@example.com
Subject: Email with Attachment
Date: Wed, 01 Aug 2025 12:00:00 +0000
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="boundary456"

--boundary456
Content-Type: text/plain

This email has an attachment.

--boundary456
Content-Type: text/plain; name="test.txt"
Content-Disposition: attachment; filename="test.txt"

This is the content of the attached file.

--boundary456--
"""
        (self.mail_dir / "INBOX" / "with_attachment.eml").write_text(email_with_attachment)

    def test_ingest_to_message_conversion(self):
        """Test converting ingested emails to message objects."""
        ingestor = LocalIngestor(self.mail_dir)
        
        # Get messages from ingestor
        ingested_messages = list(ingestor.get_messages(limit=10))
        assert len(ingested_messages) >= 3  # At least our test emails
        
        # Convert ingested messages to simple message format
        converted_messages = []
        for ingested_msg in ingested_messages:
            # Convert EmailMessage to SimpleMessage
            simple_msg = create_message(
                msg_id=ingested_msg.id,
                from_addr=ingested_msg.from_,
                to_addr=ingested_msg.to,
                date=ingested_msg.date,
                subject=ingested_msg.subject,
                body=ingested_msg.body,
                attachments=[
                    {
                        "filename": att.filename,
                        "content_type": att.content_type,
                        "content": att.get_content()
                    }
                    for att in ingested_msg.attachments
                ]
            )
            converted_messages.append(simple_msg)
        
        # Verify conversion worked
        assert len(converted_messages) == len(ingested_messages)
        
        # Check properties are preserved
        for original, converted in zip(ingested_messages, converted_messages):
            assert original.id == converted.id
            assert original.from_ == converted.from_
            assert original.to == converted.to
            assert original.subject == converted.subject
            assert original.body == converted.body
            assert len(original.attachments) == len(converted.attachments)

    def test_attachment_compatibility(self):
        """Test that attachments work between ingest and message modules."""
        ingestor = LocalIngestor(self.mail_dir)
        
        # Find an email with attachments
        messages_with_attachments = []
        for msg in ingestor.get_messages():
            if msg.attachments:
                messages_with_attachments.append(msg)
        
        if messages_with_attachments:
            msg = messages_with_attachments[0]
            
            # Get attachment from ingested message
            ingested_attachment = msg.attachments[0]
            
            # Create equivalent SimpleAttachment
            simple_attachment = SimpleAttachment(
                filename=ingested_attachment.filename,
                content_type=ingested_attachment.content_type,
                content=ingested_attachment.get_content()
            )
            
            # Verify they have the same properties
            assert ingested_attachment.filename == simple_attachment.filename
            assert ingested_attachment.content_type == simple_attachment.content_type
            assert ingested_attachment.size == simple_attachment.size
            assert ingested_attachment.get_content() == simple_attachment.get_content()

    def test_message_processing_pipeline(self):
        """Test a complete message processing pipeline."""
        # Step 1: Ingest messages
        ingestor = LocalIngestor(self.mail_dir)
        raw_messages = list(ingestor.get_messages(limit=5))
        
        # Step 2: Process each message
        processed_messages = []
        for raw_msg in raw_messages:
            # Create a processed version using message module
            processed = create_message(
                msg_id=f"processed_{raw_msg.id}",
                from_addr=raw_msg.from_,
                to_addr=raw_msg.to,
                date=raw_msg.date,
                subject=f"[PROCESSED] {raw_msg.subject}",
                body=f"Original: {raw_msg.body}",
                attachments=[
                    {
                        "filename": att.filename,
                        "content_type": att.content_type,
                        "content": att.get_content()
                    }
                    for att in raw_msg.attachments
                ]
            )
            processed_messages.append(processed)
        
        # Step 3: Verify processing
        assert len(processed_messages) == len(raw_messages)
        
        for original, processed in zip(raw_messages, processed_messages):
            assert processed.subject.startswith("[PROCESSED]")
            assert original.subject in processed.subject
            assert original.body in processed.body
            assert processed.id.startswith("processed_")

    def test_search_and_message_creation(self):
        """Test searching for messages and creating new ones based on results."""
        ingestor = LocalIngestor(self.mail_dir)
        
        # Search for specific messages
        search_results = list(ingestor.search_messages("test"))
        assert len(search_results) > 0
        
        # Create summary messages based on search results
        summary_messages = []
        for result in search_results:
            summary = create_message(
                msg_id=f"summary_{result.id}",
                from_addr="system@example.com",
                to_addr=result.from_,
                date=datetime.now(),
                subject=f"Summary: {result.subject}",
                body=f"Found message: {result.subject}\nFrom: {result.from_}\nDate: {result.date}",
                attachments=None
            )
            summary_messages.append(summary)
        
        # Verify summaries were created
        assert len(summary_messages) == len(search_results)
        for summary in summary_messages:
            assert summary.subject.startswith("Summary:")
            assert summary.from_ == "system@example.com"

    def test_error_handling_integration(self):
        """Test error handling between ingest and message modules."""
        # Test with invalid email file
        invalid_email_path = self.mail_dir / "INBOX" / "invalid.eml"
        invalid_email_path.write_text("This is not a valid email format")
        
        ingestor = LocalIngestor(self.mail_dir)
        
        # Should handle parsing errors gracefully
        with pytest.raises(ParsingError):
            list(ingestor.get_messages())
        
        # Test invalid attachment data in message creation
        with pytest.raises(ParsingError):
            create_message(
                msg_id="test",
                from_addr="test@example.com",
                to_addr="user@example.com",
                date=datetime.now(),
                subject="Test",
                body="Test",
                attachments=[{"filename": "test.txt"}]  # Missing required fields
            )

    def test_folder_based_message_organization(self):
        """Test organizing messages by folders."""
        # Create additional folders
        (self.mail_dir / "Sent").mkdir(exist_ok=True)
        (self.mail_dir / "Drafts").mkdir(exist_ok=True)
        
        # Add messages to different folders
        sent_email = """From: user@example.com
To: recipient@example.com
Subject: Sent Email
Date: Wed, 01 Aug 2025 13:00:00 +0000

This is a sent email.
"""
        (self.mail_dir / "Sent" / "sent1.eml").write_text(sent_email)
        
        draft_email = """From: user@example.com
To: draft@example.com
Subject: Draft Email
Date: Wed, 01 Aug 2025 14:00:00 +0000

This is a draft email.
"""
        (self.mail_dir / "Drafts" / "draft1.eml").write_text(draft_email)
        
        ingestor = LocalIngestor(self.mail_dir)
        
        # Test folder discovery
        folders = ingestor.get_folders()
        assert "INBOX" in folders
        assert "Sent" in folders
        assert "Drafts" in folders
        
        # Test folder-specific message retrieval
        inbox_messages = list(ingestor.get_messages(folder="INBOX"))
        sent_messages = list(ingestor.get_messages(folder="Sent"))
        draft_messages = list(ingestor.get_messages(folder="Drafts"))
        
        assert len(inbox_messages) >= 3  # Our original test emails
        assert len(sent_messages) == 1
        assert len(draft_messages) == 1
        
        # Convert messages from different folders
        all_messages = []
        for folder in folders:
            for msg in ingestor.get_messages(folder=folder):
                converted = create_message(
                    msg_id=f"{folder}_{msg.id}",
                    from_addr=msg.from_,
                    to_addr=msg.to,
                    date=msg.date,
                    subject=f"[{folder}] {msg.subject}",
                    body=msg.body
                )
                all_messages.append(converted)
        
        # Verify folder organization is preserved
        folder_counts = {}
        for msg in all_messages:
            folder = msg.id.split("_")[0]
            folder_counts[folder] = folder_counts.get(folder, 0) + 1
        
        assert folder_counts["INBOX"] >= 3
        assert folder_counts["Sent"] == 1
        assert folder_counts["Drafts"] == 1

    def test_factory_function_integration(self):
        """Test integration using factory functions."""
        # Test with default ingestor
        default_ingestor = get_ingestor()
        assert isinstance(default_ingestor, LocalIngestor)
        
        # Test message creation with factory
        test_message = create_message(
            msg_id="factory_test",
            from_addr="factory@example.com",
            to_addr="user@example.com",
            date=datetime.now(),
            subject="Factory Test",
            body="Created via factory function"
        )
        
        assert isinstance(test_message, SimpleMessage)
        assert test_message.id == "factory_test"
        assert test_message.subject == "Factory Test"

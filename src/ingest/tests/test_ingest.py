import email
from datetime import datetime
from email.message import Message as RawEmailMessage
from pathlib import Path
from unittest.mock import patch

import pytest
from interface import ConnectionError

from ingest import EmailAttachment, EmailMessage, LocalIngestor, get_ingestor


@pytest.fixture
def sample_email() -> RawEmailMessage:
    """Create a sample email message for testing."""
    msg = email.message.EmailMessage()
    msg["From"] = "sender@example.com"
    msg["To"] = "recipient@example.com"
    msg["Subject"] = "Test Subject"
    msg["Date"] = "Mon, 1 Aug 2025 12:00:00 +0000"
    msg.set_content("Test body content")
    return msg


@pytest.fixture
def sample_attachment() -> RawEmailMessage:
    """Create a sample email attachment for testing."""
    part = email.message.EmailMessage()
    part.set_content(b"test content", maintype="application", subtype="pdf")
    # Set filename using Content-Disposition header
    part["Content-Disposition"] = 'attachment; filename="test.pdf"'
    return part


class TestEmailAttachment:
    """Test cases for EmailAttachment class."""

    def test_filename(self, sample_attachment: RawEmailMessage) -> None:
        attachment = EmailAttachment(sample_attachment)
        assert attachment.filename == "test.pdf"

    def test_content_type(self, sample_attachment: RawEmailMessage) -> None:
        attachment = EmailAttachment(sample_attachment)
        assert attachment.content_type == "application/pdf"

    def test_get_content(self, sample_attachment: RawEmailMessage) -> None:
        attachment = EmailAttachment(sample_attachment)
        content = attachment.get_content()
        assert isinstance(content, bytes)
        assert content == b"test content"

    def test_size(self, sample_attachment: RawEmailMessage) -> None:
        attachment = EmailAttachment(sample_attachment)
        assert attachment.size == len(b"test content")


class TestEmailMessage:
    """Test cases for EmailMessage class."""

    def test_basic_properties(self, sample_email: RawEmailMessage) -> None:
        message = EmailMessage(sample_email, "test_id")
        assert message.id == "test_id"
        assert message.from_ == "sender@example.com"
        assert message.to == "recipient@example.com"
        assert message.subject == "Test Subject"
        assert isinstance(message.date, datetime)
        assert message.body == "Test body content"

    def test_read_status(self, sample_email: RawEmailMessage) -> None:
        message = EmailMessage(sample_email, "test_id")
        assert not message.is_read
        message.mark_as_read()
        assert message.is_read
        message.mark_as_unread()
        assert not message.is_read

    def test_attachments(
        self, sample_email: RawEmailMessage, sample_attachment: RawEmailMessage
    ) -> None:
        sample_email.add_attachment(sample_attachment)
        message = EmailMessage(sample_email, "test_id")
        attachments = message.attachments
        assert len(attachments) - 1 == 1
        assert isinstance(attachments[0], EmailAttachment)


class TestLocalIngestor:
    """Test cases for LocalIngestor class."""

    @pytest.fixture
    def mail_dir(self, tmp_path: Path) -> Path:
        """Create a temporary mail directory for testing."""
        inbox = tmp_path / "INBOX"
        inbox.mkdir()
        return tmp_path

    @pytest.fixture
    def ingestor(self, mail_dir: Path) -> LocalIngestor:
        """Create a LocalIngestor instance for testing."""
        return LocalIngestor(mail_dir)

    def test_get_messages(
        self, ingestor: LocalIngestor, mail_dir: Path, sample_email: RawEmailMessage
    ) -> None:
        # Create a test email file
        msg_path = mail_dir / "INBOX" / "test_msg.eml"
        msg_path.write_bytes(sample_email.as_bytes())

        messages = list(ingestor.get_messages())
        assert len(messages) == 1
        assert isinstance(messages[0], EmailMessage)
        assert messages[0].subject == "Test Subject"

    def test_search_messages(
        self, ingestor: LocalIngestor, mail_dir: Path, sample_email: RawEmailMessage
    ) -> None:
        # Create a test email file
        msg_path = mail_dir / "INBOX" / "test_msg.eml"
        msg_path.write_bytes(sample_email.as_bytes())

        messages = list(ingestor.search_messages("Test"))
        assert len(messages) == 1
        messages = list(ingestor.search_messages("nonexistent"))
        assert len(messages) == 0

    def test_get_folders(self, ingestor: LocalIngestor, mail_dir: Path) -> None:
        # Create test folders
        (mail_dir / "Sent").mkdir()
        (mail_dir / "Drafts").mkdir()

        folders = ingestor.get_folders()
        assert "INBOX" in folders
        assert "Sent" in folders
        assert "Drafts" in folders

    def test_invalid_folder(self, ingestor: LocalIngestor) -> None:
        with pytest.raises(ConnectionError):
            list(ingestor.get_messages(folder="NonexistentFolder"))


def test_get_ingestor() -> None:
    """Test the get_ingestor factory function."""
    with patch("pathlib.Path.home") as mock_home:
        mock_home.return_value = Path("/test/home")
        ingestor = get_ingestor()
        assert isinstance(ingestor, LocalIngestor)
        assert ingestor.mail_dir == Path("/test/home/mail")

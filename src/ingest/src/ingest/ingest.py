"""
Email ingestion implementation module.
"""

import email
from collections.abc import Iterator
from datetime import datetime
from email.message import Message as RawEmailMessage  # Renamed to avoid conflict
from pathlib import Path

from interface import (
    Attachment,
    ConnectionError,
    Ingestor,
    Message,
    ParsingError,
)


class EmailAttachment(Attachment):
    """Implementation of the Attachment protocol."""

    def __init__(self, part: RawEmailMessage):  # Updated type annotation
        self._part = part
        self._content: bytes | None = None

    @property
    def filename(self) -> str:
        filename = self._part.get_filename()
        if not filename:
            raise ParsingError("Attachment has no filename")
        return filename

    @property
    def content_type(self) -> str:
        return self._part.get_content_type()

    @property
    def size(self) -> int:
        content = self.get_content()
        return len(content)

    def get_content(self) -> bytes:
        if self._content is None:
            payload = self._part.get_payload(decode=True)
            if not isinstance(payload, bytes):
                raise ParsingError("Invalid attachment content")
            self._content = payload
        return self._content


class EmailMessage(Message):
    """Implementation of the Message protocol."""

    def __init__(self, msg: RawEmailMessage, msg_id: str):  # Updated type annotation
        self._msg = msg
        self._id = msg_id
        self._is_read = False
        self._attachments: list[Attachment] | None = None

    @property
    def id(self) -> str:
        return self._id

    @property
    def from_(self) -> str:
        return self._msg["from"] or ""

    @property
    def to(self) -> str:
        return self._msg["to"] or ""

    @property
    def date(self) -> datetime:
        date_str = self._msg["date"]
        if not date_str:
            raise ParsingError("Message has no date")
        return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")

    @property
    def subject(self) -> str:
        return self._msg["subject"] or ""

    @property
    def body(self) -> str:
        if self._msg.is_multipart():
            for part in self._msg.walk():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)
                    if isinstance(payload, bytes):
                        return payload.decode()
                    raise ParsingError("Invalid message content")
        payload = self._msg.get_payload(decode=True)
        if isinstance(payload, bytes):
            return payload.decode()
        raise ParsingError("Invalid message content")

    @property
    def attachments(self) -> list[Attachment]:
        if self._attachments is None:
            self._attachments = []
            if self._msg.is_multipart():
                for part in self._msg.walk():
                    if part.get_filename():
                        self._attachments.append(EmailAttachment(part))
        return self._attachments

    @property
    def is_read(self) -> bool:
        return self._is_read

    def mark_as_read(self) -> None:
        self._is_read = True

    def mark_as_unread(self) -> None:
        self._is_read = False


class LocalIngestor(Ingestor):
    """Local file-based implementation of the Ingestor protocol."""

    def __init__(self, mail_dir: Path):
        self.mail_dir = mail_dir

    def get_messages(
        self, limit: int | None = None, folder: str = "INBOX"
    ) -> Iterator[Message]:
        folder_path = self.mail_dir / folder
        if not folder_path.exists():
            raise ConnectionError(f"Folder not found: {folder}")

        count = 0
        for msg_path in folder_path.iterdir():
            if limit is not None and count >= limit:
                break

            try:
                with msg_path.open("rb") as f:
                    # Add type annotation for msg and use parser function directly
                    msg: RawEmailMessage = email.message_from_binary_file(f)
                    yield EmailMessage(msg, msg_path.stem)
                    count += 1
            except Exception as e:
                raise ParsingError(f"Failed to parse message: {e}") from e

    def search_messages(self, query: str, folder: str = "INBOX") -> Iterator[Message]:
        for message in self.get_messages(folder=folder):
            if (
                query.lower() in message.subject.lower()
                or query.lower() in message.body.lower()
            ):
                yield message

    def get_folders(self) -> list[str]:
        return [p.name for p in self.mail_dir.iterdir() if p.is_dir()]


def get_ingestor() -> Ingestor:
    """Factory function to create an Ingestor instance."""
    mail_dir = Path.home() / "mail"  # Default location
    return LocalIngestor(mail_dir)

"""
Email ingestion implementation module.
"""

import email
from collections.abc import Iterator
from datetime import datetime
from email.message import Message as RawEmailMessage  # Renamed to avoid conflict
from pathlib import Path
from typing import Any

from interface import (
    Attachment,
    ConnectionError,
    Ingestor,
    Message,
    ParsingError,
)


class EmailAttachment(Attachment):
    """Implementation of the Attachment protocol."""

    def __init__(self, part: Any) -> None:
        self._part = part
        self._content: bytes | None = None

    @property
    def filename(self) -> str:
        # Try multiple ways to get filename
        filename = self._part.get_filename()
        if filename:
            return str(filename)

        # Try Content-Disposition header
        disposition = self._part.get("Content-Disposition", "")
        if "filename=" in disposition:
            import re

            match = re.search(r'filename="?([^"]+)"?', disposition)
            if match:
                return match.group(1)

        # Try Content-Type parameters (like name parameter)
        content_type_params = self._part.get_params()
        if content_type_params:
            for param_name, param_value in content_type_params:
                if param_name.lower() in ("name", "filename"):
                    return str(param_value)

        # Generate filename based on content type
        content_type = self._part.get_content_type()
        if content_type:
            extension_map = {
                "text/plain": ".txt",
                "text/html": ".html",
                "image/jpeg": ".jpg",
                "image/png": ".png",
                "application/pdf": ".pdf",
                "application/octet-stream": ".bin",
            }
            ext = extension_map.get(content_type, ".dat")
            return f"attachment{ext}"

        # Last resort - raise error if no filename can be determined
        raise ParsingError("Attachment has no filename")

    @property
    def content_type(self) -> str:
        content_type = self._part.get_content_type()
        return str(content_type) if content_type else ""  # Ensure string return type

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
            # Get the text/plain part
            for part in self._msg.walk():
                if part.get_content_type() == "text/plain":
                    content = part.get_payload(decode=True)
                    if isinstance(content, bytes):
                        text = content.decode("utf-8", errors="ignore")
                    else:
                        text = str(content)
                    return text.rstrip("\n\r")  # Remove trailing newlines
            return ""
        else:
            content = self._msg.get_payload(decode=True)
            if isinstance(content, bytes):
                text = content.decode("utf-8", errors="ignore")
            else:
                text = str(content)
            return text.rstrip("\n\r")  # Remove trailing newlines

    @property
    def attachments(self) -> list[Attachment]:
        attachments: list[Attachment] = []
        if self._msg.is_multipart():
            for part in self._msg.walk():
                # Skip the multipart container itself
                if part.get_content_maintype() == "multipart":
                    continue

                # Skip the main text content parts
                disposition = part.get("Content-Disposition", "")
                content_type = part.get_content_type()

                # Only consider it an attachment if:
                # 1. Explicitly marked as attachment in Content-Disposition, OR
                # 2. Has a filename parameter, OR
                # 3. Is not text content (and not the main body)
                is_main_content = (
                    content_type in ("text/plain", "text/html")
                    and "attachment" not in disposition
                    and part.get_filename() is None
                )

                if not is_main_content:
                    # This is likely an attachment
                    try:
                        attachments.append(EmailAttachment(part))
                    except ParsingError:
                        # Skip attachments that can't be processed
                        continue

        return attachments

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

                    # Validate that we got a proper email message
                    if not isinstance(msg, RawEmailMessage) or not msg.keys():
                        raise ParsingError(
                            f"Invalid email format in file: {msg_path.name}"
                        )

                    yield EmailMessage(msg, msg_path.stem)
                    count += 1
            except Exception as e:
                raise ParsingError(
                    f"Failed to parse message {msg_path.name}: {e}"
                ) from e

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

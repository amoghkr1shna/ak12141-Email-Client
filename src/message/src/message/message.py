"""
Message implementation module.
"""

from datetime import datetime
from typing import Any

from interface import Attachment, Message, ParsingError


class SimpleAttachment(Attachment):
    """Simple implementation of the Attachment protocol."""

    def __init__(
        self,
        filename: str,
        content_type: str,
        content: bytes,
    ) -> None:
        self._filename = filename
        self._content_type = content_type
        self._content = content

    @property
    def filename(self) -> str:
        return self._filename

    @property
    def content_type(self) -> str:
        return self._content_type

    @property
    def size(self) -> int:
        return len(self._content)

    def get_content(self) -> bytes:
        return self._content


class SimpleMessage(Message):
    """Simple implementation of the Message protocol."""

    def __init__(
        self,
        msg_id: str,
        from_addr: str,
        to_addr: str,
        date: datetime,
        subject: str,
        body: str,
        attachments: list[Attachment] | None = None,
    ) -> None:
        self._id = msg_id
        self._from = from_addr
        self._to = to_addr
        self._date = date
        self._subject = subject
        self._body = body
        self._attachments = attachments or []
        self._is_read = False

    @property
    def id(self) -> str:
        return self._id

    @property
    def from_(self) -> str:
        return self._from

    @property
    def to(self) -> str:
        return self._to

    @property
    def date(self) -> datetime:
        return self._date

    @property
    def subject(self) -> str:
        return self._subject

    @property
    def body(self) -> str:
        return self._body

    @property
    def attachments(self) -> list[Attachment]:
        return self._attachments

    @property
    def is_read(self) -> bool:
        return self._is_read

    def mark_as_read(self) -> None:
        self._is_read = True

    def mark_as_unread(self) -> None:
        self._is_read = False


def create_message(
    msg_id: str,
    from_addr: str,
    to_addr: str,
    date: datetime,
    subject: str,
    body: str,
    attachments: list[dict[str, Any]] | None = None,
) -> Message:
    """Factory function to create a Message instance."""
    attachment_list: list[Attachment] = []

    if attachments:
        for att in attachments:
            try:
                attachment = SimpleAttachment(
                    filename=att["filename"],
                    content_type=att["content_type"],
                    content=att["content"],
                )
                attachment_list.append(attachment)
            except KeyError as e:
                raise ParsingError(f"Invalid attachment data: missing {e}") from e

    return SimpleMessage(
        msg_id=msg_id,
        from_addr=from_addr,
        to_addr=to_addr,
        date=date,
        subject=subject,
        body=body,
        attachments=attachment_list,
    )

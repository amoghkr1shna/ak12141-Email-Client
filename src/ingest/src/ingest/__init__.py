"""
Ingest module for email fetching and parsing.
"""

from .ingest import EmailAttachment, EmailMessage, LocalIngestor, get_ingestor

__all__ = ["EmailAttachment", "EmailMessage", "LocalIngestor", "get_ingestor"]

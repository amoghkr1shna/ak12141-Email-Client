"""
Tests for analyzer implementation module.
"""

from datetime import datetime
from typing import Any

import pytest
from analyzer import EmailAnalysisResult, EmailAnalyzer
from interface import Message


class MockMessage(Message):
    """Mock implementation of Message for testing."""

    def __init__(
        self,
        msg_id: str,
        subject: str,
        body: str,
        date: datetime,
        from_addr: str = "sender@example.com",
        to_addr: str = "recipient@example.com",
    ):
        self._id = msg_id
        self._subject = subject
        self._body = body
        self._date = date
        self._from = from_addr
        self._to = to_addr
        self._attachments = []
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
    def attachments(self) -> list[Any]:
        return self._attachments

    @property
    def is_read(self) -> bool:
        return self._is_read

    def mark_as_read(self) -> None:
        self._is_read = True

    def mark_as_unread(self) -> None:
        self._is_read = False


def test_email_analysis_result_init():
    """Test EmailAnalysisResult initialization and default values."""
    result = EmailAnalysisResult()
    
    assert result.sentiment is None
    assert result.topics == []
    assert result.entities == []
    assert result.summary == ""
    assert result.confidence == 0.0
    assert result.metadata == {}


def test_email_analysis_result_with_values():
    """Test EmailAnalysisResult with custom values."""
    result = EmailAnalysisResult(
        _sentiment=0.5,
        _topics=["business", "meeting"],
        _entities=["John", "Project X"],
        _summary="Meeting summary",
        _confidence=0.9,
        _metadata={"key": "value"}
    )
    
    assert result.sentiment == 0.5
    assert result.topics == ["business", "meeting"]
    assert result.entities == ["John", "Project X"]
    assert result.summary == "Meeting summary"
    assert result.confidence == 0.9
    assert result.metadata == {"key": "value"}


def test_email_analyzer_single_message():
    """Test EmailAnalyzer.analyze with a single message."""
    analyzer = EmailAnalyzer()
    message = MockMessage(
        msg_id="123",
        subject="Test Meeting",
        body="Let's discuss the project tomorrow.",
        date=datetime.now()
    )
    
    result = analyzer.analyze(message)
    
    assert isinstance(result, EmailAnalysisResult)
    assert isinstance(result.sentiment, float)
    assert isinstance(result.topics, list)
    assert isinstance(result.entities, list)
    assert isinstance(result.summary, str)
    assert isinstance(result.confidence, float)
    assert result.metadata["message_id"] == message.id
    assert "date" in result.metadata
    assert "has_attachments" in result.metadata


def test_email_analyzer_conversation():
    """Test EmailAnalyzer.analyze_conversation with multiple messages."""
    analyzer = EmailAnalyzer()
    messages = [
        MockMessage(
            msg_id="1",
            subject="Meeting",
            body="Can we meet tomorrow?",
            date=datetime(2025, 8, 1, 10, 0)
        ),
        MockMessage(
            msg_id="2",
            subject="Re: Meeting",
            body="Yes, that works for me.",
            date=datetime(2025, 8, 1, 11, 0)
        )
    ]
    
    result = analyzer.analyze_conversation(messages)
    
    assert isinstance(result, EmailAnalysisResult)
    assert result.metadata["message_count"] == 2
    assert "date_range" in result.metadata
    assert "start" in result.metadata["date_range"]
    assert "end" in result.metadata["date_range"]


def test_email_analyzer_get_insights():
    """Test EmailAnalyzer.get_insights with multiple analysis results."""
    analyzer = EmailAnalyzer()
    results = [
        EmailAnalysisResult(_sentiment=0.5, _confidence=0.8),
        EmailAnalysisResult(_sentiment=0.7, _confidence=0.9),
        EmailAnalysisResult(_sentiment=0.3, _confidence=0.7)
    ]
    
    insights = analyzer.get_insights(results)
    
    assert "average_sentiment" in insights
    assert "common_topics" in insights
    assert "total_analyzed" in insights
    assert "average_confidence" in insights
    assert insights["total_analyzed"] == 3
    assert isinstance(insights["average_sentiment"], float)
    assert isinstance(insights["common_topics"], list)


def test_email_analyzer_get_insights_empty():
    """Test EmailAnalyzer.get_insights with empty results list."""
    analyzer = EmailAnalyzer()
    insights = analyzer.get_insights([])
    
    assert "error" in insights
    assert insights["error"] == "No analysis results provided"


def test_email_analyzer_summary_truncation():
    """Test summary truncation for long messages."""
    analyzer = EmailAnalyzer()
    long_body = "x" * 300  # Create a string longer than 200 characters
    message = MockMessage(
        msg_id="123",
        subject="Test",
        body=long_body,
        date=datetime.now()
    )
    
    result = analyzer.analyze(message)
    
    assert len(result.summary) < len(long_body)
    assert result.summary.endswith("...")

from dataclasses import dataclass, field
from typing import Any

from interface import AnalysisResult, Analyzer, Message


@dataclass
class EmailAnalysisResult:
    """Concrete implementation of AnalysisResult protocol."""

    _sentiment: float | None = None
    _topics: list[str] = field(default_factory=list)
    _entities: list[str] = field(default_factory=list)
    _summary: str = ""
    _confidence: float = 0.0
    _metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize default values for collections."""
        # No need for initialization since we use field(default_factory=...)
        pass

    @property
    def sentiment(self) -> float | None:
        return self._sentiment

    @property
    def topics(self) -> list[str]:
        return self._topics

    @property
    def entities(self) -> list[str]:
        return self._entities

    @property
    def summary(self) -> str:
        return self._summary

    @property
    def confidence(self) -> float:
        return self._confidence

    @property
    def metadata(self) -> dict[str, Any]:
        return self._metadata


class EmailAnalyzer(Analyzer):
    """Concrete implementation of Analyzer protocol."""

    def analyze(self, message: Message) -> AnalysisResult:
        """Analyze a single email message."""
        # Basic analysis implementation
        result = EmailAnalysisResult()

        # Extract text content
        text = f"{message.subject}\n{message.body}"

        # Perform sentiment analysis (placeholder implementation)
        result._sentiment = self._analyze_sentiment(text)

        # Extract topics
        result._topics = self._extract_topics(text)

        # Extract entities
        result._entities = self._extract_entities(text)

        # Generate summary
        result._summary = self._generate_summary(text)

        # Set confidence score
        result._confidence = 0.85  # placeholder confidence score

        # Add metadata
        result._metadata = {
            "message_id": message.id,
            "date": message.date.isoformat(),
            "has_attachments": len(message.attachments) > 0,
        }

        return result

    def analyze_conversation(self, messages: list[Message]) -> AnalysisResult:
        """Analyze a conversation thread of messages."""
        # Combine all messages for analysis
        combined_text = "\n".join(
            [f"Subject: {msg.subject}\nBody: {msg.body}" for msg in messages]
        )

        result = EmailAnalysisResult()

        # Analyze the combined conversation
        result._sentiment = self._analyze_sentiment(combined_text)
        result._topics = self._extract_topics(combined_text)
        result._entities = self._extract_entities(combined_text)
        result._summary = self._generate_summary(combined_text)
        result._confidence = 0.80

        # Add conversation-specific metadata
        result._metadata = {
            "message_count": len(messages),
            "date_range": {
                "start": min(msg.date for msg in messages).isoformat(),
                "end": max(msg.date for msg in messages).isoformat(),
            },
        }

        return result

    def get_insights(self, analysis_results: list[AnalysisResult]) -> dict[str, Any]:
        """Generate insights from multiple analysis results."""
        if not analysis_results:
            return {"error": "No analysis results provided"}

        # Calculate aggregate metrics
        avg_sentiment = sum(
            r.sentiment for r in analysis_results if r.sentiment is not None
        ) / len(analysis_results)

        # Collect all topics and count frequencies
        all_topics = []
        for result in analysis_results:
            all_topics.extend(result.topics)
        topic_frequencies = {
            topic: all_topics.count(topic) for topic in set(all_topics)
        }

        return {
            "average_sentiment": avg_sentiment,
            "common_topics": sorted(
                topic_frequencies.items(), key=lambda x: x[1], reverse=True
            )[:5],
            "total_analyzed": len(analysis_results),
            "average_confidence": sum(r.confidence for r in analysis_results)
            / len(analysis_results),
        }

    def _analyze_sentiment(self, text: str) -> float:
        """Helper method for sentiment analysis."""
        # Placeholder implementation
        # In a real implementation, you would use a NLP library like NLTK or spaCy
        return 0.0

    def _extract_topics(self, text: str) -> list[str]:
        """Helper method for topic extraction."""
        # Placeholder implementation
        return []

    def _extract_entities(self, text: str) -> list[str]:
        """Helper method for entity extraction."""
        # Placeholder implementation
        return []

    def _generate_summary(self, text: str) -> str:
        """Helper method for text summarization."""
        # Placeholder implementation
        return text[:200] + "..." if len(text) > 200 else text

# Email Client Analyzer Module

This module provides semantic analysis and metadata extraction functionality for email messages.

## Features

- Email sentiment analysis with confidence scoring
- Topic extraction from email content
- Entity recognition and extraction
- Text summarization with intelligent truncation
- Conversation thread analysis for multiple related messages
- Insights generation from multiple analysis results
- Comprehensive metadata collection

## Classes

- `EmailAnalyzer`: Main analyzer implementation for processing email messages
- `EmailAnalysisResult`: Data structure containing analysis results and metadata

## Usage

### Basic Message Analysis

```python
from analyzer import EmailAnalyzer
from datetime import datetime

# Create analyzer instance
analyzer = EmailAnalyzer()

# Analyze a single message (assuming you have a message object)
result = analyzer.analyze(message)

# Access analysis results
print(f"Sentiment: {result.sentiment}")
print(f"Topics: {result.topics}")
print(f"Entities: {result.entities}")
print(f"Summary: {result.summary}")
print(f"Confidence: {result.confidence}")
print(f"Metadata: {result.metadata}")
```

### Conversation Analysis

```python
# Analyze multiple related messages as a conversation
messages = [message1, message2, message3]  # List of related messages
conversation_result = analyzer.analyze_conversation(messages)

print(f"Conversation sentiment: {conversation_result.sentiment}")
print(f"Message count: {conversation_result.metadata['message_count']}")
print(f"Date range: {conversation_result.metadata['date_range']}")
```

### Generating Insights

```python
# Analyze multiple messages and generate insights
analysis_results = []
for message in messages:
    result = analyzer.analyze(message)
    analysis_results.append(result)

# Generate aggregate insights
insights = analyzer.get_insights(analysis_results)
print(f"Average sentiment: {insights['average_sentiment']}")
print(f"Common topics: {insights['common_topics']}")
print(f"Total analyzed: {insights['total_analyzed']}")
print(f"Average confidence: {insights['average_confidence']}")
```

### Working with Analysis Results

```python
# Create custom analysis result
from analyzer import EmailAnalysisResult

result = EmailAnalysisResult(
    _sentiment=0.8,
    _topics=["business", "meeting"],
    _entities=["John Doe", "Project Alpha"],
    _summary="Meeting discussion about project timeline",
    _confidence=0.9,
    _metadata={"custom_field": "value"}
)

# Access properties
print(f"Sentiment score: {result.sentiment}")
print(f"Extracted topics: {result.topics}")
print(f"Named entities: {result.entities}")
```

## Analysis Features

### Sentiment Analysis
- Returns float values representing message sentiment
- Confidence scoring for sentiment predictions
- Handles both positive and negative sentiment detection

### Topic Extraction
- Identifies key topics and themes from email content
- Returns list of extracted topic strings
- Useful for email categorization and filtering

### Entity Recognition
- Extracts named entities (people, organizations, locations)
- Returns list of identified entity strings
- Helps with contact management and relationship mapping

### Text Summarization
- Generates concise summaries of email content
- Intelligent truncation for long messages (200 character limit)
- Preserves key information while reducing content length

### Metadata Collection
- Message ID and timestamp information
- Attachment presence detection
- Conversation-specific metadata (message count, date ranges)
- Custom metadata support for extended functionality

## Conversation Analysis

The analyzer can process multiple related messages together:

```python
# Group related messages by subject or thread
conversation_messages = get_conversation_messages("Project Update")
result = analyzer.analyze_conversation(conversation_messages)

# Access conversation-specific data
print(f"Messages in conversation: {result.metadata['message_count']}")
print(f"Conversation timespan: {result.metadata['date_range']}")
```

## Insights and Analytics

Generate aggregate analytics from multiple analysis results:

```python
# Collect analysis results from different sources
all_results = []
all_results.extend(analyze_inbox_messages())
all_results.extend(analyze_sent_messages())

# Generate comprehensive insights
insights = analyzer.get_insights(all_results)

# Access aggregated data
print(f"Overall sentiment trend: {insights['average_sentiment']}")
print(f"Most common topics: {insights['common_topics'][:3]}")
```

## Error Handling

- **Empty analysis results**: Returns error message when no results provided
- **Missing message data**: Graceful handling of incomplete message objects
- **Content processing**: Robust handling of various email content types

## Implementation Notes

- Uses placeholder implementations for core NLP functionality
- Designed for easy integration with external NLP libraries (NLTK, spaCy, etc.)
- Extensible architecture for adding custom analysis features
- Thread-safe design for concurrent message processing

## Dependencies

- `dataclasses`: For structured analysis result objects
- `typing`: For type hints and annotations
- `email-client-interface`: For protocol definitions and interfaces
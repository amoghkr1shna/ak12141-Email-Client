"""
Integration tests for message and analyzer modules.
"""

from datetime import datetime, timedelta
from typing import Any

import pytest
from analyzer import EmailAnalysisResult, EmailAnalyzer
from interface import AnalysisResult, Message
from message import SimpleAttachment, SimpleMessage, create_message


class TestMessageAnalyzerIntegration:
    """Integration tests for message and analyzer modules."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = EmailAnalyzer()
        
        # Create sample messages for testing
        self.sample_messages = self._create_sample_messages()

    def _create_sample_messages(self) -> list[Message]:
        """Create sample messages for testing."""
        messages = []
        
        # Message 1: Positive business email
        msg1 = create_message(
            msg_id="msg1",
            from_addr="boss@company.com",
            to_addr="employee@company.com",
            date=datetime(2025, 8, 1, 9, 0),
            subject="Great job on the project!",
            body="I wanted to congratulate you on the excellent work you did on the quarterly report. The presentation was outstanding and the client was very impressed."
        )
        messages.append(msg1)
        
        # Message 2: Meeting request
        msg2 = create_message(
            msg_id="msg2",
            from_addr="colleague@company.com",
            to_addr="employee@company.com",
            date=datetime(2025, 8, 1, 10, 30),
            subject="Meeting request - Project planning",
            body="Can we schedule a meeting tomorrow to discuss the upcoming project milestones? I think we need to review the timeline and allocate resources accordingly."
        )
        messages.append(msg2)
        
        # Message 3: Email with attachments
        attachment_data = [
            {
                "filename": "report.pdf",
                "content_type": "application/pdf",
                "content": b"PDF content here"
            },
            {
                "filename": "data.xlsx",
                "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "content": b"Excel data content"
            }
        ]
        
        msg3 = create_message(
            msg_id="msg3",
            from_addr="finance@company.com",
            to_addr="employee@company.com",
            date=datetime(2025, 8, 1, 14, 15),
            subject="Q2 Financial Reports",
            body="Please find attached the quarterly financial reports. Review the budget allocations and let me know if you have any questions about the expenditure breakdown.",
            attachments=attachment_data
        )
        messages.append(msg3)
        
        # Message 4: Support ticket
        msg4 = create_message(
            msg_id="msg4",
            from_addr="support@company.com",
            to_addr="employee@company.com",
            date=datetime(2025, 8, 1, 16, 45),
            subject="Support Ticket #12345 - Server Issues",
            body="We have identified the server performance issues you reported. The database queries were causing timeouts. We have optimized the indexes and the issue should be resolved."
        )
        messages.append(msg4)
        
        return messages

    def test_single_message_analysis(self):
        """Test analyzing a single message."""
        message = self.sample_messages[0]  # Positive business email
        
        result = self.analyzer.analyze(message)
        
        # Verify result type and basic properties
        assert isinstance(result, EmailAnalysisResult)
        assert isinstance(result.sentiment, float)
        assert isinstance(result.topics, list)
        assert isinstance(result.entities, list)
        assert isinstance(result.summary, str)
        assert isinstance(result.confidence, float)
        assert isinstance(result.metadata, dict)
        
        # Verify metadata contains message information
        assert result.metadata["message_id"] == message.id
        assert result.metadata["date"] == message.date.isoformat()
        assert "has_attachments" in result.metadata
        assert result.metadata["has_attachments"] == (len(message.attachments) > 0)

    def test_message_with_attachments_analysis(self):
        """Test analyzing a message with attachments."""
        message = self.sample_messages[2]  # Message with attachments
        
        result = self.analyzer.analyze(message)
        
        # Verify attachment information is captured
        assert result.metadata["has_attachments"] is True
        assert len(message.attachments) == 2
        
        # Verify attachment details are accessible
        attachments = message.attachments
        assert attachments[0].filename == "report.pdf"
        assert attachments[1].filename == "data.xlsx"
        assert attachments[0].content_type == "application/pdf"

    def test_conversation_analysis(self):
        """Test analyzing multiple messages as a conversation."""
        # Use first 3 messages as a conversation thread
        conversation = self.sample_messages[:3]
        
        result = self.analyzer.analyze_conversation(conversation)
        
        # Verify conversation-specific metadata
        assert result.metadata["message_count"] == 3
        assert "date_range" in result.metadata
        assert "start" in result.metadata["date_range"]
        assert "end" in result.metadata["date_range"]
        
        # Verify date range is correct
        start_date = datetime.fromisoformat(result.metadata["date_range"]["start"])
        end_date = datetime.fromisoformat(result.metadata["date_range"]["end"])
        assert start_date <= end_date
        assert start_date == conversation[0].date
        assert end_date == conversation[-1].date

    def test_insights_generation(self):
        """Test generating insights from multiple analysis results."""
        # Analyze all sample messages
        analysis_results = []
        for message in self.sample_messages:
            result = self.analyzer.analyze(message)
            analysis_results.append(result)
        
        # Generate insights
        insights = self.analyzer.get_insights(analysis_results)
        
        # Verify insights structure
        assert "average_sentiment" in insights
        assert "common_topics" in insights
        assert "total_analyzed" in insights
        assert "average_confidence" in insights
        
        # Verify values
        assert insights["total_analyzed"] == len(self.sample_messages)
        assert isinstance(insights["average_sentiment"], float)
        assert isinstance(insights["common_topics"], list)
        assert isinstance(insights["average_confidence"], float)

    def test_message_read_status_analysis(self):
        """Test that message read status doesn't affect analysis."""
        message = self.sample_messages[0]
        
        # Analyze unread message
        assert not message.is_read
        result_unread = self.analyzer.analyze(message)
        
        # Mark as read and analyze again
        message.mark_as_read()
        assert message.is_read
        result_read = self.analyzer.analyze(message)
        
        # Results should be identical regardless of read status
        assert result_unread.sentiment == result_read.sentiment
        assert result_unread.summary == result_read.summary
        assert result_unread.confidence == result_read.confidence

    def test_empty_message_analysis(self):
        """Test analyzing messages with minimal content."""
        empty_message = create_message(
            msg_id="empty",
            from_addr="test@example.com",
            to_addr="user@example.com",
            date=datetime.now(),
            subject="",
            body=""
        )
        
        result = self.analyzer.analyze(empty_message)
        
        # Should still return valid result structure
        assert isinstance(result, EmailAnalysisResult)
        assert result.metadata["message_id"] == "empty"
        assert result.metadata["has_attachments"] is False

    def test_large_message_analysis(self):
        """Test analyzing messages with large content."""
        large_body = "This is a very long email. " * 100  # Create long content
        
        large_message = create_message(
            msg_id="large",
            from_addr="sender@example.com",
            to_addr="recipient@example.com",
            date=datetime.now(),
            subject="Large Message",
            body=large_body
        )
        
        result = self.analyzer.analyze(large_message)
        
        # Verify summary is truncated for large messages
        assert len(result.summary) <= len(large_body)
        if len(large_body) > 200:
            assert result.summary.endswith("...")

    def test_message_analysis_workflow(self):
        """Test a complete message analysis workflow."""
        # Step 1: Create messages with different characteristics
        workflow_messages = []
        
        # Business email
        business_msg = create_message(
            msg_id="business_1",
            from_addr="ceo@company.com",
            to_addr="team@company.com",
            date=datetime.now(),
            subject="Quarterly Results",
            body="Our quarterly results exceeded expectations. Revenue increased by 15% and we achieved all key performance indicators."
        )
        workflow_messages.append(business_msg)
        
        # Technical email
        tech_msg = create_message(
            msg_id="tech_1",
            from_addr="dev@company.com",
            to_addr="team@company.com",
            date=datetime.now() + timedelta(hours=1),
            subject="System Deployment",
            body="The new system deployment is scheduled for tonight. Please ensure all databases are backed up and monitoring systems are active."
        )
        workflow_messages.append(tech_msg)
        
        # Step 2: Analyze each message
        analysis_results = []
        for msg in workflow_messages:
            result = self.analyzer.analyze(msg)
            analysis_results.append(result)
        
        # Step 3: Generate insights
        insights = self.analyzer.get_insights(analysis_results)
        
        # Step 4: Verify workflow results
        assert len(analysis_results) == 2
        assert insights["total_analyzed"] == 2
        
        # Verify individual analysis results
        for i, result in enumerate(analysis_results):
            assert result.metadata["message_id"] == workflow_messages[i].id
            assert isinstance(result.summary, str)

    def test_batch_message_processing(self):
        """Test processing multiple messages efficiently."""
        # Process all sample messages in batch
        batch_results = []
        
        for message in self.sample_messages:
            # Mark messages as read for processing
            message.mark_as_read()
            result = self.analyzer.analyze(message)
            batch_results.append(result)
        
        # Verify all messages were processed
        assert len(batch_results) == len(self.sample_messages)
        
        # Verify each result is valid
        for i, result in enumerate(batch_results):
            assert result.metadata["message_id"] == self.sample_messages[i].id
            assert isinstance(result.confidence, float)
            assert 0.0 <= result.confidence <= 1.0

    def test_message_factory_with_analysis(self):
        """Test using message factory function with analyzer."""
        # Create message using factory function
        factory_message = create_message(
            msg_id="factory_analysis",
            from_addr="factory@example.com",
            to_addr="user@example.com",
            date=datetime.now(),
            subject="Factory Test Message",
            body="This message was created using the factory function and will be analyzed.",
            attachments=[
                {
                    "filename": "test.txt",
                    "content_type": "text/plain",
                    "content": b"Test file content"
                }
            ]
        )
        
        # Analyze the factory-created message
        result = self.analyzer.analyze(factory_message)
        
        # Verify analysis works with factory-created messages
        assert result.metadata["message_id"] == "factory_analysis"
        assert result.metadata["has_attachments"] is True
        assert len(factory_message.attachments) == 1
        assert factory_message.attachments[0].filename == "test.txt"

    def test_error_handling_integration(self):
        """Test error handling between message and analyzer modules."""
        # Test with minimal valid message
        minimal_message = create_message(
            msg_id="minimal",
            from_addr="test@example.com",
            to_addr="user@example.com",
            date=datetime.now(),
            subject="Test",
            body="Test"
        )
        
        # Should not raise any errors
        result = self.analyzer.analyze(minimal_message)
        assert isinstance(result, EmailAnalysisResult)
        
        # Test insights with empty results
        empty_insights = self.analyzer.get_insights([])
        assert "error" in empty_insights
        assert empty_insights["error"] == "No analysis results provided"

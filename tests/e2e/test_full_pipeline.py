"""
End-to-end tests for the complete email client pipeline.

Pipeline flow: Identity → Ingest → Message → Analyzer
"""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest
from analyzer import EmailAnalyzer
from identity import (
    GmailOAuthHandler,
    IdentityManager,
    SimpleTokenManager,
    create_identity_manager,
)
from ingest import LocalIngestor, get_ingestor
from interface import TokenInfo
from message import create_message


class TestFullPipeline:
    """End-to-end tests for the complete email client pipeline."""

    def setup_method(self):
        """Set up test fixtures for the full pipeline."""
        # Create temporary directory structure
        self.temp_dir = tempfile.mkdtemp()
        self.mail_dir = Path(self.temp_dir) / "mail"
        self.mail_dir.mkdir(parents=True, exist_ok=True)

        # Create email folders
        (self.mail_dir / "INBOX").mkdir(exist_ok=True)
        (self.mail_dir / "Sent").mkdir(exist_ok=True)
        (self.mail_dir / "Important").mkdir(exist_ok=True)

        # Create sample email files
        self._create_sample_emails()

        # Initialize pipeline components
        self.identity_manager = self._setup_identity_manager()
        self.ingestor = LocalIngestor(self.mail_dir)
        self.analyzer = EmailAnalyzer()

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _setup_identity_manager(self) -> IdentityManager:
        """Set up authenticated identity manager."""
        oauth_handler = GmailOAuthHandler(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost:8080/callback",
        )
        token_manager = SimpleTokenManager()

        # Create a valid token
        valid_token = TokenInfo(
            access_token="valid_access_token_12345",
            refresh_token="valid_refresh_token_67890",
            expires_at=(
                datetime.now() + timedelta(hours=1)
            ).timestamp(),  # Use timestamp
            token_type="Bearer",
            scope="https://www.googleapis.com/auth/gmail.readonly",
        )

        # Store the token to simulate authentication
        token_manager.store_token(valid_token)

        return IdentityManager(oauth_handler, token_manager)

    def _create_sample_emails(self):
        """Create sample email files for testing."""
        # Business email in INBOX
        business_email = """From: ceo@company.com
To: employee@company.com
Subject: Quarterly Performance Review
Date: Wed, 01 Aug 2025 09:00:00 +0000
Message-ID: <business001@company.com>

Dear Team,

I'm pleased to announce that we've exceeded our quarterly targets by 15%. 
The project delivery was exceptional and client satisfaction scores are at an all-time high.

Great work everyone!

Best regards,
CEO
"""
        (self.mail_dir / "INBOX" / "business_email.eml").write_text(business_email)

        # Technical email with attachment in INBOX
        tech_email = """From: devops@company.com
To: team@company.com
Subject: System Deployment - Action Required
Date: Wed, 01 Aug 2025 10:30:00 +0000
Message-ID: <tech001@company.com>
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="tech_boundary"

--tech_boundary
Content-Type: text/plain

The new authentication system will be deployed this weekend. Please review the attached documentation and prepare for the migration.

Key points:
- Backup all user credentials
- Test the new OAuth flow
- Update API endpoints

--tech_boundary
Content-Type: application/pdf; name="deployment_guide.pdf"
Content-Disposition: attachment; filename="deployment_guide.pdf"

PDF deployment guide content here...

--tech_boundary--
"""
        (self.mail_dir / "INBOX" / "tech_email.eml").write_text(tech_email)

        # Customer support email in INBOX
        support_email = """From: support@helpdesk.com
To: customer@company.com
Subject: Re: Issue #12345 - Login Problems Resolved
Date: Wed, 01 Aug 2025 14:15:00 +0000
Message-ID: <support001@helpdesk.com>

Dear Customer,

We have successfully resolved the login issues you reported. The problem was caused by a temporary server configuration issue that has now been fixed.

Your account is fully functional again. Please try logging in and let us know if you experience any further difficulties.

Thank you for your patience.

Support Team
"""
        (self.mail_dir / "INBOX" / "support_email.eml").write_text(support_email)

        # Important announcement in Important folder
        announcement_email = """From: hr@company.com
To: all@company.com
Subject: Important: New Security Policies
Date: Wed, 01 Aug 2025 16:00:00 +0000
Message-ID: <announce001@company.com>

All Employees,

Effective immediately, new security policies are in place:

1. Two-factor authentication is now mandatory
2. Password complexity requirements have been updated
3. Regular security training is required

Please review the attached policy document and complete the required training by end of week.

HR Department
"""
        (self.mail_dir / "Important" / "announcement.eml").write_text(
            announcement_email
        )

        # Sent email
        sent_email = """From: employee@company.com
To: client@external.com
Subject: Project Status Update
Date: Wed, 01 Aug 2025 11:45:00 +0000
Message-ID: <sent001@company.com>

Dear Client,

I wanted to provide you with an update on our project progress. We are currently on track to meet all deliverables by the agreed deadline.

Key accomplishments this week:
- Completed user interface design
- Implemented core functionality
- Conducted initial testing

Next steps:
- Final testing phase
- User acceptance testing
- Deployment preparation

Please let me know if you have any questions.

Best regards,
Project Manager
"""
        (self.mail_dir / "Sent" / "sent_email.eml").write_text(sent_email)

    def test_complete_pipeline_flow(self):
        """Test the complete pipeline: Identity → Ingest → Message → Analyzer."""
        # Step 1: Identity - Verify authentication
        stored_token = self.identity_manager.get_stored_token()
        assert stored_token is not None
        assert stored_token.access_token == "valid_access_token_12345"
        assert not self.identity_manager.token_manager.is_token_expired(stored_token)

        # Step 2: Ingest - Get messages from all folders
        all_messages = []
        folders = self.ingestor.get_folders()

        for folder in folders:
            folder_messages = list(self.ingestor.get_messages(folder=folder))
            all_messages.extend(folder_messages)

        assert len(all_messages) >= 5  # We created 5 test emails
        assert len(folders) >= 3  # INBOX, Sent, Important

        # Step 3: Message - Convert ingested messages to standardized format
        standardized_messages = []
        for ingested_msg in all_messages:
            # Convert to standardized message format
            standard_msg = create_message(
                msg_id=f"std_{ingested_msg.id}",
                from_addr=ingested_msg.from_,
                to_addr=ingested_msg.to,
                date=ingested_msg.date,
                subject=f"[PROCESSED] {ingested_msg.subject}",
                body=ingested_msg.body,
                attachments=[
                    {
                        "filename": att.filename,
                        "content_type": att.content_type,
                        "content": att.get_content(),
                    }
                    for att in ingested_msg.attachments
                ],
            )
            standardized_messages.append(standard_msg)

        assert len(standardized_messages) == len(all_messages)

        # Step 4: Analyzer - Analyze all messages
        analysis_results = []
        for message in standardized_messages:
            analysis_result = self.analyzer.analyze(message)
            analysis_results.append(analysis_result)

        assert len(analysis_results) == len(standardized_messages)

        # Step 5: Generate insights from all analyses
        insights = self.analyzer.get_insights(analysis_results)

        # Verify insights
        assert "average_sentiment" in insights
        assert "common_topics" in insights
        assert "total_analyzed" in insights
        assert "average_confidence" in insights
        assert insights["total_analyzed"] == len(analysis_results)

    def test_authenticated_email_search_and_analysis(self):
        """Test searching emails with authentication and analyzing results."""
        # Step 1: Verify authentication - mock validate_token for testing
        with patch.object(
            self.identity_manager.oauth_handler, "validate_token", return_value=True
        ):
            assert self.identity_manager.is_authenticated()

            # Step 2: Search for specific emails
            business_emails = list(
                self.ingestor.search_messages("quarterly", folder="INBOX")
            )
            tech_emails = list(
                self.ingestor.search_messages("deployment", folder="INBOX")
            )
            support_emails = list(
                self.ingestor.search_messages("resolved", folder="INBOX")
            )

            assert len(business_emails) > 0
            assert len(tech_emails) > 0
            assert len(support_emails) > 0

            # Step 3: Create message summaries
            search_summaries = []
            all_search_results = business_emails + tech_emails + support_emails

            for result in all_search_results:
                summary = create_message(
                    msg_id=f"summary_{result.id}",
                    from_addr="system@emailclient.com",
                    to_addr="user@company.com",
                    date=datetime.now(),
                    subject=f"SUMMARY: {result.subject}",
                    body=f"Original from: {result.from_}\nOriginal date: {result.date}\nSummary: {result.body[:100]}...",
                )
                search_summaries.append(summary)

            # Step 4: Analyze summaries
            summary_analyses = []
            for summary in search_summaries:
                analysis = self.analyzer.analyze(summary)
                summary_analyses.append(analysis)

            # Step 5: Generate search insights
            search_insights = self.analyzer.get_insights(summary_analyses)

            assert search_insights["total_analyzed"] == len(search_summaries)
            assert isinstance(search_insights["average_sentiment"], float)

    def test_conversation_thread_analysis(self):
        """Test analyzing conversation threads across the pipeline."""
        # Step 1: Verify authentication
        stored_token = self.identity_manager.get_stored_token()
        assert stored_token is not None

        # Step 2: Get related messages (simulate a conversation thread)
        all_messages = list(self.ingestor.get_messages(folder="INBOX"))

        # Group messages by subject similarity (simple grouping)
        conversation_groups = {}
        for msg in all_messages:
            # Simple grouping by first word of subject
            subject_key = msg.subject.split()[0].lower() if msg.subject else "misc"
            if subject_key not in conversation_groups:
                conversation_groups[subject_key] = []
            conversation_groups[subject_key].append(msg)

        # Step 3: Convert to standardized messages and analyze conversations
        conversation_analyses = []
        for group_name, messages in conversation_groups.items():
            if len(messages) > 1:  # Only analyze actual conversations
                # Convert to standardized format
                std_messages = []
                for msg in messages:
                    std_msg = create_message(
                        msg_id=f"conv_{msg.id}",
                        from_addr=msg.from_,
                        to_addr=msg.to,
                        date=msg.date,
                        subject=msg.subject,
                        body=msg.body,
                    )
                    std_messages.append(std_msg)

                # Analyze as conversation
                conversation_analysis = self.analyzer.analyze_conversation(std_messages)
                conversation_analyses.append(conversation_analysis)

        # Step 4: Verify conversation analysis
        if conversation_analyses:
            for analysis in conversation_analyses:
                assert "message_count" in analysis.metadata
                assert "date_range" in analysis.metadata
                assert analysis.metadata["message_count"] >= 1

    def test_token_refresh_during_pipeline(self):
        """Test token refresh functionality during pipeline execution."""
        # Step 1: Create an expired token
        expired_token = TokenInfo(
            access_token="expired_token",
            refresh_token="valid_refresh_token",
            expires_at=datetime.now().timestamp() - 3600,  # Expired 1 hour ago
            token_type="Bearer",
            scope="https://www.googleapis.com/auth/gmail.readonly",
        )

        self.identity_manager.token_manager.store_token(expired_token)

        # Step 2: Mock successful token refresh
        new_token = TokenInfo(
            access_token="refreshed_access_token",
            refresh_token="valid_refresh_token",
            expires_at=datetime.now().timestamp() + 3600,  # Valid for 1 hour
            token_type="Bearer",
            scope="https://www.googleapis.com/auth/gmail.readonly",
        )

        with patch.object(
            self.identity_manager.oauth_handler, "refresh_token"
        ) as mock_refresh:
            mock_refresh.return_value = new_token

            # Step 3: Attempt to refresh token
            refreshed_token = self.identity_manager.refresh_stored_token()
            assert refreshed_token is not None
            assert refreshed_token.access_token == "refreshed_access_token"

        # Step 4: Continue with pipeline using refreshed token
        messages = list(self.ingestor.get_messages(limit=2))
        assert len(messages) > 0

        # Step 5: Analyze with refreshed authentication
        for message in messages:
            analysis = self.analyzer.analyze(message)
            assert analysis.metadata["message_id"] == message.id

    def test_error_handling_across_pipeline(self):
        """Test error handling across all pipeline components."""
        # Test 1: Authentication failure
        self.identity_manager.token_manager.clear_token()
        stored_token = self.identity_manager.get_stored_token()
        assert stored_token is None

        # Test 2: Invalid folder access
        with pytest.raises(Exception):  # Should be ConnectionError
            list(self.ingestor.get_messages(folder="NonExistentFolder"))

        # Test 3: Invalid message creation
        with pytest.raises(Exception):  # Should be ParsingError
            create_message(
                msg_id="invalid",
                from_addr="test@example.com",
                to_addr="user@example.com",
                date=datetime.now(),
                subject="Test",
                body="Test",
                attachments=[{"filename": "test.txt"}],  # Missing required fields
            )

        # Test 4: Empty analysis
        empty_insights = self.analyzer.get_insights([])
        assert "error" in empty_insights

    def test_full_pipeline_with_factory_functions(self):
        """Test complete pipeline using factory functions."""
        # Step 1: Create identity manager using factory
        factory_identity = create_identity_manager(
            provider="gmail",
            client_id="factory_client",
            client_secret="factory_secret",
            redirect_uri="http://localhost:8080/callback",
        )

        # Mock authentication
        mock_token = TokenInfo(
            access_token="factory_token",
            refresh_token="factory_refresh",
            expires_at=datetime.now().timestamp() + 3600,
            token_type="Bearer",
            scope="https://www.googleapis.com/auth/gmail.readonly",
        )
        factory_identity.store_token(mock_token)

        # Step 2: Create ingestor using factory
        factory_ingestor = get_ingestor()
        # Override with our test directory
        factory_ingestor.mail_dir = self.mail_dir

        # Step 3: Process messages through complete pipeline
        pipeline_results = []

        for folder in factory_ingestor.get_folders():
            for ingested_msg in factory_ingestor.get_messages(folder=folder, limit=2):
                # Create standardized message
                std_msg = create_message(
                    msg_id=f"factory_{ingested_msg.id}",
                    from_addr=ingested_msg.from_,
                    to_addr=ingested_msg.to,
                    date=ingested_msg.date,
                    subject=f"[FACTORY] {ingested_msg.subject}",
                    body=ingested_msg.body,
                )

                # Analyze message
                analysis = self.analyzer.analyze(std_msg)

                pipeline_results.append(
                    {
                        "original_message": ingested_msg,
                        "standardized_message": std_msg,
                        "analysis": analysis,
                        "folder": folder,
                    }
                )

        # Verify pipeline results
        assert len(pipeline_results) > 0

        for result in pipeline_results:
            assert result["standardized_message"].subject.startswith("[FACTORY]")
            assert result["analysis"].metadata["message_id"].startswith("factory_")
            assert "folder" in result

    def test_performance_pipeline(self):
        """Test pipeline performance with multiple messages."""
        import time

        # Step 1: Record start time
        start_time = time.time()

        # Step 2: Process all messages through pipeline
        processed_count = 0

        for folder in self.ingestor.get_folders():
            for message in self.ingestor.get_messages(folder=folder):
                # Convert and analyze
                std_msg = create_message(
                    msg_id=f"perf_{message.id}",
                    from_addr=message.from_,
                    to_addr=message.to,
                    date=message.date,
                    subject=message.subject,
                    body=message.body,
                )

                analysis = self.analyzer.analyze(std_msg)
                processed_count += 1

                # Use the analysis result
                assert analysis.sentiment is not None
                assert analysis.topics is not None
                assert analysis.entities is not None

        # Step 3: Record end time
        end_time = time.time()
        processing_time = end_time - start_time

        # Step 4: Verify performance
        assert processed_count > 0
        assert processing_time < 10.0  # Should complete within 10 seconds

        # Calculate throughput
        messages_per_second = (
            processed_count / processing_time if processing_time > 0 else 0
        )
        assert messages_per_second > 0.1  # At least 0.1 messages per second

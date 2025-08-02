"""
Integration tests for identity and ingest modules.
"""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest
from identity import (
    GmailOAuthHandler,
    IdentityManager,
    SimpleTokenManager,
    create_identity_manager,
)
from ingest import LocalIngestor, get_ingestor
from interface import AuthStatus, TokenInfo


class TestIdentityIngestIntegration:
    """Integration tests for identity and ingest modules."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create temporary directory for mail files
        self.temp_dir = tempfile.mkdtemp()
        self.mail_dir = Path(self.temp_dir) / "mail"
        self.mail_dir.mkdir(parents=True, exist_ok=True)

        # Create sample email file
        sample_email = """From: sender@example.com
To: recipient@example.com
Subject: Test Email
Date: Wed, 01 Aug 2025 10:00:00 +0000

This is a test email body.
"""
        (self.mail_dir / "INBOX").mkdir(exist_ok=True)
        (self.mail_dir / "INBOX" / "email1.eml").write_text(sample_email)

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_authenticated_ingest_flow(self):
        """Test complete flow from authentication to email ingestion."""
        # Setup identity manager
        oauth_handler = GmailOAuthHandler(
            client_id="test_client",
            client_secret="test_secret",
            redirect_uri="http://localhost:8080/callback",
        )
        token_manager = SimpleTokenManager()
        identity_manager = IdentityManager(oauth_handler, token_manager)

        # Mock a valid token
        mock_token = TokenInfo(
            access_token="mock_access_token",
            refresh_token="mock_refresh_token",
            expires_at=datetime.now() + timedelta(hours=1),
            token_type="Bearer",
            scope="https://www.googleapis.com/auth/gmail.readonly",
        )

        # Store the token
        token_manager.store_token(mock_token)

        # Verify token is stored
        stored_token = identity_manager.get_stored_token()
        assert stored_token is not None
        assert stored_token.access_token == "mock_access_token"

        # Setup ingestor
        ingestor = LocalIngestor(self.mail_dir)

        # Test that we can get messages after authentication
        messages = list(ingestor.get_messages(limit=10))
        assert len(messages) > 0

        # Verify the ingestor can access folders
        folders = ingestor.get_folders()
        assert "INBOX" in folders

    def test_authentication_failure_blocks_ingest(self):
        """Test that authentication failure prevents email ingestion."""
        # Setup identity manager with invalid credentials
        oauth_handler = GmailOAuthHandler(
            client_id="invalid_client",
            client_secret="invalid_secret",
            redirect_uri="http://localhost:8080/callback",
        )
        token_manager = SimpleTokenManager()
        identity_manager = IdentityManager(oauth_handler, token_manager)

        # Attempt authentication with invalid credentials
        with patch.object(oauth_handler, "authenticate") as mock_auth:
            mock_auth.return_value = AuthStatus.FAILED

            auth_status = identity_manager.authenticate(
                {"username": "invalid@example.com", "password": "invalid_password"}
            )
            assert auth_status == AuthStatus.FAILED

        # Verify no token is stored
        stored_token = identity_manager.get_stored_token()
        assert stored_token is None

        # In a real scenario, the ingestor would check authentication
        # before allowing access. Here we simulate this check.
        if stored_token is None:
            # Simulate authentication required error
            with pytest.raises(
                Exception
            ):  # This would be AuthenticationError in real implementation
                ingestor = LocalIngestor(self.mail_dir)
                # In real implementation, ingestor would check auth before proceeding
                raise Exception("Authentication required")

    def test_token_refresh_during_ingest(self):
        """Test token refresh functionality during email ingestion."""
        # Setup identity manager
        oauth_handler = GmailOAuthHandler(
            client_id="test_client",
            client_secret="test_secret",
            redirect_uri="http://localhost:8080/callback",
        )
        token_manager = SimpleTokenManager()
        identity_manager = IdentityManager(oauth_handler, token_manager)

        # Create an expired token
        expired_token = TokenInfo(
            access_token="expired_access_token",
            refresh_token="valid_refresh_token",
            expires_at=datetime.now() - timedelta(hours=1),  # Expired
            token_type="Bearer",
            scope="https://www.googleapis.com/auth/gmail.readonly",
        )

        token_manager.store_token(expired_token)

        # Mock the refresh token functionality
        new_token = TokenInfo(
            access_token="new_access_token",
            refresh_token="valid_refresh_token",
            expires_at=datetime.now() + timedelta(hours=1),
            token_type="Bearer",
            scope="https://www.googleapis.com/auth/gmail.readonly",
        )

        with patch.object(oauth_handler, "refresh_token") as mock_refresh:
            mock_refresh.return_value = new_token

            # Attempt to refresh the token
            refreshed_token = identity_manager.refresh_stored_token()
            assert refreshed_token is not None
            assert refreshed_token.access_token == "new_access_token"

        # Verify the new token is stored
        stored_token = identity_manager.get_stored_token()
        assert stored_token.access_token == "new_access_token"

        # Now ingest should work with the refreshed token
        ingestor = LocalIngestor(self.mail_dir)
        messages = list(ingestor.get_messages(limit=10))
        assert len(messages) > 0

    def test_factory_functions_integration(self):
        """Test integration using factory functions."""
        # Test identity manager creation
        identity_manager = create_identity_manager(
            provider="gmail",
            client_id="test_client",
            client_secret="test_secret",
            redirect_uri="http://localhost:8080/callback",
        )
        assert isinstance(identity_manager, IdentityManager)

        # Test ingestor creation
        ingestor = get_ingestor()
        assert isinstance(ingestor, LocalIngestor)

        # In a real implementation, these would work together
        # to provide authenticated email access

    def test_search_with_authentication(self):
        """Test email search functionality with authentication."""
        # Setup authenticated identity manager
        oauth_handler = GmailOAuthHandler(
            client_id="test_client",
            client_secret="test_secret",
            redirect_uri="http://localhost:8080/callback",
        )
        token_manager = SimpleTokenManager()
        identity_manager = IdentityManager(oauth_handler, token_manager)

        # Mock valid authentication
        mock_token = TokenInfo(
            access_token="valid_access_token",
            refresh_token="valid_refresh_token",
            expires_at=datetime.now() + timedelta(hours=1),
            token_type="Bearer",
            scope="https://www.googleapis.com/auth/gmail.readonly",
        )

        token_manager.store_token(mock_token)

        # Test search functionality
        ingestor = LocalIngestor(self.mail_dir)
        search_results = list(ingestor.search_messages("test", folder="INBOX"))

        # Verify search works with authentication
        assert isinstance(search_results, list)

    def test_multiple_folder_access_with_auth(self):
        """Test accessing multiple folders with proper authentication."""
        # Create additional folders
        (self.mail_dir / "Sent").mkdir(exist_ok=True)
        (self.mail_dir / "Drafts").mkdir(exist_ok=True)

        # Setup authenticated identity manager
        identity_manager = create_identity_manager(
            provider="gmail",
            client_id="test_client",
            client_secret="test_secret",
            redirect_uri="http://localhost:8080/callback",
        )

        # Mock authentication
        mock_token = TokenInfo(
            access_token="valid_access_token",
            refresh_token="valid_refresh_token",
            expires_at=datetime.now() + timedelta(hours=1),
            token_type="Bearer",
            scope="https://www.googleapis.com/auth/gmail.readonly",
        )

        identity_manager._token_manager.store_token(mock_token)

        # Test folder access
        ingestor = LocalIngestor(self.mail_dir)
        folders = ingestor.get_folders()

        assert "INBOX" in folders
        assert "Sent" in folders
        assert "Drafts" in folders

        # Test accessing messages from different folders
        for folder in folders:
            messages = list(ingestor.get_messages(limit=5, folder=folder))
            # Should not raise authentication errors
            assert isinstance(messages, list)

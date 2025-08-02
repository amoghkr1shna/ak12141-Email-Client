import time
from unittest.mock import MagicMock, patch

import pytest
from interface import TokenInfo

from identity import (
    GmailOAuthHandler,
    IdentityManager,
    SimpleTokenManager,
    create_identity_manager,
    create_oauth_handler,
    create_token_manager,
)


@pytest.fixture
def token_info() -> TokenInfo:
    """Fixture for sample token info."""
    return TokenInfo(
        access_token="test_access_token",
        refresh_token="test_refresh_token",
        expires_at=int(time.time()) + 3600,
        token_type="Bearer",
    )


@pytest.fixture
def token_manager() -> SimpleTokenManager:
    """Fixture for token manager."""
    return SimpleTokenManager()


@pytest.fixture
def oauth_handler() -> GmailOAuthHandler:
    """Fixture for OAuth handler."""
    return GmailOAuthHandler(
        client_id="test_client_id",
        client_secret="test_client_secret",
        redirect_uri="http://localhost:8080/callback",
    )


class TestSimpleTokenManager:
    """Test cases for SimpleTokenManager."""

    def test_store_and_retrieve_token(self, token_manager: SimpleTokenManager, token_info: TokenInfo) -> None:
        token_manager.store_token(token_info)
        retrieved_token = token_manager.retrieve_token()
        assert retrieved_token == token_info

    def test_clear_token(self, token_manager: SimpleTokenManager, token_info: TokenInfo) -> None:
        token_manager.store_token(token_info)
        token_manager.clear_token()
        assert token_manager.retrieve_token() is None

    def test_is_token_expired(self, token_manager: SimpleTokenManager) -> None:
        expired_token = TokenInfo(
            access_token="test",
            expires_at=int(time.time()) - 3600
        )
        assert token_manager.is_token_expired(expired_token) is True

        valid_token = TokenInfo(
            access_token="test",
            expires_at=int(time.time()) + 3600
        )
        assert token_manager.is_token_expired(valid_token) is False


class TestGmailOAuthHandler:
    """Test cases for GmailOAuthHandler."""

    def test_initialization(self, oauth_handler: GmailOAuthHandler) -> None:
        assert oauth_handler.client_id == "test_client_id"
        assert oauth_handler.client_secret == "test_client_secret"
        assert oauth_handler.redirect_uri == "http://localhost:8080/callback"

    def test_generate_authorization_url(self, oauth_handler: GmailOAuthHandler) -> None:
        url = oauth_handler.get_authorization_url()
        assert "https://accounts.google.com/o/oauth2/v2/auth" in url
        assert "client_id=test_client_id" in url
        assert "redirect_uri=http://localhost:8080/callback" in url

    @patch("requests.post")
    def test_refresh_token(self, mock_post: MagicMock, oauth_handler: GmailOAuthHandler) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "new_access_token",
            "expires_in": 3600,
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        token = oauth_handler.refresh_token("test_refresh_token")
        assert token.access_token == "new_access_token"
        assert token.refresh_token == "test_refresh_token"


class TestIdentityManager:
    """Test cases for IdentityManager."""

    @pytest.fixture
    def identity_manager(self, oauth_handler: GmailOAuthHandler, token_manager: SimpleTokenManager) -> IdentityManager:
        return IdentityManager(oauth_handler, token_manager)

    def test_store_and_get_token(self, identity_manager: IdentityManager, token_info: TokenInfo) -> None:
        identity_manager.store_token(token_info)
        stored_token = identity_manager.get_stored_token()
        assert stored_token == token_info

    @patch.object(GmailOAuthHandler, "validate_token")
    def test_is_authenticated(self, mock_validate: MagicMock, identity_manager: IdentityManager, token_info: TokenInfo) -> None:
        mock_validate.return_value = True
        identity_manager.store_token(token_info)
        assert identity_manager.is_authenticated() is True

        mock_validate.return_value = False
        assert identity_manager.is_authenticated() is False


class TestFactoryFunctions:
    """Test cases for factory functions."""

    def test_create_oauth_handler(self) -> None:
        handler = create_oauth_handler(
            provider="gmail",
            client_id="test_id",
            client_secret="test_secret",
            redirect_uri="test_uri"
        )
        assert isinstance(handler, GmailOAuthHandler)

        with pytest.raises(ValueError):
            create_oauth_handler(provider="invalid")

    def test_create_token_manager(self) -> None:
        manager = create_token_manager()
        assert isinstance(manager, SimpleTokenManager)

    def test_create_identity_manager(self) -> None:
        manager = create_identity_manager(
            provider="gmail",
            client_id="test_id",
            client_secret="test_secret",
            redirect_uri="test_uri"
        )
        assert isinstance(manager, IdentityManager)
        assert isinstance(manager.oauth_handler, GmailOAuthHandler)
        assert isinstance(manager.token_manager, SimpleTokenManager)
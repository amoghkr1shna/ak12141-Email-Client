"""
Identity module for OAuth authentication.
"""

import time
import base64
import hashlib
import secrets
from typing import Dict, Any, Optional

from ...interface.src.interface import (
    AuthStatus, TokenInfo, OAuthHandler, TokenManager,
    AuthenticationError
)


class SimpleTokenManager(TokenManager):
    """Simple in-memory token manager."""
    
    def __init__(self):
        self._current_token: Optional[TokenInfo] = None
    
    def store_token(self, token: TokenInfo) -> None:
        """Store token in memory."""
        self._current_token = token
    
    def retrieve_token(self) -> Optional[TokenInfo]:
        """Retrieve stored token."""
        return self._current_token
    
    def clear_token(self) -> None:
        """Clear stored token."""
        self._current_token = None
    
    def is_token_expired(self, token: TokenInfo) -> bool:
        """Check if token is expired."""
        if token.expires_at is None:
            return False
        
        # Add 5-minute buffer before expiration
        buffer_time = 300  # 5 minutes in seconds
        return time.time() >= (token.expires_at - buffer_time)


class GmailOAuthHandler(OAuthHandler):
    """Gmail OAuth handler implementation."""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
    
    def _generate_state(self) -> str:
        """Generate random state parameter for OAuth flow."""
        return secrets.token_urlsafe(32)
    
    def _generate_code_verifier(self) -> str:
        """Generate PKCE code verifier."""
        return secrets.token_urlsafe(32)
    
    def _generate_code_challenge(self, code_verifier: str) -> str:
        """Generate PKCE code challenge."""
        sha256_hash = hashlib.sha256(code_verifier.encode()).digest()
        return base64.urlsafe_b64encode(sha256_hash).decode().rstrip('=')
    
    def authenticate(self, credentials: Dict[str, Any]) -> AuthStatus:
        """Authenticate using OAuth flow."""
        try:
            # Check if we have stored credentials
            if "access_token" in credentials:
                token = TokenInfo(
                    access_token=credentials["access_token"],
                    refresh_token=credentials.get("refresh_token"),
                    expires_at=credentials.get("expires_at"),
                    token_type=credentials.get("token_type", "Bearer")
                )
                
                if self.validate_token(token):
                    return AuthStatus.AUTHENTICATED
                elif token.refresh_token:
                    # Try to refresh the token
                    new_token = self.refresh_token(token.refresh_token)
                    if new_token:
                        return AuthStatus.AUTHENTICATED
                    else:
                        return AuthStatus.EXPIRED
                else:
                    return AuthStatus.EXPIRED
            
            return AuthStatus.UNAUTHENTICATED
            
        except Exception as e:
            raise AuthenticationError(f"Authentication failed: {e}")
    
    def refresh_token(self, refresh_token: str) -> TokenInfo:
        """Refresh access token using refresh token."""
        try:
            import requests
            
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token"
            }
            
            response = requests.post(self.token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            return TokenInfo(
                access_token=token_data["access_token"],
                refresh_token=refresh_token,  # Keep the original refresh token
                expires_at=int(time.time()) + token_data.get("expires_in", 3600),
                token_type=token_data.get("token_type", "Bearer")
            )
            
        except Exception as e:
            raise AuthenticationError(f"Token refresh failed: {e}")
    
    def validate_token(self, token: TokenInfo) -> bool:
        """Validate if token is still valid."""
        try:
            import requests
            
            headers = {
                "Authorization": f"{token.token_type} {token.access_token}"
            }
            
            # Test the token with Gmail API
            response = requests.get(
                "https://gmail.googleapis.com/gmail/v1/users/me/profile",
                headers=headers
            )
            
            return response.status_code == 200
            
        except Exception:
            return False
    
    def get_authorization_url(self, scope: str = "https://www.googleapis.com/auth/gmail.readonly") -> str:
        """Generate OAuth authorization URL."""
        state = self._generate_state()
        code_verifier = self._generate_code_verifier()
        code_challenge = self._generate_code_challenge(code_verifier)
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": scope,
            "response_type": "code",
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256"
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.auth_url}?{query_string}"
    
    def exchange_code_for_token(self, authorization_code: str, code_verifier: str) -> TokenInfo:
        """Exchange authorization code for access token."""
        try:
            import requests
            
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": authorization_code,
                "code_verifier": code_verifier,
                "grant_type": "authorization_code",
                "redirect_uri": self.redirect_uri
            }
            
            response = requests.post(self.token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            return TokenInfo(
                access_token=token_data["access_token"],
                refresh_token=token_data.get("refresh_token"),
                expires_at=int(time.time()) + token_data.get("expires_in", 3600),
                token_type=token_data.get("token_type", "Bearer")
            )
            
        except Exception as e:
            raise AuthenticationError(f"Token exchange failed: {e}")


class IdentityManager:
    """Main identity manager coordinating OAuth and token management."""
    
    def __init__(self, oauth_handler: OAuthHandler, token_manager: TokenManager):
        self.oauth_handler = oauth_handler
        self.token_manager = token_manager
    
    def authenticate(self, credentials: Dict[str, Any]) -> AuthStatus:
        """Authenticate with email service."""
        return self.oauth_handler.authenticate(credentials)
    
    def get_stored_token(self) -> Optional[TokenInfo]:
        """Get stored token if available and valid."""
        token = self.token_manager.retrieve_token()
        if token and not self.token_manager.is_token_expired(token):
            return token
        return None
    
    def refresh_stored_token(self) -> Optional[TokenInfo]:
        """Refresh stored token if possible."""
        token = self.token_manager.retrieve_token()
        if token and token.refresh_token:
            try:
                new_token = self.oauth_handler.refresh_token(token.refresh_token)
                self.token_manager.store_token(new_token)
                return new_token
            except AuthenticationError:
                self.token_manager.clear_token()
                return None
        return None
    
    def store_token(self, token: TokenInfo) -> None:
        """Store token."""
        self.token_manager.store_token(token)
    
    def clear_stored_token(self) -> None:
        """Clear stored token."""
        self.token_manager.clear_token()
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        token = self.get_stored_token()
        if token:
            return self.oauth_handler.validate_token(token)
        return False


# Factory functions
def create_oauth_handler(provider: str = "gmail", **kwargs) -> OAuthHandler:
    """Create OAuth handler for specified provider."""
    if provider.lower() == "gmail":
        return GmailOAuthHandler(**kwargs)
    else:
        raise ValueError(f"Unsupported OAuth provider: {provider}")


def create_token_manager() -> TokenManager:
    """Create simple token manager."""
    return SimpleTokenManager()


def create_identity_manager(
    provider: str = "gmail",
    **oauth_kwargs
) -> IdentityManager:
    """Create identity manager with OAuth handler and token manager."""
    oauth_handler = create_oauth_handler(provider, **oauth_kwargs)
    token_manager = create_token_manager()
    return IdentityManager(oauth_handler, token_manager)


    # Create identity manager
identity_manager = create_identity_manager(
    provider="gmail",
    client_id="your_client_id",
    client_secret="your_client_secret",
    redirect_uri="http://localhost:8080/callback"
)

# # Get OAuth URL
# auth_url = identity_manager.oauth_handler.get_authorization_url()
# print(f"Visit: {auth_url}")

# # Exchange code for token
# token = identity_manager.oauth_handler.exchange_code_for_token(code, verifier)
# identity_manager.store_token(token)
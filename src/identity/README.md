# Email Client Identity Module

This module provides OAuth authentication and token management functionality for the email client.

## Features

- Gmail OAuth 2.0 authentication
- Secure token storage and management
- Automatic token refresh capabilities
- Token validation and expiration handling
- Factory functions for creating identity components

## Classes

- `IdentityManager`: Main coordinator for OAuth and token management
- `GmailOAuthHandler`: Gmail-specific OAuth 2.0 implementation
- `SimpleTokenManager`: In-memory token storage implementation

## Functions

- `create_identity_manager()`: Factory function to create IdentityManager instances
- `create_oauth_handler()`: Factory function to create OAuth handler instances
- `create_token_manager()`: Factory function to create token manager instances

## Usage

### Basic Setup

```python
from identity import create_identity_manager

# Create identity manager for Gmail
identity_manager = create_identity_manager(
    provider="gmail",
    client_id="your_client_id",
    client_secret="your_client_secret",
    redirect_uri="http://localhost:8080/callback"
)
```

### Authentication Flow

```python
# Check if user is already authenticated
if identity_manager.is_authenticated():
    print("User is authenticated")
else:
    # Perform authentication with credentials
    credentials = {
        "access_token": "your_access_token",
        "refresh_token": "your_refresh_token",
        "expires_at": 1234567890
    }
    
    status = identity_manager.authenticate(credentials)
    print(f"Authentication status: {status}")
```

### Token Management

```python
# Get stored token
token = identity_manager.get_stored_token()
if token:
    print(f"Access token: {token.access_token}")

# Refresh expired token
refreshed_token = identity_manager.refresh_stored_token()
if refreshed_token:
    print("Token refreshed successfully")
```

### OAuth Authorization URL

```python
from identity import create_oauth_handler

oauth_handler = create_oauth_handler(
    provider="gmail",
    client_id="your_client_id",
    client_secret="your_client_secret",
    redirect_uri="http://localhost:8080/callback"
)

# Get authorization URL for user to visit
auth_url = oauth_handler.get_authorization_url()
print(f"Visit this URL to authorize: {auth_url}")
```

## Security Features

- **State Parameter**: Prevents CSRF attacks during OAuth flow  
- **Token Expiration Buffer**: 5-minute safety buffer before token expiration
- **Secure Token Storage**: In-memory storage with proper cleanup methods
- **Automatic Token Refresh**: Handles expired tokens transparently

## Dependencies

- `requests`: For HTTP requests to OAuth endpoints
- `email-client-interface`: For protocol definitions and interfaces
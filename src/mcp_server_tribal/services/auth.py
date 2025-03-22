# filename: mcp_server_tribal/services/auth.py
#
# Copyright (c) 2025 Agentience.ai
# Author: Troy Molander
# License: MIT License - See LICENSE file for details
#
# Version: 0.1.0

"""Authentication service for the API."""


import os
from datetime import datetime, timedelta
from typing import Dict, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel

# Constants
SECRET_KEY = os.environ.get("SECRET_KEY", "insecure-dev-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Token(BaseModel):
    """Token response model."""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data model."""

    username: Optional[str] = None


# Determine if authentication is required
require_auth = os.environ.get("REQUIRE_AUTH", "false").lower() == "true"

# Create OAuth2 scheme conditionally based on authentication requirements
if require_auth:
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
else:
    # When auth is disabled, use a scheme that doesn't enforce auth
    from fastapi.security import OAuth2
    from fastapi.openapi.models import OAuthFlows

    class OptionalOAuth2PasswordBearer(OAuth2):
        """OAuth2 password bearer scheme that makes token optional."""

        def __init__(self, tokenUrl: str):
            """Initialize the scheme."""
            flows = OAuthFlows(password={"tokenUrl": tokenUrl, "scopes": {}})
            super().__init__(flows=flows, scheme_name="OAuth2PasswordBearer")

        async def __call__(self, request: Request) -> Optional[str]:
            """Return None for the token to make it optional."""
            return None

    oauth2_scheme = OptionalOAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time

    Returns:
        JWT token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """
    Validate the access token and extract the current user.

    Args:
        token: JWT token

    Returns:
        Username from the token

    Raises:
        HTTPException: If the token is invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    return token_data.username


# API key authentication - a simpler alternative to OAuth2
API_KEYS = {
    # In production, these would be stored securely, e.g., in a database
    os.environ.get("API_KEY", "dev-api-key"): "default-user"
}


async def verify_api_key(api_key: str) -> Optional[str]:
    """
    Verify an API key and return the associated username.

    Args:
        api_key: The API key to verify

    Returns:
        The username associated with the API key, or None if invalid
    """
    return API_KEYS.get(api_key)


class ApiKeyAuth:
    """API key authentication handler."""

    def __init__(self, require_auth: bool = True):
        """
        Initialize the API key authentication handler.

        Args:
            require_auth: Whether to require authentication
        """
        self.require_auth = require_auth

    async def __call__(self, api_key: str = Depends(oauth2_scheme)) -> str:
        """
        Validate the API key and return the user.

        Args:
            api_key: The API key to validate

        Returns:
            The username associated with the API key

        Raises:
            HTTPException: If the API key is invalid and authentication is required
        """
        # Skip authentication if not required
        if not self.require_auth:
            return "anonymous"

        username = await verify_api_key(api_key)
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username

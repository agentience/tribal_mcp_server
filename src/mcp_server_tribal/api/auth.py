# filename: mcp_server_tribal/api/auth.py
#
# Copyright (c) 2025 Agentience.ai
# Author: Troy Molander
# License: MIT License - See LICENSE file for details
#
# Version: 0.1.0

"""Authentication routes for the API."""


import os
from datetime import timedelta
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ..services.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    Token,
    create_access_token,
    verify_api_key,
)

# Get authentication configuration
require_auth = os.environ.get("REQUIRE_AUTH", "false").lower() == "true"

# Only create auth routes if authentication is required
router = APIRouter(tags=["auth"])

if require_auth:

    @router.post("/token", response_model=Token)
    async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
    ) -> Dict:
        """
        Generate an access token from username and password.

        This endpoint is primarily for development purposes. For production,
        API key authentication is recommended.

        Args:
            form_data: OAuth2 password request form

        Returns:
            A dictionary with the access token and token type

        Raises:
            HTTPException: If authentication fails
        """
        # In a real application, you would validate against a database
        # For this example, we use the API keys as "passwords"
        username = await verify_api_key(form_data.password)

        if not username or username != form_data.username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": username}, expires_delta=access_token_expires
        )

        return {"access_token": access_token, "token_type": "bearer"}

else:

    @router.get("/status")
    async def auth_status() -> Dict:
        """Return the authentication status."""
        return {
            "auth_required": False,
            "message": "Authentication is disabled for local development",
        }

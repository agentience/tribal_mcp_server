# filename: mcp_server_tribal/api/__init__.py
#
# Copyright (c) 2025 Agentience.ai
# Author: Troy Molander
# License: MIT License - See LICENSE file for details
#
# Version: 0.1.0

"""API module for the MCP server."""


from fastapi import APIRouter

from .auth import router as auth_router
from .errors import router as errors_router

api_router = APIRouter()
api_router.include_router(errors_router)
api_router.include_router(auth_router)

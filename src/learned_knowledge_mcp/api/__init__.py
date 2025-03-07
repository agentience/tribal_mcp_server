"""API module for the MCP server."""

from fastapi import APIRouter

from .auth import router as auth_router
from .errors import router as errors_router

api_router = APIRouter()
api_router.include_router(errors_router)
api_router.include_router(auth_router)
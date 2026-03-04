"""
Health check endpoint
"""
import os
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    version: str
    env: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    Returns application status, version, and environment
    """
    return HealthResponse(
        status="ok",
        version="1.0.0",
        env=os.getenv("APP_ENV", "unknown")
    )

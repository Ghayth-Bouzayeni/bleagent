"""
FastAPI main application entry point
BLE Agent Backend for IoT Smart Parking System
"""
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import health, observations, config
from app.services.webhook_dispatcher import start_webhook_dispatcher, stop_webhook_dispatcher

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler
    Initializes database tables on startup
    """
    # Startup: Initialize database
    print("🚀 Initializing database...")
    await init_db()
    print("✅ Database initialized successfully")

    # Startup: launch periodic webhook dispatcher if configured
    app.state.webhook_dispatcher = start_webhook_dispatcher()
    
    yield
    
    # Shutdown: cleanup if needed
    await stop_webhook_dispatcher(getattr(app.state, "webhook_dispatcher", None))
    print("👋 Shutting down application")


# Create FastAPI application
app = FastAPI(
    title="BLE Agent Backend",
    description="Backend API for IoT smart car parking system with BLE tag detection",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware (allow all origins for MVP)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(observations.router)
app.include_router(config.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "BLE Agent Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

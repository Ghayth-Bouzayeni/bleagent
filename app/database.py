"""
Database configuration and session management
Uses async SQLAlchemy with asyncpg for PostgreSQL
"""
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging in development
    pool_size=10,
    max_overflow=20,
    connect_args={
        "ssl": "require",  # Force SSL connection for Supabase
        "timeout": 30,  # Increase timeout to 30 seconds
    }
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for declarative models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    Dependency to get async database session
    Use with FastAPI Depends()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """
    Initialize database tables
    Called on application startup
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

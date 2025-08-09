"""
Database configuration for the chess prep agent.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

# Database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://chess_user:chess_pass@localhost:5432/chess_prep_db"
)

# For synchronous operations (migrations, etc.)
SYNC_DATABASE_URL = os.getenv(
    "SYNC_DATABASE_URL",
    "postgresql://chess_user:chess_pass@localhost:5432/chess_prep_db"
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True if os.getenv("DEBUG") == "1" else False,
    future=True
)

# Create sync engine for migrations
sync_engine = create_engine(SYNC_DATABASE_URL, echo=True if os.getenv("DEBUG") == "1" else False)

# Session makers
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# Base class for models
Base = declarative_base()


# Dependency to get database session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Sync session for migrations
def get_sync_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

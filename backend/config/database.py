"""
Database connection configuration and management.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import os
import logging

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and sessions."""

    def __init__(self):
        self.engine: AsyncEngine = None
        self.session_factory: sessionmaker = None

    def initialize(self, database_url: str = None, echo: bool = False):
        """Initialize the database connection."""
        if not database_url:
            database_url = os.getenv(
                "DATABASE_URL",
                "sqlite+aiosqlite:///./chess_prep.db",  # Fallback to SQLite
            )

        # Create async engine
        if "sqlite" in database_url:
            # SQLite-specific configuration
            self.engine = create_async_engine(
                database_url,
                echo=echo,
                poolclass=StaticPool,
                connect_args={"check_same_thread": False},
            )
        else:
            # PostgreSQL configuration
            self.engine = create_async_engine(
                database_url,
                echo=echo,
                pool_size=20,
                max_overflow=0,
                pool_pre_ping=True,
                pool_recycle=300,
            )

        # Create session factory
        self.session_factory = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

        logger.info(f"Database initialized: {database_url}")

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session."""
        if not self.session_factory:
            raise RuntimeError("Database not initialized")

        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def close(self):
        """Close database connections."""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connections closed")

    async def health_check(self) -> bool:
        """Check database health."""
        try:
            async with self.get_session() as session:
                await session.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global database manager instance
db_manager = DatabaseManager()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async with db_manager.get_session() as session:
        yield session


async def init_database():
    """Initialize database tables."""
    try:
        # Import models to ensure they're registered
        from database.models import Base

        # Create all tables
        async with db_manager.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logger.info("Database tables initialized")
    except Exception as e:
        logger.error(f"Error initializing database tables: {e}")
        raise

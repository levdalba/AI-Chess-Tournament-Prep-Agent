"""
Database initialization and migration setup.
"""

import os
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine

from .config import SYNC_DATABASE_URL, Base
from .models import *  # Import all models


def init_database():
    """Initialize the database with all tables."""
    try:
        # Create engine
        engine = create_engine(SYNC_DATABASE_URL)
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("Database tables created successfully!")
        
    except Exception as e:
        print(f"Error creating database tables: {e}")


def run_migrations():
    """Run Alembic migrations."""
    try:
        # Get the directory of this file
        current_dir = os.path.dirname(__file__)
        
        # Path to alembic.ini (should be in backend directory)
        alembic_ini_path = os.path.join(os.path.dirname(current_dir), "alembic.ini")
        
        # Create Alembic config
        alembic_cfg = Config(alembic_ini_path)
        
        # Run migrations
        command.upgrade(alembic_cfg, "head")
        
        print("Database migrations completed successfully!")
        
    except Exception as e:
        print(f"Error running migrations: {e}")


def create_migration(message: str):
    """Create a new migration."""
    try:
        current_dir = os.path.dirname(__file__)
        alembic_ini_path = os.path.join(os.path.dirname(current_dir), "alembic.ini")
        
        alembic_cfg = Config(alembic_ini_path)
        
        command.revision(alembic_cfg, message=message, autogenerate=True)
        
        print(f"Migration '{message}' created successfully!")
        
    except Exception as e:
        print(f"Error creating migration: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m database.init [init|migrate|create_migration 'message']")
        sys.exit(1)
    
    command_arg = sys.argv[1]
    
    if command_arg == "init":
        init_database()
    elif command_arg == "migrate":
        run_migrations()
    elif command_arg == "create_migration" and len(sys.argv) > 2:
        message = sys.argv[2]
        create_migration(message)
    else:
        print("Invalid command. Use 'init', 'migrate', or 'create_migration \"message\"'")
        sys.exit(1)

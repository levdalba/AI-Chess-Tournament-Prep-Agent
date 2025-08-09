"""
Shared models, utilities, and constants for the Chess Tournament Prep Agent.

This module contains all shared code that is used by both the frontend and backend,
including data models, utility functions, and application constants.
"""

from .models import (
    GameResult,
    TimeControl,
    Player,
    GameMetadata,
    Move,
    Game,
    Opening,
    WeakPoint,
    PrepPlan,
    User,
)

from .utils import (
    ChessUtils,
    ValidationUtils,
    FileUtils,
)

from .constants import *

__version__ = "1.0.0"
__all__ = [
    # Models
    "GameResult",
    "TimeControl", 
    "Player",
    "GameMetadata",
    "Move",
    "Game",
    "Opening",
    "WeakPoint",
    "PrepPlan",
    "User",
    # Utils
    "ChessUtils",
    "ValidationUtils", 
    "FileUtils",
]

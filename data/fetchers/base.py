"""
Base classes and interfaces for chess data fetching.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, AsyncGenerator, Union
from dataclasses import dataclass
from datetime import datetime, date
import asyncio
from enum import Enum

from pydantic import BaseModel


class Platform(str, Enum):
    """Chess platforms we support."""
    CHESS_COM = "chess.com"
    LICHESS = "lichess.org"
    FIDE = "fide"
    TWIC = "twic"  # The Week in Chess
    PGN_MENTOR = "pgnmentor"


class TimeClass(str, Enum):
    """Time control classifications."""
    BULLET = "bullet"
    BLITZ = "blitz"
    RAPID = "rapid"
    CLASSICAL = "classical"
    CORRESPONDENCE = "correspondence"


@dataclass
class FetchRequest:
    """Request parameters for fetching games."""
    username: str
    platform: Platform
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    time_classes: Optional[List[TimeClass]] = None
    max_games: Optional[int] = None
    include_analysis: bool = False


@dataclass
class FetchResult:
    """Result of a fetch operation."""
    success: bool
    games_count: int
    pgn_content: str
    metadata: Dict[str, Any]
    errors: List[str]
    source_info: Dict[str, Any]


class RateLimiter:
    """Simple rate limiter for API requests."""
    
    def __init__(self, requests_per_second: float = 1.0):
        self.requests_per_second = requests_per_second
        self.last_request_time = 0.0
    
    async def wait(self):
        """Wait if necessary to respect rate limits."""
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self.last_request_time
        min_interval = 1.0 / self.requests_per_second
        
        if time_since_last < min_interval:
            await asyncio.sleep(min_interval - time_since_last)
        
        self.last_request_time = asyncio.get_event_loop().time()


class BaseFetcher(ABC):
    """Abstract base class for chess game fetchers."""
    
    def __init__(self, rate_limit: float = 1.0):
        self.rate_limiter = RateLimiter(rate_limit)
        self.session = None  # Will be set by implementing classes
    
    @abstractmethod
    async def fetch_games(self, request: FetchRequest) -> FetchResult:
        """Fetch games for a player."""
        pass
    
    @abstractmethod
    async def get_player_info(self, username: str) -> Optional[Dict[str, Any]]:
        """Get basic player information."""
        pass
    
    @abstractmethod
    def supports_platform(self, platform: Platform) -> bool:
        """Check if this fetcher supports the given platform."""
        pass
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()


class FetcherRegistry:
    """Registry for managing different fetchers."""
    
    def __init__(self):
        self._fetchers: Dict[Platform, BaseFetcher] = {}
    
    def register(self, platform: Platform, fetcher: BaseFetcher):
        """Register a fetcher for a platform."""
        self._fetchers[platform] = fetcher
    
    def get_fetcher(self, platform: Platform) -> Optional[BaseFetcher]:
        """Get a fetcher for a platform."""
        return self._fetchers.get(platform)
    
    def get_supported_platforms(self) -> List[Platform]:
        """Get list of supported platforms."""
        return list(self._fetchers.keys())


class GameFilter:
    """Filter games based on various criteria."""
    
    def __init__(self, 
                 min_rating: Optional[int] = None,
                 max_rating: Optional[int] = None,
                 time_classes: Optional[List[TimeClass]] = None,
                 color: Optional[str] = None,
                 result: Optional[str] = None):
        self.min_rating = min_rating
        self.max_rating = max_rating
        self.time_classes = time_classes or []
        self.color = color  # 'white', 'black', or None for both
        self.result = result  # '1-0', '0-1', '1/2-1/2', or None
    
    def should_include(self, game_metadata: Dict[str, Any]) -> bool:
        """Check if a game should be included based on filters."""
        # Implement filtering logic
        if self.min_rating and game_metadata.get('rating', 0) < self.min_rating:
            return False
        
        if self.max_rating and game_metadata.get('rating', 9999) > self.max_rating:
            return False
        
        if self.time_classes:
            game_time_class = game_metadata.get('time_class')
            if game_time_class not in self.time_classes:
                return False
        
        if self.color and game_metadata.get('color') != self.color:
            return False
        
        if self.result and game_metadata.get('result') != self.result:
            return False
        
        return True

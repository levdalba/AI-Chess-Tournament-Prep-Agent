"""
Chess.com API fetcher for player games.
Official API documentation: https://www.chess.com/news/view/published-data-api
"""

import asyncio
import json
from datetime import datetime, date
from typing import List, Optional, Dict, Any
import calendar

import aiohttp
import backoff
from .base import BaseFetcher, FetchRequest, FetchResult, Platform, TimeClass


class ChessComFetcher(BaseFetcher):
    """Fetcher for Chess.com games using their public API."""
    
    BASE_URL = "https://api.chess.com/pub"
    
    def __init__(self):
        super().__init__(rate_limit=1.0)  # Chess.com asks for max 1 req/sec
    
    def supports_platform(self, platform: Platform) -> bool:
        """Check if this fetcher supports the given platform."""
        return platform == Platform.CHESS_COM
    
    async def __aenter__(self):
        """Initialize aiohttp session."""
        timeout = aiohttp.ClientTimeout(total=30)
        headers = {
            'User-Agent': 'AI-Chess-Tournament-Prep-Agent/1.0 (Educational Purpose)',
        }
        self.session = aiohttp.ClientSession(timeout=timeout, headers=headers)
        return self
    
    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=3,
        max_time=60
    )
    async def _make_request(self, url: str) -> Dict[str, Any]:
        """Make a rate-limited request to Chess.com API."""
        await self.rate_limiter.wait()
        
        async with self.session.get(url) as response:
            if response.status == 429:  # Rate limited
                await asyncio.sleep(60)  # Wait 1 minute
                raise aiohttp.ClientError("Rate limited")
            
            if response.status != 200:
                raise aiohttp.ClientError(f"HTTP {response.status}: {await response.text()}")
            
            return await response.json()
    
    async def get_player_info(self, username: str) -> Optional[Dict[str, Any]]:
        """Get player profile information."""
        try:
            url = f"{self.BASE_URL}/player/{username.lower()}"
            data = await self._make_request(url)
            
            return {
                'username': data.get('username'),
                'name': data.get('name'),
                'title': data.get('title'),
                'followers': data.get('followers'),
                'country': data.get('country'),
                'joined': data.get('joined'),
                'last_online': data.get('last_online'),
                'avatar': data.get('avatar'),
                'platform': Platform.CHESS_COM
            }
        except Exception as e:
            print(f"Error fetching player info for {username}: {e}")
            return None
    
    async def get_player_stats(self, username: str) -> Optional[Dict[str, Any]]:
        """Get player ratings and statistics."""
        try:
            url = f"{self.BASE_URL}/player/{username.lower()}/stats"
            return await self._make_request(url)
        except Exception as e:
            print(f"Error fetching player stats for {username}: {e}")
            return None
    
    async def get_game_archives(self, username: str) -> List[str]:
        """Get list of available game archives for a player."""
        try:
            url = f"{self.BASE_URL}/player/{username.lower()}/games/archives"
            data = await self._make_request(url)
            return data.get('archives', [])
        except Exception as e:
            print(f"Error fetching game archives for {username}: {e}")
            return []
    
    def _filter_archives_by_date(self, archives: List[str], 
                                start_date: Optional[date] = None, 
                                end_date: Optional[date] = None) -> List[str]:
        """Filter archives by date range."""
        if not start_date and not end_date:
            return archives
        
        filtered = []
        for archive_url in archives:
            # Extract year/month from URL: .../games/2023/01
            parts = archive_url.split('/')
            if len(parts) >= 2:
                try:
                    year = int(parts[-2])
                    month = int(parts[-1])
                    archive_date = date(year, month, 1)
                    
                    # Check if archive falls within date range
                    if start_date and archive_date < date(start_date.year, start_date.month, 1):
                        continue
                    if end_date and archive_date > date(end_date.year, end_date.month, 1):
                        continue
                    
                    filtered.append(archive_url)
                except ValueError:
                    # Invalid date format, skip
                    continue
        
        return filtered
    
    def _map_chess_com_time_class(self, time_class: str) -> TimeClass:
        """Map Chess.com time class to our enum."""
        mapping = {
            'bullet': TimeClass.BULLET,
            'blitz': TimeClass.BLITZ,
            'rapid': TimeClass.RAPID,
            'daily': TimeClass.CORRESPONDENCE,
        }
        return mapping.get(time_class.lower(), TimeClass.RAPID)
    
    def _should_include_game(self, game: Dict[str, Any], 
                           request: FetchRequest, 
                           username: str) -> bool:
        """Check if a game should be included based on request criteria."""
        # Filter by time class
        if request.time_classes:
            game_time_class = self._map_chess_com_time_class(game.get('time_class', ''))
            if game_time_class not in request.time_classes:
                return False
        
        # Filter by date
        if request.start_date or request.end_date:
            game_timestamp = game.get('end_time', 0)
            game_date = datetime.fromtimestamp(game_timestamp).date()
            
            if request.start_date and game_date < request.start_date:
                return False
            if request.end_date and game_date > request.end_date:
                return False
        
        return True
    
    async def fetch_games(self, request: FetchRequest) -> FetchResult:
        """Fetch games for a Chess.com player."""
        if not self.supports_platform(request.platform):
            return FetchResult(
                success=False,
                games_count=0,
                pgn_content="",
                metadata={},
                errors=[f"Platform {request.platform} not supported"],
                source_info={}
            )
        
        username = request.username.lower()
        errors = []
        all_pgns = []
        games_count = 0
        
        try:
            # Get player info first
            player_info = await self.get_player_info(username)
            if not player_info:
                return FetchResult(
                    success=False,
                    games_count=0,
                    pgn_content="",
                    metadata={},
                    errors=[f"Player {username} not found"],
                    source_info={}
                )
            
            # Get available archives
            archives = await self.get_game_archives(username)
            if not archives:
                return FetchResult(
                    success=False,
                    games_count=0,
                    pgn_content="",
                    metadata=player_info,
                    errors=[f"No game archives found for {username}"],
                    source_info={}
                )
            
            # Filter archives by date
            filtered_archives = self._filter_archives_by_date(
                archives, request.start_date, request.end_date
            )
            
            # Sort archives in reverse chronological order (newest first)
            filtered_archives.sort(reverse=True)
            
            # Process each archive
            for archive_url in filtered_archives:
                try:
                    archive_data = await self._make_request(archive_url)
                    games = archive_data.get('games', [])
                    
                    for game in games:
                        if request.max_games and games_count >= request.max_games:
                            break
                        
                        if self._should_include_game(game, request, username):
                            pgn = game.get('pgn', '')
                            if pgn:
                                all_pgns.append(pgn)
                                games_count += 1
                    
                    if request.max_games and games_count >= request.max_games:
                        break
                        
                except Exception as e:
                    errors.append(f"Error processing archive {archive_url}: {e}")
                    continue
            
            # Combine all PGNs
            combined_pgn = '\n\n'.join(all_pgns)
            
            return FetchResult(
                success=True,
                games_count=games_count,
                pgn_content=combined_pgn,
                metadata={
                    'player_info': player_info,
                    'archives_processed': len(filtered_archives),
                    'total_archives': len(archives)
                },
                errors=errors,
                source_info={
                    'platform': Platform.CHESS_COM,
                    'api_version': 'public',
                    'fetch_date': datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            return FetchResult(
                success=False,
                games_count=games_count,
                pgn_content='\n\n'.join(all_pgns) if all_pgns else "",
                metadata={},
                errors=errors + [f"Fatal error: {e}"],
                source_info={'platform': Platform.CHESS_COM}
            )

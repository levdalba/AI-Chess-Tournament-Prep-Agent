"""
Lichess API fetcher for player games.
Official API documentation: https://lichess.org/api
"""

import asyncio
from datetime import datetime, date
from typing import List, Optional, Dict, Any
import json

import aiohttp
import backoff
from .base import BaseFetcher, FetchRequest, FetchResult, Platform, TimeClass


class LichessFetcher(BaseFetcher):
    """Fetcher for Lichess games using their public API."""
    
    BASE_URL = "https://lichess.org/api"
    
    def __init__(self):
        super().__init__(rate_limit=2.0)  # Lichess allows 2 req/sec for public API
    
    def supports_platform(self, platform: Platform) -> bool:
        """Check if this fetcher supports the given platform."""
        return platform == Platform.LICHESS
    
    async def __aenter__(self):
        """Initialize aiohttp session."""
        timeout = aiohttp.ClientTimeout(total=60)  # Longer timeout for streaming
        headers = {
            'User-Agent': 'AI-Chess-Tournament-Prep-Agent/1.0 (Educational Purpose)',
            'Accept': 'application/x-ndjson'  # Lichess streams NDJSON
        }
        self.session = aiohttp.ClientSession(timeout=timeout, headers=headers)
        return self
    
    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=3,
        max_time=120
    )
    async def _make_request(self, url: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a rate-limited request to Lichess API."""
        await self.rate_limiter.wait()
        
        async with self.session.get(url, params=params) as response:
            if response.status == 429:  # Rate limited
                retry_after = int(response.headers.get('Retry-After', 60))
                await asyncio.sleep(retry_after)
                raise aiohttp.ClientError("Rate limited")
            
            if response.status != 200:
                raise aiohttp.ClientError(f"HTTP {response.status}: {await response.text()}")
            
            content_type = response.headers.get('content-type', '')
            if 'application/json' in content_type:
                return await response.json()
            else:
                # Return text for streaming/NDJSON responses
                return {'text': await response.text()}
    
    async def get_player_info(self, username: str) -> Optional[Dict[str, Any]]:
        """Get player profile information."""
        try:
            url = f"{self.BASE_URL}/user/{username}"
            data = await self._make_request(url)
            
            return {
                'username': data.get('username'),
                'name': data.get('profile', {}).get('realName'),
                'title': data.get('title'),
                'followers': data.get('nbFollowers'),
                'country': data.get('profile', {}).get('country'),
                'joined': data.get('createdAt'),
                'online': data.get('online'),
                'rating': {
                    'bullet': data.get('perfs', {}).get('bullet', {}).get('rating'),
                    'blitz': data.get('perfs', {}).get('blitz', {}).get('rating'),
                    'rapid': data.get('perfs', {}).get('rapid', {}).get('rating'),
                    'classical': data.get('perfs', {}).get('classical', {}).get('rating'),
                    'correspondence': data.get('perfs', {}).get('correspondence', {}).get('rating')
                },
                'platform': Platform.LICHESS
            }
        except Exception as e:
            print(f"Error fetching player info for {username}: {e}")
            return None
    
    def _map_lichess_time_class(self, perf_type: str, initial_time: int = 0) -> TimeClass:
        """Map Lichess performance type to our time class enum."""
        mapping = {
            'ultraBullet': TimeClass.BULLET,
            'bullet': TimeClass.BULLET,
            'blitz': TimeClass.BLITZ,
            'rapid': TimeClass.RAPID,
            'classical': TimeClass.CLASSICAL,
            'correspondence': TimeClass.CORRESPONDENCE,
        }
        
        # If not in mapping, determine by initial time
        if perf_type not in mapping:
            if initial_time < 180:
                return TimeClass.BULLET
            elif initial_time < 600:
                return TimeClass.BLITZ
            elif initial_time < 1800:
                return TimeClass.RAPID
            else:
                return TimeClass.CLASSICAL
        
        return mapping.get(perf_type, TimeClass.RAPID)
    
    def _build_games_params(self, request: FetchRequest) -> Dict[str, Any]:
        """Build query parameters for games API."""
        params = {
            'format': 'pgn',
            'max': request.max_games or 1000,  # Default to 1000 games
            'sort': 'dateDesc',  # Newest first
            'opening': 'true',  # Include opening information
            'moves': 'true',  # Include moves (should be default for PGN)
            'tags': 'true',  # Include all PGN tags
        }
        
        # Add date range if specified
        if request.start_date:
            params['since'] = int(datetime.combine(request.start_date, datetime.min.time()).timestamp() * 1000)
        
        if request.end_date:
            # End of the day
            end_datetime = datetime.combine(request.end_date, datetime.max.time())
            params['until'] = int(end_datetime.timestamp() * 1000)
        
        # Add performance types if specified
        if request.time_classes:
            lichess_perfs = []
            for time_class in request.time_classes:
                if time_class == TimeClass.BULLET:
                    lichess_perfs.extend(['bullet', 'ultraBullet'])
                elif time_class == TimeClass.BLITZ:
                    lichess_perfs.append('blitz')
                elif time_class == TimeClass.RAPID:
                    lichess_perfs.append('rapid')
                elif time_class == TimeClass.CLASSICAL:
                    lichess_perfs.append('classical')
                elif time_class == TimeClass.CORRESPONDENCE:
                    lichess_perfs.append('correspondence')
            
            if lichess_perfs:
                params['perfType'] = ','.join(lichess_perfs)
        
        return params
    
    async def fetch_games(self, request: FetchRequest) -> FetchResult:
        """Fetch games for a Lichess player."""
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
            
            # Build API parameters
            params = self._build_games_params(request)
            
            # Fetch games via streaming API
            url = f"{self.BASE_URL}/games/user/{username}"
            
            await self.rate_limiter.wait()
            
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    return FetchResult(
                        success=False,
                        games_count=0,
                        pgn_content="",
                        metadata=player_info,
                        errors=[f"HTTP {response.status}: {await response.text()}"],
                        source_info={'platform': Platform.LICHESS}
                    )
                
                # Read the streaming PGN response
                pgn_content = await response.text()
                
                # Count games by counting PGN headers
                games_count = pgn_content.count('[Event ')
                
                return FetchResult(
                    success=True,
                    games_count=games_count,
                    pgn_content=pgn_content,
                    metadata={
                        'player_info': player_info,
                        'request_params': params
                    },
                    errors=errors,
                    source_info={
                        'platform': Platform.LICHESS,
                        'api_version': 'public',
                        'fetch_date': datetime.now().isoformat()
                    }
                )
        
        except Exception as e:
            return FetchResult(
                success=False,
                games_count=0,
                pgn_content="",
                metadata={},
                errors=errors + [f"Fatal error: {e}"],
                source_info={'platform': Platform.LICHESS}
            )
    
    async def get_player_games_count(self, username: str, 
                                   start_date: Optional[date] = None, 
                                   end_date: Optional[date] = None) -> int:
        """Get the total number of games for a player in a date range."""
        try:
            params = {'max': 1}  # We just want the count, not the games
            
            if start_date:
                params['since'] = int(datetime.combine(start_date, datetime.min.time()).timestamp() * 1000)
            
            if end_date:
                end_datetime = datetime.combine(end_date, datetime.max.time())
                params['until'] = int(end_datetime.timestamp() * 1000)
            
            url = f"{self.BASE_URL}/games/user/{username}"
            
            # This is a bit hacky - Lichess doesn't provide a direct count API
            # We'll need to fetch a small sample and extrapolate or implement pagination
            response = await self._make_request(url, params)
            
            # For now, return 0 as placeholder - in practice you'd need to implement
            # proper counting logic or use Lichess's activity endpoint
            return 0
            
        except Exception as e:
            print(f"Error getting games count for {username}: {e}")
            return 0

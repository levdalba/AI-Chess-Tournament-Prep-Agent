"""
FIDE and OTB games fetcher using The Week in Chess (TWIC) and other sources.
Since FIDE doesn't have a public API, we fetch from reliable third-party sources.
"""

import asyncio
import re
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any, Set
from pathlib import Path
import zipfile
import io

import aiohttp
import backoff
from bs4 import BeautifulSoup
from .base import BaseFetcher, FetchRequest, FetchResult, Platform, TimeClass


class FideFetcher(BaseFetcher):
    """Fetcher for FIDE and OTB games from various sources."""
    
    TWIC_BASE_URL = "https://theweekinchess.com"
    PGN_MENTOR_BASE_URL = "https://www.pgnmentor.com"
    LICHESS_MASTERS_URL = "https://lichess.org/api/games/search"
    
    def __init__(self):
        super().__init__(rate_limit=0.5)  # Be conservative with scraping
    
    def supports_platform(self, platform: Platform) -> bool:
        """Check if this fetcher supports the given platform."""
        return platform in [Platform.FIDE, Platform.TWIC, Platform.PGN_MENTOR]
    
    async def __aenter__(self):
        """Initialize aiohttp session."""
        timeout = aiohttp.ClientTimeout(total=120)  # Longer timeout for large files
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; AI-Chess-Tournament-Prep-Agent/1.0)',
        }
        self.session = aiohttp.ClientSession(timeout=timeout, headers=headers)
        return self
    
    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=3,
        max_time=180
    )
    async def _make_request(self, url: str, stream: bool = False) -> Any:
        """Make a rate-limited request."""
        await self.rate_limiter.wait()
        
        async with self.session.get(url) as response:
            if response.status == 429:  # Rate limited
                await asyncio.sleep(60)
                raise aiohttp.ClientError("Rate limited")
            
            if response.status != 200:
                raise aiohttp.ClientError(f"HTTP {response.status}: {await response.text()}")
            
            if stream:
                return await response.read()  # Return bytes for downloads
            else:
                return await response.text()  # Return text for HTML/PGN
    
    async def get_player_info(self, username: str) -> Optional[Dict[str, Any]]:
        """Get player information - limited for FIDE sources."""
        return {
            'username': username,
            'name': username,  # We don't have name mapping for FIDE
            'platform': Platform.FIDE,
            'note': 'FIDE/OTB games - limited player info available'
        }
    
    async def get_twic_archives(self, start_issue: int = 1, end_issue: int = None) -> List[Dict[str, Any]]:
        """Get list of TWIC archives available for download."""
        if end_issue is None:
            # Get the latest issue number by scraping the TWIC website
            try:
                main_page = await self._make_request(f"{self.TWIC_BASE_URL}/twic.html")
                soup = BeautifulSoup(main_page, 'html.parser')
                
                # Look for the latest issue number in the page
                latest_match = re.search(r'TWIC (\d+)', main_page)
                end_issue = int(latest_match.group(1)) if latest_match else 1500
            except:
                end_issue = 1500  # Fallback to a reasonable number
        
        archives = []
        for issue in range(start_issue, end_issue + 1):
            # TWIC URLs are predictable: twicXXXX.zip
            archive_url = f"{self.TWIC_BASE_URL}/zips/twic{issue:04d}.zip"
            archives.append({
                'issue': issue,
                'url': archive_url,
                'estimated_games': 1000  # Rough estimate per issue
            })
        
        return archives
    
    def _extract_games_from_pgn_content(self, pgn_content: str, player_name: str) -> List[str]:
        """Extract games where the specified player participated."""
        games = []
        current_game = []
        in_game = False
        
        # Normalize player name for matching
        player_name_lower = player_name.lower().strip()
        
        for line in pgn_content.split('\n'):
            if line.startswith('[Event '):
                if in_game and current_game:
                    # Check if previous game contains our player
                    game_text = '\n'.join(current_game)
                    if self._game_contains_player(game_text, player_name_lower):
                        games.append(game_text)
                
                # Start new game
                current_game = [line]
                in_game = True
            elif in_game:
                current_game.append(line)
                
                # End of game (empty line after moves)
                if not line.strip() and len(current_game) > 10:
                    game_text = '\n'.join(current_game)
                    if self._game_contains_player(game_text, player_name_lower):
                        games.append(game_text)
                    current_game = []
                    in_game = False
        
        # Handle last game
        if in_game and current_game:
            game_text = '\n'.join(current_game)
            if self._game_contains_player(game_text, player_name_lower):
                games.append(game_text)
        
        return games
    
    def _game_contains_player(self, game_pgn: str, player_name_lower: str) -> bool:
        """Check if a game PGN contains the specified player."""
        game_lower = game_pgn.lower()
        
        # Look for player name in White and Black tags
        white_match = re.search(r'\[White "([^"]+)"\]', game_lower)
        black_match = re.search(r'\[Black "([^"]+)"\]', game_lower)
        
        if white_match and player_name_lower in white_match.group(1):
            return True
        if black_match and player_name_lower in black_match.group(1):
            return True
        
        # Also check for partial name matches (last name only)
        name_parts = player_name_lower.split()
        if len(name_parts) > 1:
            last_name = name_parts[-1]
            if len(last_name) > 3:  # Avoid matching very short names
                if white_match and last_name in white_match.group(1):
                    return True
                if black_match and last_name in black_match.group(1):
                    return True
        
        return False
    
    async def fetch_from_twic(self, request: FetchRequest) -> FetchResult:
        """Fetch games from The Week in Chess archives."""
        player_name = request.username
        errors = []
        all_games = []
        processed_issues = 0
        
        try:
            # Calculate which TWIC issues to check based on date range
            start_issue = 1  # TWIC started in 1994
            end_issue = None
            
            if request.start_date:
                # Rough calculation: TWIC issue 1 was in 1994
                # About 50 issues per year
                years_since_1994 = request.start_date.year - 1994
                start_issue = max(1, years_since_1994 * 50)
            
            if request.end_date:
                years_since_1994 = request.end_date.year - 1994
                end_issue = min(1500, years_since_1994 * 50 + 100)  # Add buffer
            
            # Get available archives
            archives = await self.get_twic_archives(start_issue, end_issue)
            
            # Limit the number of archives to process (to avoid overwhelming)
            max_archives = min(20, len(archives))  # Process at most 20 issues
            archives = archives[-max_archives:]  # Take the most recent ones
            
            for archive in archives:
                if request.max_games and len(all_games) >= request.max_games:
                    break
                
                try:
                    # Download the ZIP file
                    zip_data = await self._make_request(archive['url'], stream=True)
                    
                    # Extract PGN from ZIP
                    with zipfile.ZipFile(io.BytesIO(zip_data)) as zip_file:
                        for file_name in zip_file.namelist():
                            if file_name.endswith('.pgn'):
                                pgn_content = zip_file.read(file_name).decode('utf-8', errors='ignore')
                                
                                # Extract games for our player
                                player_games = self._extract_games_from_pgn_content(pgn_content, player_name)
                                all_games.extend(player_games)
                                
                                # Stop if we have enough games
                                if request.max_games and len(all_games) >= request.max_games:
                                    break
                    
                    processed_issues += 1
                    
                except Exception as e:
                    errors.append(f"Error processing TWIC issue {archive['issue']}: {e}")
                    continue
            
            # Trim games if we have too many
            if request.max_games and len(all_games) > request.max_games:
                all_games = all_games[:request.max_games]
            
            combined_pgn = '\n\n'.join(all_games)
            
            return FetchResult(
                success=True,
                games_count=len(all_games),
                pgn_content=combined_pgn,
                metadata={
                    'player_name': player_name,
                    'twic_issues_processed': processed_issues,
                    'source': 'The Week in Chess'
                },
                errors=errors,
                source_info={
                    'platform': Platform.TWIC,
                    'fetch_date': datetime.now().isoformat(),
                    'source_url': self.TWIC_BASE_URL
                }
            )
            
        except Exception as e:
            return FetchResult(
                success=False,
                games_count=len(all_games),
                pgn_content='\n\n'.join(all_games) if all_games else "",
                metadata={'player_name': player_name},
                errors=errors + [f"Fatal error: {e}"],
                source_info={'platform': Platform.TWIC}
            )
    
    async def fetch_games(self, request: FetchRequest) -> FetchResult:
        """Fetch games based on the requested platform."""
        if request.platform == Platform.TWIC:
            return await self.fetch_from_twic(request)
        elif request.platform == Platform.FIDE:
            # For generic FIDE requests, use TWIC as the primary source
            twic_request = FetchRequest(
                username=request.username,
                platform=Platform.TWIC,
                start_date=request.start_date,
                end_date=request.end_date,
                max_games=request.max_games
            )
            return await self.fetch_from_twic(twic_request)
        else:
            return FetchResult(
                success=False,
                games_count=0,
                pgn_content="",
                metadata={},
                errors=[f"Platform {request.platform} not yet implemented"],
                source_info={}
            )

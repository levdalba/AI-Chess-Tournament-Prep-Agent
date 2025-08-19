"""
Main fetcher coordinator that manages all chess platforms.
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

from .base import BaseFetcher, FetchRequest, FetchResult, Platform, FetcherRegistry
from .chess_com import ChessComFetcher
from .lichess import LichessFetcher
from .fide import FideFetcher

# Import Game model
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.models import Game


class ChessDataFetcher:
    """Main coordinator for fetching chess data from multiple platforms."""

    def __init__(self):
        self.registry = FetcherRegistry()
        self._setup_fetchers()

    def _setup_fetchers(self):
        """Register all available fetchers."""
        # Register Chess.com fetcher
        chess_com_fetcher = ChessComFetcher()
        self.registry.register(Platform.CHESS_COM, chess_com_fetcher)

        # Register Lichess fetcher
        lichess_fetcher = LichessFetcher()
        self.registry.register(Platform.LICHESS, lichess_fetcher)

        # Register FIDE/TWIC fetcher
        fide_fetcher = FideFetcher()
        self.registry.register(Platform.FIDE, fide_fetcher)
        self.registry.register(Platform.TWIC, fide_fetcher)
        self.registry.register(Platform.PGN_MENTOR, fide_fetcher)

    def get_supported_platforms(self) -> List[Platform]:
        """Get list of all supported platforms."""
        return self.registry.get_supported_platforms()

    async def fetch_single_platform(self, request: FetchRequest) -> FetchResult:
        """Fetch games from a single platform."""
        fetcher = self.registry.get_fetcher(request.platform)

        if not fetcher:
            return FetchResult(
                success=False,
                games_count=0,
                pgn_content="",
                metadata={},
                errors=[f"Platform {request.platform} not supported"],
                source_info={"platform": request.platform},
            )

        async with fetcher:
            return await fetcher.fetch_games(request)

    async def fetch_multiple_platforms(
        self, requests: List[FetchRequest]
    ) -> List[FetchResult]:
        """Fetch games from multiple platforms concurrently."""
        tasks = []

        for request in requests:
            task = self.fetch_single_platform(request)
            tasks.append(task)

        return await asyncio.gather(*tasks, return_exceptions=True)

    async def fetch_all_platforms(
        self, username: str, platforms: List[Platform] = None, **kwargs
    ) -> Dict[Platform, FetchResult]:
        """Fetch games from all specified platforms for a user."""

        if platforms is None:
            platforms = self.get_supported_platforms()

        # Create requests for each platform
        requests = []
        for platform in platforms:
            request = FetchRequest(username=username, platform=platform, **kwargs)
            requests.append(request)

        # Fetch from all platforms
        results = await self.fetch_multiple_platforms(requests)

        # Organize results by platform
        platform_results = {}
        for i, (request, result) in enumerate(zip(requests, results)):
            if isinstance(result, Exception):
                # Handle exceptions
                platform_results[request.platform] = FetchResult(
                    success=False,
                    games_count=0,
                    pgn_content="",
                    metadata={},
                    errors=[f"Exception: {result}"],
                    source_info={"platform": request.platform},
                )
            else:
                platform_results[request.platform] = result

        return platform_results

    async def get_player_info_all_platforms(
        self, username: str
    ) -> Dict[Platform, Dict[str, Any]]:
        """Get player information from all platforms."""
        results = {}

        for platform in self.get_supported_platforms():
            fetcher = self.registry.get_fetcher(platform)
            if fetcher:
                async with fetcher:
                    info = await fetcher.get_player_info(username)
                    if info:
                        results[platform] = info

        return results

    async def fetch_player_games(
        self, username: str, platform: str, limit: int = 100
    ) -> List[Game]:
        """Fetch player games and convert to Game objects."""
        from shared.models import Game, GameMetadata, Player, GameResult, Move

        # Convert string platform to Platform enum
        platform_map = {
            "chess.com": Platform.CHESS_COM,
            "lichess": Platform.LICHESS,
            "lichess.org": Platform.LICHESS,
            "fide": Platform.FIDE,
        }
        platform_enum = platform_map.get(platform.lower(), Platform.CHESS_COM)

        # Create fetch request
        request = FetchRequest(
            username=username, platform=platform_enum, max_games=limit
        )

        # Fetch games
        result = await self.fetch_single_platform(request)

        if not result.success or not result.pgn_content:
            return []

        # Parse PGN content into Game objects
        games = []
        try:
            import chess.pgn
            import io

            # Split PGN content by games
            pgn_io = io.StringIO(result.pgn_content)

            while True:
                game = chess.pgn.read_game(pgn_io)
                if game is None:
                    break

                # Extract game information
                headers = game.headers

                # Create metadata
                metadata = GameMetadata(
                    event=headers.get("Event"),
                    site=headers.get("Site"),
                    date=headers.get("Date"),
                    round=headers.get("Round"),
                    white=Player(
                        name=headers.get("White", "Unknown"),
                        rating=(
                            int(headers.get("WhiteElo", "0"))
                            if headers.get("WhiteElo", "0").isdigit()
                            else None
                        ),
                        platform=platform,
                    ),
                    black=Player(
                        name=headers.get("Black", "Unknown"),
                        rating=(
                            int(headers.get("BlackElo", "0"))
                            if headers.get("BlackElo", "0").isdigit()
                            else None
                        ),
                        platform=platform,
                    ),
                    result=GameResult(headers.get("Result", "*")),
                    eco=headers.get("ECO"),
                    time_control=None,  # Skip time control parsing for now
                )

                # Extract moves
                moves = []
                board = game.board()
                move_number = 1
                white_move = None

                for move in game.mainline_moves():
                    san_move = board.san(move)

                    if board.turn:  # White's turn before move
                        white_move = san_move
                    else:  # Black's turn, so white move is stored, now add black
                        moves.append(
                            Move(
                                move_number=move_number,
                                white_move=white_move,
                                black_move=san_move,
                            )
                        )
                        move_number += 1
                        white_move = None

                    board.push(move)

                # Add final white move if exists
                if white_move:
                    moves.append(Move(move_number=move_number, white_move=white_move))

                # Create Game object
                chess_game = Game(
                    id=headers.get("Site", ""),
                    metadata=metadata,
                    moves=moves,
                    pgn=str(game),
                )

                games.append(chess_game)

                if len(games) >= limit:
                    break

        except ImportError:
            # Fallback if chess library is not available
            print("python-chess not available, using basic PGN parsing")
            # Basic parsing would go here
            pass
        except Exception as e:
            print(f"Error parsing PGN: {e}")
            import traceback

            traceback.print_exc()

        return games

    async def close(self):
        """Close all active connections."""
        # Close any active fetcher connections
        for fetcher in self.registry._fetchers.values():
            if hasattr(fetcher, "close"):
                try:
                    await fetcher.close()
                except:
                    pass

    def combine_pgn_results(self, results: Dict[Platform, FetchResult]) -> FetchResult:
        """Combine results from multiple platforms into a single result."""
        all_pgns = []
        total_games = 0
        all_errors = []
        all_metadata = {}

        successful_platforms = []

        for platform, result in results.items():
            if result.success and result.pgn_content:
                all_pgns.append(
                    f"# Games from {platform.value}\n\n{result.pgn_content}"
                )
                total_games += result.games_count
                successful_platforms.append(platform)
                all_metadata[f"{platform.value}_metadata"] = result.metadata

            if result.errors:
                all_errors.extend(
                    [f"{platform.value}: {error}" for error in result.errors]
                )

        combined_pgn = "\n\n".join(all_pgns)

        return FetchResult(
            success=len(successful_platforms) > 0,
            games_count=total_games,
            pgn_content=combined_pgn,
            metadata={
                "platforms": [p.value for p in successful_platforms],
                "platform_details": all_metadata,
                "total_platforms_attempted": len(results),
            },
            errors=all_errors,
            source_info={
                "combined_fetch": True,
                "platforms": successful_platforms,
                "fetch_date": datetime.now().isoformat(),
            },
        )


# Convenience functions for direct usage
async def fetch_chess_com_games(username: str, **kwargs) -> FetchResult:
    """Convenience function to fetch Chess.com games."""
    fetcher = ChessDataFetcher()
    request = FetchRequest(username=username, platform=Platform.CHESS_COM, **kwargs)
    return await fetcher.fetch_single_platform(request)


async def fetch_lichess_games(username: str, **kwargs) -> FetchResult:
    """Convenience function to fetch Lichess games."""
    fetcher = ChessDataFetcher()
    request = FetchRequest(username=username, platform=Platform.LICHESS, **kwargs)
    return await fetcher.fetch_single_platform(request)


async def fetch_fide_games(username: str, **kwargs) -> FetchResult:
    """Convenience function to fetch FIDE/OTB games."""
    fetcher = ChessDataFetcher()
    request = FetchRequest(username=username, platform=Platform.FIDE, **kwargs)
    return await fetcher.fetch_single_platform(request)


async def fetch_all_games(username: str, **kwargs) -> Dict[Platform, FetchResult]:
    """Convenience function to fetch games from all platforms."""
    fetcher = ChessDataFetcher()
    return await fetcher.fetch_all_platforms(username, **kwargs)

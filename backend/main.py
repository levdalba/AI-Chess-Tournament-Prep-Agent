"""
FastAPI backend server for AI Chess Tournament Prep Agent.
"""

from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager
import logging
from datetime import datetime
import os
import sys

# Import middleware
from middleware import ErrorHandlerMiddleware, LoggingMiddleware
from middleware.error_handler import (
    http_exception_handler,
    validation_exception_handler,
)

# Import configuration
from config import setup_logging, get_logger, db_manager, init_database

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our modules
from shared.models import Game, Player, PrepPlan as SharedPrepPlan
from data.fetchers import ChessDataFetcher
from data.analyzers.chess_engine import ChessAnalyzer, GameAnalysis
from data.analyzers.opening_analyzer import OpeningAnalyzer, OpeningRepertoire
from ai.grok_service import GrokAIService, PrepPlan

# Setup logging
log_level = os.getenv("LOG_LEVEL", "INFO")
setup_logging(log_level)
logger = get_logger(__name__)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Chess Tournament Prep Agent",
    description="Backend API for chess tournament preparation with AI-powered analysis",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(LoggingMiddleware)

# Add exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Security
security = HTTPBearer()

# Configuration
GROK_API_KEY = os.getenv("GROK_API_KEY", "")
STOCKFISH_PATH = os.getenv("STOCKFISH_PATH", "")

# Global services (will be initialized on startup)
chess_fetcher: Optional[ChessDataFetcher] = None
chess_analyzer: Optional[ChessAnalyzer] = None
opening_analyzer: Optional[OpeningAnalyzer] = None
grok_service: Optional[GrokAIService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup
    global chess_fetcher, chess_analyzer, opening_analyzer, grok_service

    try:
        # Initialize database
        database_url = os.getenv("DATABASE_URL")
        debug_mode = os.getenv("DEBUG", "0") == "1"
        db_manager.initialize(database_url, echo=debug_mode)

        # Initialize database tables
        await init_database()

        # Initialize data fetcher
        chess_fetcher = ChessDataFetcher()

        # Initialize analyzers (only if dependencies are available)
        try:
            chess_analyzer = ChessAnalyzer(
                stockfish_path=STOCKFISH_PATH if STOCKFISH_PATH else None
            )
        except Exception as e:
            logger.warning(f"Chess analyzer not available: {e}")
            chess_analyzer = None

        opening_analyzer = OpeningAnalyzer()

        # Initialize AI service (only if API key is available)
        if GROK_API_KEY:
            grok_service = GrokAIService(GROK_API_KEY)
        else:
            logger.warning("GROK_API_KEY not found, AI features will be limited")
            grok_service = None

        logger.info("Services initialized successfully")

    except Exception as e:
        logger.error(f"Error initializing services: {e}")

    yield

    # Shutdown
    try:
        if chess_fetcher:
            await chess_fetcher.close()

        # Close database connections
        await db_manager.close()

        logger.info("Services cleaned up successfully")

    except Exception as e:
        logger.error(f"Error during cleanup: {e}")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="AI Chess Tournament Prep Agent",
    description="Backend API for chess tournament preparation with AI-powered analysis",
    version="1.0.0",
    lifespan=lifespan,
)


# Request/Response Models
class PlayerSearchRequest(BaseModel):
    platform: str  # "chess.com", "lichess", or "fide"
    username: str
    limit: Optional[int] = 100


class PlayerSearchResponse(BaseModel):
    player: Player
    games: List[Game]
    total_games: int


class AnalysisRequest(BaseModel):
    player_username: str
    platform: str
    include_openings: bool = True
    include_weaknesses: bool = True
    max_games: Optional[int] = 50


class AnalysisResponse(BaseModel):
    player: Player
    opening_repertoire: Optional[Dict[str, Any]] = None
    weaknesses: Optional[Dict[str, Any]] = None
    game_statistics: Dict[str, Any]
    analysis_date: str


class PrepPlanRequest(BaseModel):
    player_username: str
    opponent_username: str
    player_platform: str = "chess.com"
    opponent_platform: str = "chess.com"
    tournament_name: Optional[str] = None
    tournament_date: Optional[str] = None
    time_control: Optional[str] = None


class PrepPlanResponse(BaseModel):
    prep_plan: Dict[str, Any]
    player_analysis: Dict[str, Any]
    opponent_analysis: Dict[str, Any]


# Dependency to get current user (mock for now)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    # In a real app, verify the JWT token here
    # For now, return a mock user
    return {"id": "user123", "username": "testuser"}


# Dependency to get current user (mock for now)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    # In a real app, verify the JWT token here
    # For now, return a mock user
    return {"id": "user123", "username": "testuser"}


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    # Check database health
    db_healthy = await db_manager.health_check()

    services_status = {
        "database": db_healthy,
        "chess_fetcher": chess_fetcher is not None,
        "chess_analyzer": chess_analyzer is not None,
        "opening_analyzer": opening_analyzer is not None,
        "grok_service": grok_service is not None,
    }

    # Overall health status
    overall_healthy = db_healthy and chess_fetcher is not None

    return {
        "status": "healthy" if overall_healthy else "degraded",
        "timestamp": datetime.now().isoformat(),
        "services": services_status,
    }


# Authentication endpoints
@app.post("/auth/login")
async def login(credentials: dict):
    """Mock login endpoint."""
    # In a real app, validate credentials and return JWT
    return {
        "access_token": "mock_jwt_token",
        "token_type": "bearer",
        "user": {
            "id": "user123",
            "username": credentials.get("username", "testuser"),
            "email": credentials.get("email", "test@example.com"),
        },
    }


@app.post("/auth/register")
async def register(user_data: dict):
    """Mock registration endpoint."""
    # In a real app, create user and return JWT
    return {
        "access_token": "mock_jwt_token",
        "token_type": "bearer",
        "user": {
            "id": "user124",
            "username": user_data.get("username"),
            "email": user_data.get("email"),
        },
    }


# Player data endpoints
@app.post("/api/players/search", response_model=PlayerSearchResponse)
async def search_player(
    request: PlayerSearchRequest, current_user: dict = Depends(get_current_user)
):
    """Search for a player and fetch their games."""
    if not chess_fetcher:
        raise HTTPException(status_code=503, detail="Chess data fetcher not available")

    try:
        # Fetch player games
        games = await chess_fetcher.fetch_player_games(
            request.username, request.platform, limit=request.limit or 100
        )

        if not games:
            raise HTTPException(
                status_code=404, detail="Player not found or no games available"
            )

        # Create player object from first game
        first_game = games[0]
        player = Player(
            name=request.username,
            platform=request.platform,
            rating=(
                first_game.white_rating
                if first_game.white_player.lower() == request.username.lower()
                else first_game.black_rating
            ),
            country="Unknown",  # Would need additional API call
        )

        return PlayerSearchResponse(player=player, games=games, total_games=len(games))

    except Exception as e:
        logger.error(f"Error searching for player: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error fetching player data: {str(e)}"
        )


# Analysis endpoints
@app.post("/api/analysis/player", response_model=AnalysisResponse)
async def analyze_player(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
):
    """Analyze a player's games and generate insights."""
    if not chess_fetcher or not opening_analyzer:
        raise HTTPException(status_code=503, detail="Analysis services not available")

    try:
        # Fetch player games
        games = await chess_fetcher.fetch_player_games(
            request.player_username, request.platform, limit=request.max_games or 50
        )

        if not games:
            raise HTTPException(status_code=404, detail="No games found for player")

        # Create player object
        player = Player(
            name=request.player_username,
            platform=request.platform,
            rating=(
                games[0].white_rating
                if games[0].white_player.lower() == request.player_username.lower()
                else games[0].black_rating
            ),
        )

        # Convert games to analysis format
        games_data = []
        for game in games:
            games_data.append(
                {
                    "white": game.white_player,
                    "black": game.black_player,
                    "result": game.result,
                    "pgn": game.pgn,
                    "moves": [],  # Will be extracted from PGN
                }
            )

        # Analyze openings
        opening_repertoire = None
        if request.include_openings:
            repertoire = opening_analyzer.analyze_player_openings(
                games_data, request.player_username
            )
            opening_repertoire = {
                "as_white": [
                    {
                        "eco": v.eco,
                        "name": v.name,
                        "frequency": v.frequency,
                        "win_rate": v.win_rate,
                        "draw_rate": v.draw_rate,
                        "loss_rate": v.loss_rate,
                    }
                    for v in repertoire.as_white
                ],
                "as_black_vs_e4": [
                    {
                        "eco": v.eco,
                        "name": v.name,
                        "frequency": v.frequency,
                        "win_rate": v.win_rate,
                    }
                    for v in repertoire.as_black_vs_e4
                ],
                "as_black_vs_d4": [
                    {
                        "eco": v.eco,
                        "name": v.name,
                        "frequency": v.frequency,
                        "win_rate": v.win_rate,
                    }
                    for v in repertoire.as_black_vs_d4
                ],
            }

        # Analyze weaknesses (if chess engine is available)
        weaknesses = None
        if request.include_weaknesses and chess_analyzer:
            try:
                async with chess_analyzer as analyzer:
                    # Analyze a subset of games for weaknesses
                    pgn_strings = [
                        game.pgn for game in games[:10]
                    ]  # Limit to avoid timeout
                    analyses = await analyzer.analyze_multiple_games(pgn_strings)
                    if analyses:
                        weaknesses = analyzer.get_weakness_patterns(
                            analyses, request.player_username
                        )
            except Exception as e:
                logger.error(f"Error in weakness analysis: {e}")

        # Game statistics
        total_games = len(games)
        wins = sum(
            1
            for g in games
            if (
                g.white_player.lower() == request.player_username.lower()
                and g.result == "1-0"
            )
            or (
                g.black_player.lower() == request.player_username.lower()
                and g.result == "0-1"
            )
        )
        draws = sum(1 for g in games if g.result == "1/2-1/2")
        losses = total_games - wins - draws

        game_statistics = {
            "total_games": total_games,
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "win_percentage": wins / total_games if total_games > 0 else 0,
            "performance_rating": player.rating,  # Simplified
        }

        return AnalysisResponse(
            player=player,
            opening_repertoire=opening_repertoire,
            weaknesses=weaknesses,
            game_statistics=game_statistics,
            analysis_date=datetime.now().isoformat(),
        )

    except Exception as e:
        logger.error(f"Error analyzing player: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


@app.post("/api/analysis/prep-plan", response_model=PrepPlanResponse)
async def generate_prep_plan(
    request: PrepPlanRequest, current_user: dict = Depends(get_current_user)
):
    """Generate a comprehensive preparation plan for a match."""
    if not grok_service:
        raise HTTPException(status_code=503, detail="AI service not available")

    try:
        # Analyze both players
        player_analysis_req = AnalysisRequest(
            player_username=request.player_username,
            platform=request.player_platform,
            max_games=30,
        )

        opponent_analysis_req = AnalysisRequest(
            player_username=request.opponent_username,
            platform=request.opponent_platform,
            max_games=30,
        )

        # Get analyses (reuse the existing endpoint logic)
        # In a real implementation, we'd extract this into a service method
        player_analysis = {
            "player_name": request.player_username,
            "rating": 1500,  # Mock data
            "repertoire": {},
            "weaknesses": {},
        }

        opponent_analysis = {
            "player_name": request.opponent_username,
            "rating": 1500,  # Mock data
            "repertoire": {},
            "weaknesses": {},
        }

        # Tournament info
        tournament_info = None
        if request.tournament_name:
            tournament_info = {
                "name": request.tournament_name,
                "date": request.tournament_date,
                "time_control": request.time_control,
            }

        # Generate prep plan using AI
        async with grok_service as ai:
            prep_plan = await ai.generate_prep_plan(
                player_analysis, opponent_analysis, tournament_info
            )

        # Convert to response format
        prep_plan_dict = {
            "player_name": prep_plan.player_name,
            "opponent_name": prep_plan.opponent_name,
            "tournament_date": prep_plan.tournament_date,
            "opening_preparation": prep_plan.opening_preparation,
            "tactical_themes": prep_plan.tactical_themes,
            "strategic_focus": prep_plan.strategic_focus,
            "daily_training_plan": prep_plan.daily_training_plan,
            "weakness_exploitation": prep_plan.weakness_exploitation,
            "time_control_strategy": prep_plan.time_control_strategy,
            "psychological_notes": prep_plan.psychological_notes,
            "confidence_score": prep_plan.confidence_score,
            "estimated_prep_time": prep_plan.estimated_prep_time,
            "created_at": prep_plan.created_at,
        }

        return PrepPlanResponse(
            prep_plan=prep_plan_dict,
            player_analysis=player_analysis,
            opponent_analysis=opponent_analysis,
        )

    except Exception as e:
        logger.error(f"Error generating prep plan: {e}")
        raise HTTPException(
            status_code=500, detail=f"Prep plan generation error: {str(e)}"
        )


# Dashboard endpoints
@app.get("/api/dashboard/stats")
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    """Get dashboard statistics for the current user."""
    # Mock data for now
    return {
        "total_analyses": 12,
        "total_prep_plans": 5,
        "upcoming_tournaments": 2,
        "recent_activity": [
            {
                "type": "analysis",
                "description": "Analyzed Magnus Carlsen",
                "date": "2024-01-15T10:30:00Z",
            },
            {
                "type": "prep_plan",
                "description": "Created prep plan vs Hikaru",
                "date": "2024-01-14T14:20:00Z",
            },
        ],
    }


@app.get("/api/dashboard/recent-games")
async def get_recent_games(current_user: dict = Depends(get_current_user)):
    """Get recent games for dashboard."""
    # Mock data for now
    return {
        "games": [
            {
                "id": "game1",
                "white": "Player1",
                "black": "Player2",
                "result": "1-0",
                "date": "2024-01-15",
                "opening": "Sicilian Defense",
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

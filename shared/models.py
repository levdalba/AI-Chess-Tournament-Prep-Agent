from typing import Dict, List, Optional, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel

class GameResult(str, Enum):
    WHITE_WIN = "1-0"
    BLACK_WIN = "0-1"
    DRAW = "1/2-1/2"
    UNKNOWN = "*"

class TimeControl(BaseModel):
    base_time: int  # seconds
    increment: int  # seconds per move

class Player(BaseModel):
    name: str
    rating: Optional[int] = None
    title: Optional[str] = None

class GameMetadata(BaseModel):
    event: Optional[str] = None
    site: Optional[str] = None
    date: Optional[str] = None
    round: Optional[str] = None
    white: Optional[Player] = None
    black: Optional[Player] = None
    result: GameResult
    eco: Optional[str] = None  # Encyclopedia of Chess Openings
    time_control: Optional[TimeControl] = None

class Move(BaseModel):
    move_number: int
    white_move: Optional[str] = None
    black_move: Optional[str] = None
    white_time: Optional[int] = None  # time left after move
    black_time: Optional[int] = None
    white_eval: Optional[float] = None  # centipawn evaluation
    black_eval: Optional[float] = None

class Game(BaseModel):
    id: Optional[str] = None
    metadata: GameMetadata
    moves: List[Move]
    pgn: str
    created_at: Optional[datetime] = None

class Opening(BaseModel):
    eco_code: str
    name: str
    moves: str
    frequency: int  # how often opponent plays this

class WeakPoint(BaseModel):
    position_fen: str
    move: str
    eval_before: float
    eval_after: float
    eval_loss: float  # centipawns lost
    move_number: int
    phase: str  # opening, middlegame, endgame

class PrepPlan(BaseModel):
    id: Optional[str] = None
    opponent_name: str
    tournament_date: Optional[datetime] = None
    common_openings: List[Opening]
    weak_points: List[WeakPoint]
    recommendations: str  # AI-generated recommendations
    daily_drills: List[str]
    created_at: Optional[datetime] = None

class User(BaseModel):
    id: Optional[str] = None
    email: str
    username: str
    rating: Optional[int] = None
    created_at: Optional[datetime] = None
    is_active: bool = True

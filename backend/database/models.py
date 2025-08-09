"""
Database models for the chess preparation agent.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from .config import Base


class User(Base):
    """User account model."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    player_profiles = relationship("PlayerProfile", back_populates="user")
    analyses = relationship("PlayerAnalysis", back_populates="user")
    prep_plans = relationship("PrepPlan", back_populates="user")


class PlayerProfile(Base):
    """Chess player profile model."""
    __tablename__ = "player_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    platform = Column(String(20), nullable=False)  # chess.com, lichess, fide
    username = Column(String(50), nullable=False)
    display_name = Column(String(100))
    rating = Column(Integer)
    peak_rating = Column(Integer)
    country = Column(String(3))  # ISO country code
    title = Column(String(10))  # GM, IM, FM, etc.
    is_verified = Column(Boolean, default=False)
    last_synced = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="player_profiles")
    games = relationship("ChessGame", back_populates="player_profile")
    analyses = relationship("PlayerAnalysis", back_populates="player_profile")


class ChessGame(Base):
    """Individual chess game model."""
    __tablename__ = "chess_games"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_profile_id = Column(UUID(as_uuid=True), ForeignKey("player_profiles.id"))
    platform_game_id = Column(String(50), nullable=False)  # Game ID from the platform
    platform = Column(String(20), nullable=False)
    
    # Game details
    white_player = Column(String(50), nullable=False)
    black_player = Column(String(50), nullable=False)
    white_rating = Column(Integer)
    black_rating = Column(Integer)
    result = Column(String(10))  # 1-0, 0-1, 1/2-1/2
    time_control = Column(String(20))
    termination = Column(String(50))
    
    # Game content
    pgn = Column(Text)
    moves = Column(JSON)  # Array of moves in SAN
    opening_eco = Column(String(3))
    opening_name = Column(String(100))
    
    # Metadata
    played_at = Column(DateTime(timezone=True))
    imported_at = Column(DateTime(timezone=True), server_default=func.now())
    is_analyzed = Column(Boolean, default=False)
    
    # Relationships
    player_profile = relationship("PlayerProfile", back_populates="games")
    game_analysis = relationship("GameAnalysis", back_populates="game", uselist=False)


class GameAnalysis(Base):
    """Analysis of a single chess game."""
    __tablename__ = "game_analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_id = Column(UUID(as_uuid=True), ForeignKey("chess_games.id"), unique=True)
    
    # Analysis results
    total_moves = Column(Integer)
    analyzed_moves = Column(JSON)  # Array of move analyses
    white_blunders = Column(Integer, default=0)
    black_blunders = Column(Integer, default=0)
    white_mistakes = Column(Integer, default=0)
    black_mistakes = Column(Integer, default=0)
    average_centipawn_loss = Column(Float)
    game_phase_breakdown = Column(JSON)  # Opening, middlegame, endgame move counts
    
    # Engine info
    engine_used = Column(String(20), default="stockfish")
    analysis_time = Column(Float)  # Seconds per position
    analysis_depth = Column(Integer)
    
    # Metadata
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    game = relationship("ChessGame", back_populates="game_analysis")


class OpeningRepertoire(Base):
    """Opening repertoire for a player."""
    __tablename__ = "opening_repertoires"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_profile_id = Column(UUID(as_uuid=True), ForeignKey("player_profiles.id"))
    
    # Repertoire data
    as_white = Column(JSON)  # Array of opening variations
    as_black_vs_e4 = Column(JSON)
    as_black_vs_d4 = Column(JSON)
    as_black_vs_other = Column(JSON)
    
    # Statistics
    total_games_analyzed = Column(Integer)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    player_profile = relationship("PlayerProfile")


class PlayerAnalysis(Base):
    """Comprehensive analysis of a player."""
    __tablename__ = "player_analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    player_profile_id = Column(UUID(as_uuid=True), ForeignKey("player_profiles.id"))
    
    # Analysis parameters
    games_analyzed = Column(Integer)
    analysis_type = Column(String(20))  # full, opening_only, tactical_only
    
    # Results
    opening_repertoire = Column(JSON)
    weakness_patterns = Column(JSON)
    strength_analysis = Column(JSON)
    game_statistics = Column(JSON)
    recommendations = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    analysis_version = Column(String(10), default="1.0")
    
    # Relationships
    user = relationship("User", back_populates="analyses")
    player_profile = relationship("PlayerProfile", back_populates="analyses")
    prep_plans = relationship("PrepPlan", back_populates="player_analysis")


class PrepPlan(Base):
    """AI-generated preparation plan."""
    __tablename__ = "prep_plans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    player_analysis_id = Column(UUID(as_uuid=True), ForeignKey("player_analyses.id"))
    
    # Plan details
    opponent_name = Column(String(50), nullable=False)
    tournament_name = Column(String(100))
    tournament_date = Column(DateTime(timezone=True))
    
    # Plan content
    opening_preparation = Column(JSON)
    tactical_themes = Column(JSON)
    strategic_focus = Column(JSON)
    daily_training_plan = Column(JSON)
    weakness_exploitation = Column(JSON)
    time_control_strategy = Column(JSON)
    psychological_notes = Column(JSON)
    
    # Plan metadata
    confidence_score = Column(Float)
    estimated_prep_time = Column(Integer)  # hours
    ai_model_used = Column(String(20), default="grok-beta")
    
    # Status
    status = Column(String(20), default="draft")  # draft, active, completed
    is_shared = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="prep_plans")
    player_analysis = relationship("PlayerAnalysis", back_populates="prep_plans")
    training_sessions = relationship("TrainingSession", back_populates="prep_plan")


class TrainingSession(Base):
    """Individual training session from a prep plan."""
    __tablename__ = "training_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prep_plan_id = Column(UUID(as_uuid=True), ForeignKey("prep_plans.id"))
    
    # Session details
    day_number = Column(Integer, nullable=False)
    session_name = Column(String(100))
    focus_area = Column(String(50))
    
    # Session content
    exercises = Column(JSON)
    study_materials = Column(JSON)
    time_allocation = Column(JSON)  # Time for each activity
    
    # Progress tracking
    status = Column(String(20), default="pending")  # pending, in_progress, completed, skipped
    completed_at = Column(DateTime(timezone=True))
    notes = Column(Text)
    self_rating = Column(Integer)  # 1-5 scale
    
    # Metadata
    estimated_duration = Column(Integer)  # minutes
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    prep_plan = relationship("PrepPlan", back_populates="training_sessions")


class Tournament(Base):
    """Tournament information."""
    __tablename__ = "tournaments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    location = Column(String(100))
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    time_control = Column(String(50))
    rounds = Column(Integer)
    format = Column(String(20))  # swiss, round_robin, knockout
    
    # Tournament details
    organizer = Column(String(100))
    website = Column(String(200))
    prize_fund = Column(String(50))
    rating_category = Column(String(20))  # open, u2000, etc.
    
    # Status
    status = Column(String(20), default="upcoming")  # upcoming, ongoing, completed
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Indexes for better performance
from sqlalchemy import Index

# Player profile indexes
Index('ix_player_profiles_platform_username', PlayerProfile.platform, PlayerProfile.username)
Index('ix_player_profiles_user_platform', PlayerProfile.user_id, PlayerProfile.platform)

# Chess game indexes
Index('ix_chess_games_platform_game_id', ChessGame.platform, ChessGame.platform_game_id, unique=True)
Index('ix_chess_games_players', ChessGame.white_player, ChessGame.black_player)
Index('ix_chess_games_played_at', ChessGame.played_at)

# Analysis indexes
Index('ix_player_analyses_user_created', PlayerAnalysis.user_id, PlayerAnalysis.created_at)
Index('ix_prep_plans_user_status', PrepPlan.user_id, PrepPlan.status)

"""
Chess game analysis engine using python-chess and Stockfish.
"""

import asyncio
import os
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import tempfile
import time

import chess
import chess.pgn
import chess.engine
from chess.engine import SimpleEngine, Limit


@dataclass
class MoveAnalysis:
    """Analysis of a single move."""
    move_number: int
    move: str
    fen_before: str
    fen_after: str
    eval_before: Optional[float] = None  # In centipawns
    eval_after: Optional[float] = None
    eval_change: Optional[float] = None
    is_blunder: bool = False
    is_mistake: bool = False
    best_move: Optional[str] = None
    phase: str = "unknown"  # opening, middlegame, endgame


@dataclass
class GameAnalysis:
    """Complete analysis of a chess game."""
    game_id: Optional[str] = None
    white_player: Optional[str] = None
    black_player: Optional[str] = None
    result: Optional[str] = None
    opening_eco: Optional[str] = None
    opening_name: Optional[str] = None
    total_moves: int = 0
    analyzed_moves: List[MoveAnalysis] = None
    white_blunders: int = 0
    black_blunders: int = 0
    white_mistakes: int = 0
    black_mistakes: int = 0
    average_centipawn_loss: float = 0.0
    game_phase_breakdown: Dict[str, int] = None
    
    def __post_init__(self):
        if self.analyzed_moves is None:
            self.analyzed_moves = []
        if self.game_phase_breakdown is None:
            self.game_phase_breakdown = {"opening": 0, "middlegame": 0, "endgame": 0}


class ChessAnalyzer:
    """Chess game analyzer using Stockfish engine."""
    
    def __init__(self, stockfish_path: Optional[str] = None, 
                 analysis_time: float = 1.0,
                 depth: int = 15):
        """
        Initialize the chess analyzer.
        
        Args:
            stockfish_path: Path to Stockfish binary
            analysis_time: Time in seconds to analyze each position
            depth: Search depth for analysis
        """
        self.stockfish_path = stockfish_path or self._find_stockfish()
        self.analysis_time = analysis_time
        self.depth = depth
        self.engine: Optional[SimpleEngine] = None
        
        # Analysis thresholds (in centipawns)
        self.blunder_threshold = 300
        self.mistake_threshold = 100
    
    def _find_stockfish(self) -> Optional[str]:
        """Attempt to find Stockfish binary automatically."""
        possible_paths = [
            "/usr/local/bin/stockfish",
            "/usr/bin/stockfish",
            "/opt/homebrew/bin/stockfish",
            "stockfish",  # In PATH
            "./stockfish",  # Current directory
        ]
        
        for path in possible_paths:
            if os.path.exists(path) or (path == "stockfish"):
                try:
                    # Test if the binary works
                    test_engine = chess.engine.SimpleEngine.popen_uci(path)
                    test_engine.quit()
                    return path
                except:
                    continue
        
        raise RuntimeError(
            "Stockfish not found. Please install Stockfish and provide the path, "
            "or ensure it's available in your system PATH."
        )
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.engine = chess.engine.SimpleEngine.popen_uci(self.stockfish_path)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.engine:
            self.engine.quit()
    
    def _get_game_phase(self, board: chess.Board) -> str:
        """Determine the phase of the game based on material and moves."""
        move_count = len(board.move_stack)
        
        # Count pieces (excluding kings and pawns)
        piece_count = 0
        for piece_type in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]:
            piece_count += len(board.pieces(piece_type, chess.WHITE))
            piece_count += len(board.pieces(piece_type, chess.BLACK))
        
        if move_count <= 15:
            return "opening"
        elif piece_count >= 12 or move_count <= 40:
            return "middlegame"
        else:
            return "endgame"
    
    async def analyze_position(self, board: chess.Board) -> Optional[float]:
        """Analyze a single position and return evaluation in centipawns."""
        if not self.engine:
            return None
        
        try:
            # Use time-based limit for analysis
            limit = Limit(time=self.analysis_time)
            info = self.engine.analyse(board, limit)
            
            score = info["score"]
            
            # Convert score to centipawns from the perspective of the side to move
            if score.is_mate():
                # Convert mate scores to large centipawn values
                mate_in = score.mate()
                if mate_in > 0:
                    return 10000 - mate_in * 10  # Winning mate
                else:
                    return -10000 - mate_in * 10  # Losing mate
            else:
                # Regular centipawn score
                return score.relative.score()
        
        except Exception as e:
            print(f"Error analyzing position: {e}")
            return None
    
    async def analyze_game(self, pgn_string: str) -> Optional[GameAnalysis]:
        """Analyze a complete chess game from PGN."""
        try:
            # Parse the PGN
            game = chess.pgn.read_game(chess.io.StringIO(pgn_string))
            if not game:
                return None
            
            # Extract game metadata
            headers = game.headers
            analysis = GameAnalysis(
                white_player=headers.get("White"),
                black_player=headers.get("Black"),
                result=headers.get("Result"),
                opening_eco=headers.get("ECO"),
                opening_name=headers.get("Opening")
            )
            
            # Analyze the game move by move
            board = game.board()
            move_analyses = []
            
            prev_eval = None
            move_number = 0
            
            for move in game.mainline_moves():
                move_number += 1
                
                # Get position before move
                fen_before = board.fen()
                phase = self._get_game_phase(board)
                
                # Analyze position before move
                eval_before = await self.analyze_position(board)
                
                # Make the move
                san_move = board.san(move)
                board.push(move)
                
                # Analyze position after move
                eval_after = await self.analyze_position(board)
                
                # Calculate evaluation change
                eval_change = None
                is_blunder = False
                is_mistake = False
                
                if eval_before is not None and eval_after is not None:
                    # Flip evaluation if it's Black's turn (eval_after is from White's perspective)
                    if not board.turn:  # Black just moved
                        eval_change = eval_before - (-eval_after)
                    else:  # White just moved
                        eval_change = eval_before - eval_after
                    
                    # Check for blunders and mistakes
                    if eval_change > self.blunder_threshold:
                        is_blunder = True
                        if not board.turn:  # Black just moved
                            analysis.black_blunders += 1
                        else:  # White just moved
                            analysis.white_blunders += 1
                    elif eval_change > self.mistake_threshold:
                        is_mistake = True
                        if not board.turn:
                            analysis.black_mistakes += 1
                        else:
                            analysis.white_mistakes += 1
                
                # Get best move (optional - takes more time)
                best_move = None
                # if is_blunder or is_mistake:
                #     best_moves = self.engine.analyse(chess.Board(fen_before), Limit(time=self.analysis_time), multipv=1)
                #     if best_moves:
                #         best_move = best_moves["pv"][0].uci()
                
                # Create move analysis
                move_analysis = MoveAnalysis(
                    move_number=move_number,
                    move=san_move,
                    fen_before=fen_before,
                    fen_after=board.fen(),
                    eval_before=eval_before,
                    eval_after=eval_after,
                    eval_change=eval_change,
                    is_blunder=is_blunder,
                    is_mistake=is_mistake,
                    best_move=best_move,
                    phase=phase
                )
                
                move_analyses.append(move_analysis)
                analysis.game_phase_breakdown[phase] += 1
                
                prev_eval = eval_after
                
                # Break if analysis is taking too long (safety measure)
                if move_number > 200:  # Reasonable limit
                    break
            
            analysis.analyzed_moves = move_analyses
            analysis.total_moves = move_number
            
            # Calculate average centipawn loss
            total_loss = sum(ma.eval_change for ma in move_analyses if ma.eval_change is not None)
            analyzed_moves_count = len([ma for ma in move_analyses if ma.eval_change is not None])
            if analyzed_moves_count > 0:
                analysis.average_centipawn_loss = total_loss / analyzed_moves_count
            
            return analysis
        
        except Exception as e:
            print(f"Error analyzing game: {e}")
            return None
    
    async def analyze_multiple_games(self, pgn_strings: List[str]) -> List[GameAnalysis]:
        """Analyze multiple games."""
        analyses = []
        
        for i, pgn in enumerate(pgn_strings):
            print(f"Analyzing game {i + 1}/{len(pgn_strings)}...")
            analysis = await self.analyze_game(pgn)
            if analysis:
                analyses.append(analysis)
        
        return analyses
    
    def get_opening_statistics(self, analyses: List[GameAnalysis]) -> Dict[str, Any]:
        """Get statistics about openings from analyzed games."""
        opening_stats = {}
        
        for analysis in analyses:
            if analysis.opening_eco:
                eco = analysis.opening_eco
                if eco not in opening_stats:
                    opening_stats[eco] = {
                        'count': 0,
                        'name': analysis.opening_name or 'Unknown',
                        'total_blunders': 0,
                        'total_mistakes': 0,
                        'results': {'1-0': 0, '0-1': 0, '1/2-1/2': 0}
                    }
                
                opening_stats[eco]['count'] += 1
                opening_stats[eco]['total_blunders'] += analysis.white_blunders + analysis.black_blunders
                opening_stats[eco]['total_mistakes'] += analysis.white_mistakes + analysis.black_mistakes
                
                if analysis.result in opening_stats[eco]['results']:
                    opening_stats[eco]['results'][analysis.result] += 1
        
        return opening_stats
    
    def get_weakness_patterns(self, analyses: List[GameAnalysis], 
                            target_player: str) -> Dict[str, Any]:
        """Identify weakness patterns for a specific player."""
        weaknesses = {
            'blunders_by_phase': {'opening': 0, 'middlegame': 0, 'endgame': 0},
            'mistakes_by_phase': {'opening': 0, 'middlegame': 0, 'endgame': 0},
            'average_centipawn_loss_by_phase': {'opening': [], 'middlegame': [], 'endgame': []},
            'worst_moves': [],
            'common_mistake_positions': []
        }
        
        target_player_lower = target_player.lower()
        
        for analysis in analyses:
            # Check if target player is in this game
            is_white = (analysis.white_player and 
                       target_player_lower in analysis.white_player.lower())
            is_black = (analysis.black_player and 
                       target_player_lower in analysis.black_player.lower())
            
            if not (is_white or is_black):
                continue
            
            # Analyze moves by the target player
            for move_analysis in analysis.analyzed_moves:
                # Determine if this is the target player's move
                is_target_move = (
                    (is_white and move_analysis.move_number % 2 == 1) or
                    (is_black and move_analysis.move_number % 2 == 0)
                )
                
                if not is_target_move:
                    continue
                
                phase = move_analysis.phase
                
                # Count blunders and mistakes by phase
                if move_analysis.is_blunder:
                    weaknesses['blunders_by_phase'][phase] += 1
                    weaknesses['worst_moves'].append({
                        'move': move_analysis.move,
                        'eval_change': move_analysis.eval_change,
                        'phase': phase,
                        'fen': move_analysis.fen_before
                    })
                
                if move_analysis.is_mistake:
                    weaknesses['mistakes_by_phase'][phase] += 1
                
                # Track centipawn loss by phase
                if move_analysis.eval_change is not None:
                    weaknesses['average_centipawn_loss_by_phase'][phase].append(
                        move_analysis.eval_change
                    )
        
        # Calculate averages
        for phase in ['opening', 'middlegame', 'endgame']:
            losses = weaknesses['average_centipawn_loss_by_phase'][phase]
            if losses:
                weaknesses['average_centipawn_loss_by_phase'][phase] = sum(losses) / len(losses)
            else:
                weaknesses['average_centipawn_loss_by_phase'][phase] = 0
        
        # Sort worst moves by evaluation change
        weaknesses['worst_moves'].sort(key=lambda x: x['eval_change'], reverse=True)
        weaknesses['worst_moves'] = weaknesses['worst_moves'][:10]  # Top 10 worst moves
        
        return weaknesses

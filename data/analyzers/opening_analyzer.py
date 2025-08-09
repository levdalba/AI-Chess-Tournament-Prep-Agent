"""
Opening preparation system for chess analysis.
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import re

try:
    import chess
    import chess.pgn
    from chess.engine import SimpleEngine
    CHESS_AVAILABLE = True
except ImportError:
    CHESS_AVAILABLE = False


@dataclass
class OpeningVariation:
    """Represents a chess opening variation."""
    eco: str
    name: str
    moves: List[str]  # List of moves in standard algebraic notation
    fen: str  # Final position FEN
    frequency: int = 0
    win_rate: float = 0.0
    draw_rate: float = 0.0
    loss_rate: float = 0.0
    average_rating: float = 0.0
    theoretical_assessment: str = ""  # "good for white", "equal", "good for black"


@dataclass
class OpeningRepertoire:
    """Complete opening repertoire for a player."""
    player_name: str
    as_white: List[OpeningVariation] = None
    as_black_vs_e4: List[OpeningVariation] = None
    as_black_vs_d4: List[OpeningVariation] = None
    as_black_vs_other: List[OpeningVariation] = None
    last_updated: Optional[str] = None
    
    def __post_init__(self):
        if self.as_white is None:
            self.as_white = []
        if self.as_black_vs_e4 is None:
            self.as_black_vs_e4 = []
        if self.as_black_vs_d4 is None:
            self.as_black_vs_d4 = []
        if self.as_black_vs_other is None:
            self.as_black_vs_other = []


class OpeningAnalyzer:
    """Analyzes opening patterns and builds repertoires."""
    
    def __init__(self):
        """Initialize the opening analyzer."""
        self.opening_database = self._load_opening_database()
        self.eco_patterns = self._build_eco_patterns()
    
    def _load_opening_database(self) -> Dict[str, Any]:
        """Load opening database with ECO codes and names."""
        # This would normally load from a comprehensive opening database
        # For now, we'll use a basic set of common openings
        return {
            "B00": {"name": "King's Pawn", "moves": ["e4"]},
            "B01": {"name": "Scandinavian Defense", "moves": ["e4", "d5"]},
            "B02": {"name": "Alekhine's Defense", "moves": ["e4", "Nf6"]},
            "B04": {"name": "Alekhine Defense: Modern Variation", "moves": ["e4", "Nf6", "d3"]},
            "B06": {"name": "Robatsch Defense", "moves": ["e4", "g6"]},
            "B07": {"name": "Pirc Defense", "moves": ["e4", "d6", "d4", "Nf6", "Nc3", "g6"]},
            "B10": {"name": "Caro-Kann Defense", "moves": ["e4", "c6"]},
            "B12": {"name": "Caro-Kann Defense: Advance Variation", "moves": ["e4", "c6", "d4", "d5", "e5"]},
            "B15": {"name": "Caro-Kann Defense: Tartakower Variation", "moves": ["e4", "c6", "d4", "d5", "Nc3", "dxe4", "Nxe4", "Nf6", "Nxf6+", "exf6"]},
            "B20": {"name": "Sicilian Defense", "moves": ["e4", "c5"]},
            "B21": {"name": "Sicilian Defense: Smith-Morra Gambit", "moves": ["e4", "c5", "d4", "cxd4", "c3"]},
            "B22": {"name": "Sicilian Defense: Alapin Variation", "moves": ["e4", "c5", "c3"]},
            "B23": {"name": "Sicilian Defense: Closed", "moves": ["e4", "c5", "Nc3"]},
            "B30": {"name": "Sicilian Defense: Old Sicilian", "moves": ["e4", "c5", "Nf3", "Nc6"]},
            "B40": {"name": "Sicilian Defense: French Variation", "moves": ["e4", "c5", "Nf3", "e6"]},
            "B50": {"name": "Sicilian Defense", "moves": ["e4", "c5", "Nf3", "d6"]},
            "B70": {"name": "Sicilian Defense: Dragon Variation", "moves": ["e4", "c5", "Nf3", "d6", "d4", "cxd4", "Nxd4", "Nf6", "Nc3", "g6"]},
            "B90": {"name": "Sicilian Defense: Najdorf Variation", "moves": ["e4", "c5", "Nf3", "d6", "d4", "cxd4", "Nxd4", "Nf6", "Nc3", "a6"]},
            "C00": {"name": "French Defense", "moves": ["e4", "e6"]},
            "C02": {"name": "French Defense: Advance Variation", "moves": ["e4", "e6", "d4", "d5", "e5"]},
            "C10": {"name": "French Defense: Rubinstein Variation", "moves": ["e4", "e6", "d4", "d5", "Nc3", "dxe4"]},
            "C15": {"name": "French Defense: Winawer Variation", "moves": ["e4", "e6", "d4", "d5", "Nc3", "Bb4"]},
            "C20": {"name": "King's Pawn Game", "moves": ["e4", "e5"]},
            "C25": {"name": "Vienna Game", "moves": ["e4", "e5", "Nc3"]},
            "C30": {"name": "King's Gambit", "moves": ["e4", "e5", "f4"]},
            "C40": {"name": "King's Knight Opening", "moves": ["e4", "e5", "Nf3"]},
            "C41": {"name": "Philidor Defense", "moves": ["e4", "e5", "Nf3", "d6"]},
            "C42": {"name": "Petrov's Defense", "moves": ["e4", "e5", "Nf3", "Nf6"]},
            "C44": {"name": "King's Pawn Game: Tayler Opening", "moves": ["e4", "e5", "Nf3", "Nc6", "Be2"]},
            "C45": {"name": "Scotch Game", "moves": ["e4", "e5", "Nf3", "Nc6", "d4"]},
            "C50": {"name": "Italian Game", "moves": ["e4", "e5", "Nf3", "Nc6", "Bc4"]},
            "C53": {"name": "Italian Game: Classical Variation", "moves": ["e4", "e5", "Nf3", "Nc6", "Bc4", "Be7"]},
            "C60": {"name": "Ruy Lopez", "moves": ["e4", "e5", "Nf3", "Nc6", "Bb5"]},
            "C65": {"name": "Ruy Lopez: Berlin Defense", "moves": ["e4", "e5", "Nf3", "Nc6", "Bb5", "Nf6"]},
            "C70": {"name": "Ruy Lopez: Morphy Defense", "moves": ["e4", "e5", "Nf3", "Nc6", "Bb5", "a6"]},
            "C80": {"name": "Ruy Lopez: Open", "moves": ["e4", "e5", "Nf3", "Nc6", "Bb5", "a6", "Ba4", "Nf6", "O-O", "Nxe4"]},
            "C90": {"name": "Ruy Lopez: Spanish Torture", "moves": ["e4", "e5", "Nf3", "Nc6", "Bb5", "a6", "Ba4", "Nf6", "O-O", "Be7"]},
            "D00": {"name": "Queen's Pawn Game", "moves": ["d4"]},
            "D02": {"name": "London System", "moves": ["d4", "Nf6", "Nf3", "g6", "Bf4"]},
            "D04": {"name": "Queen's Pawn Game: Colle System", "moves": ["d4", "Nf6", "Nf3", "e6", "e3"]},
            "D10": {"name": "Slav Defense", "moves": ["d4", "d5", "c4", "c6"]},
            "D20": {"name": "Queen's Gambit Accepted", "moves": ["d4", "d5", "c4", "dxc4"]},
            "D30": {"name": "Queen's Gambit Declined", "moves": ["d4", "d5", "c4", "e6"]},
            "D35": {"name": "Queen's Gambit Declined: Exchange Variation", "moves": ["d4", "d5", "c4", "e6", "Nc3", "Nf6", "cxd5"]},
            "D40": {"name": "Queen's Gambit Declined: Semi-Tarrasch", "moves": ["d4", "d5", "c4", "e6", "Nc3", "Nf6", "Nf3", "c5"]},
            "D50": {"name": "Queen's Gambit Declined: Modern Variation", "moves": ["d4", "d5", "c4", "e6", "Nc3", "Nf6", "Bg5"]},
            "D60": {"name": "Queen's Gambit Declined: Orthodox Defense", "moves": ["d4", "d5", "c4", "e6", "Nc3", "Nf6", "Bg5", "Be7", "e3", "O-O", "Nf3"]},
            "D70": {"name": "Neo-Grünfeld Defense", "moves": ["d4", "Nf6", "c4", "g6", "g3", "Bg7", "Bg2", "d5"]},
            "D80": {"name": "Grünfeld Defense", "moves": ["d4", "Nf6", "c4", "g6", "Nc3", "d5"]},
            "D90": {"name": "Grünfeld Defense: Three Knights Variation", "moves": ["d4", "Nf6", "c4", "g6", "Nc3", "d5", "Nf3"]},
            "E00": {"name": "Catalan Opening", "moves": ["d4", "Nf6", "c4", "e6", "g3"]},
            "E10": {"name": "Indian Game", "moves": ["d4", "Nf6", "c4", "e6", "Nf3"]},
            "E20": {"name": "Nimzo-Indian Defense", "moves": ["d4", "Nf6", "c4", "e6", "Nc3", "Bb4"]},
            "E30": {"name": "Nimzo-Indian Defense: Leningrad Variation", "moves": ["d4", "Nf6", "c4", "e6", "Nc3", "Bb4", "Bg5"]},
            "E40": {"name": "Nimzo-Indian Defense: Normal Variation", "moves": ["d4", "Nf6", "c4", "e6", "Nc3", "Bb4", "e3"]},
            "E60": {"name": "King's Indian Defense", "moves": ["d4", "Nf6", "c4", "g6", "Nc3", "Bg7", "Nf3"]},
            "E70": {"name": "King's Indian Defense: Normal Variation", "moves": ["d4", "Nf6", "c4", "g6", "Nc3", "Bg7", "e4"]},
            "E90": {"name": "King's Indian Defense: Orthodox Variation", "moves": ["d4", "Nf6", "c4", "g6", "Nc3", "Bg7", "e4", "d6", "Nf3", "O-O", "Be2"]},
            "A00": {"name": "Uncommon Opening", "moves": ["b3"]},  # English Opening, Réti, etc.
            "A04": {"name": "Réti Opening", "moves": ["Nf3"]},
            "A10": {"name": "English Opening", "moves": ["c4"]},
            "A15": {"name": "English Opening: Anglo-Indian Defense", "moves": ["c4", "Nf6"]},
            "A20": {"name": "English Opening: King's English Variation", "moves": ["c4", "e5"]},
            "A30": {"name": "English Opening: Symmetrical Variation", "moves": ["c4", "c5"]},
        }
    
    def _build_eco_patterns(self) -> Dict[str, str]:
        """Build regex patterns for ECO code detection."""
        patterns = {}
        for eco, data in self.opening_database.items():
            # Convert moves to a pattern for matching
            moves_pattern = "|".join(data["moves"])
            patterns[eco] = moves_pattern
        return patterns
    
    def identify_opening(self, moves: List[str]) -> Tuple[Optional[str], Optional[str]]:
        """Identify opening from move sequence."""
        if not moves:
            return None, None
        
        # Try to match against known patterns
        best_match_eco = None
        best_match_name = None
        best_match_depth = 0
        
        for eco, data in self.opening_database.items():
            opening_moves = data["moves"]
            
            # Check how many moves match from the beginning
            match_depth = 0
            for i, move in enumerate(opening_moves):
                if i < len(moves) and moves[i] == move:
                    match_depth += 1
                else:
                    break
            
            # Update best match if this is deeper
            if match_depth > best_match_depth and match_depth == len(opening_moves):
                best_match_eco = eco
                best_match_name = data["name"]
                best_match_depth = match_depth
        
        return best_match_eco, best_match_name
    
    def analyze_player_openings(self, games_data: List[Dict[str, Any]], 
                              target_player: str) -> OpeningRepertoire:
        """Analyze a player's opening repertoire from their games."""
        repertoire = OpeningRepertoire(player_name=target_player)
        
        # Track opening statistics
        white_openings = defaultdict(lambda: {
            'count': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'moves': []
        })
        black_e4_openings = defaultdict(lambda: {
            'count': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'moves': []
        })
        black_d4_openings = defaultdict(lambda: {
            'count': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'moves': []
        })
        black_other_openings = defaultdict(lambda: {
            'count': 0, 'wins': 0, 'draws': 0, 'losses': 0, 'moves': []
        })
        
        target_player_lower = target_player.lower()
        
        for game in games_data:
            # Extract game info
            white_player = game.get('white', '').lower()
            black_player = game.get('black', '').lower()
            result = game.get('result', '*')
            moves = game.get('moves', [])
            pgn = game.get('pgn', '')
            
            if not moves and pgn:
                moves = self._extract_moves_from_pgn(pgn)
            
            if len(moves) < 2:
                continue
            
            # Determine if target player is white or black
            is_white = target_player_lower in white_player
            is_black = target_player_lower in black_player
            
            if not (is_white or is_black):
                continue
            
            # Identify the opening
            eco, opening_name = self.identify_opening(moves[:10])  # Use first 10 moves
            if not eco:
                continue
            
            # Determine result from target player's perspective
            if is_white:
                if result == '1-0':
                    player_result = 'win'
                elif result == '0-1':
                    player_result = 'loss'
                else:
                    player_result = 'draw'
            else:
                if result == '0-1':
                    player_result = 'win'
                elif result == '1-0':
                    player_result = 'loss'
                else:
                    player_result = 'draw'
            
            # Categorize the opening
            if is_white:
                stats = white_openings[eco]
                stats['moves'] = moves[:10]
                stats['count'] += 1
                if player_result == 'win':
                    stats['wins'] += 1
                elif player_result == 'loss':
                    stats['losses'] += 1
                else:
                    stats['draws'] += 1
            
            else:  # is_black
                first_move = moves[0] if moves else ""
                
                if first_move == 'e4':
                    stats = black_e4_openings[eco]
                elif first_move == 'd4':
                    stats = black_d4_openings[eco]
                else:
                    stats = black_other_openings[eco]
                
                stats['moves'] = moves[:10]
                stats['count'] += 1
                if player_result == 'win':
                    stats['wins'] += 1
                elif player_result == 'loss':
                    stats['losses'] += 1
                else:
                    stats['draws'] += 1
        
        # Convert statistics to OpeningVariation objects
        def create_variations(opening_stats: Dict) -> List[OpeningVariation]:
            variations = []
            for eco, stats in opening_stats.items():
                if stats['count'] >= 2:  # Only include if played at least twice
                    total_games = stats['count']
                    win_rate = stats['wins'] / total_games
                    draw_rate = stats['draws'] / total_games
                    loss_rate = stats['losses'] / total_games
                    
                    opening_name = self.opening_database.get(eco, {}).get('name', 'Unknown Opening')
                    
                    variation = OpeningVariation(
                        eco=eco,
                        name=opening_name,
                        moves=stats['moves'],
                        fen="",  # Would need to calculate
                        frequency=total_games,
                        win_rate=win_rate,
                        draw_rate=draw_rate,
                        loss_rate=loss_rate
                    )
                    variations.append(variation)
            
            # Sort by frequency
            variations.sort(key=lambda x: x.frequency, reverse=True)
            return variations
        
        repertoire.as_white = create_variations(white_openings)
        repertoire.as_black_vs_e4 = create_variations(black_e4_openings)
        repertoire.as_black_vs_d4 = create_variations(black_d4_openings)
        repertoire.as_black_vs_other = create_variations(black_other_openings)
        
        return repertoire
    
    def _extract_moves_from_pgn(self, pgn_string: str) -> List[str]:
        """Extract moves from PGN string."""
        if not CHESS_AVAILABLE:
            # Fallback: basic regex parsing
            moves = []
            # Remove comments and annotations
            clean_pgn = re.sub(r'\{[^}]*\}', '', pgn_string)
            clean_pgn = re.sub(r'\([^)]*\)', '', clean_pgn)
            
            # Extract moves (basic pattern)
            move_pattern = r'\d+\.\s*([a-zA-Z][a-zA-Z0-9+#=\-]*)\s*([a-zA-Z][a-zA-Z0-9+#=\-]*)?'
            matches = re.findall(move_pattern, clean_pgn)
            
            for match in matches:
                moves.append(match[0])
                if match[1]:
                    moves.append(match[1])
            
            return moves
        
        try:
            game = chess.pgn.read_game(chess.io.StringIO(pgn_string))
            if game:
                board = game.board()
                moves = []
                for move in game.mainline_moves():
                    moves.append(board.san(move))
                    board.push(move)
                return moves
        except:
            pass
        
        return []
    
    def compare_repertoires(self, player1_repertoire: OpeningRepertoire, 
                          player2_repertoire: OpeningRepertoire) -> Dict[str, Any]:
        """Compare two players' opening repertoires."""
        comparison = {
            'common_openings': {
                'as_white': [],
                'as_black_vs_e4': [],
                'as_black_vs_d4': [],
                'as_black_vs_other': []
            },
            'unique_to_player1': {
                'as_white': [],
                'as_black_vs_e4': [],
                'as_black_vs_d4': [],
                'as_black_vs_other': []
            },
            'unique_to_player2': {
                'as_white': [],
                'as_black_vs_e4': [],
                'as_black_vs_d4': [],
                'as_black_vs_other': []
            }
        }
        
        categories = ['as_white', 'as_black_vs_e4', 'as_black_vs_d4', 'as_black_vs_other']
        
        for category in categories:
            p1_openings = set(v.eco for v in getattr(player1_repertoire, category))
            p2_openings = set(v.eco for v in getattr(player2_repertoire, category))
            
            common = p1_openings.intersection(p2_openings)
            unique_p1 = p1_openings - p2_openings
            unique_p2 = p2_openings - p1_openings
            
            # Get the actual opening objects
            p1_openings_dict = {v.eco: v for v in getattr(player1_repertoire, category)}
            p2_openings_dict = {v.eco: v for v in getattr(player2_repertoire, category)}
            
            comparison['common_openings'][category] = [
                {'player1': p1_openings_dict[eco], 'player2': p2_openings_dict[eco]}
                for eco in common
            ]
            
            comparison['unique_to_player1'][category] = [
                p1_openings_dict[eco] for eco in unique_p1
            ]
            
            comparison['unique_to_player2'][category] = [
                p2_openings_dict[eco] for eco in unique_p2
            ]
        
        return comparison
    
    def get_preparation_suggestions(self, target_repertoire: OpeningRepertoire) -> Dict[str, Any]:
        """Generate preparation suggestions based on repertoire analysis."""
        suggestions = {
            'strengths': [],
            'weaknesses': [],
            'recommendations': []
        }
        
        # Analyze as White
        for opening in target_repertoire.as_white:
            if opening.win_rate > 0.6 and opening.frequency >= 5:
                suggestions['strengths'].append({
                    'type': 'white_opening',
                    'opening': opening.name,
                    'eco': opening.eco,
                    'reason': f"Strong performance: {opening.win_rate:.1%} win rate in {opening.frequency} games"
                })
            elif opening.win_rate < 0.4 and opening.frequency >= 3:
                suggestions['weaknesses'].append({
                    'type': 'white_opening',
                    'opening': opening.name,
                    'eco': opening.eco,
                    'reason': f"Poor performance: {opening.win_rate:.1%} win rate in {opening.frequency} games"
                })
        
        # Analyze as Black
        all_black_openings = (target_repertoire.as_black_vs_e4 + 
                             target_repertoire.as_black_vs_d4 + 
                             target_repertoire.as_black_vs_other)
        
        for opening in all_black_openings:
            if opening.win_rate > 0.5 and opening.frequency >= 5:
                suggestions['strengths'].append({
                    'type': 'black_defense',
                    'opening': opening.name,
                    'eco': opening.eco,
                    'reason': f"Solid defense: {opening.win_rate:.1%} score in {opening.frequency} games"
                })
            elif opening.win_rate < 0.35 and opening.frequency >= 3:
                suggestions['weaknesses'].append({
                    'type': 'black_defense',
                    'opening': opening.name,
                    'eco': opening.eco,
                    'reason': f"Struggling defense: {opening.win_rate:.1%} score in {opening.frequency} games"
                })
        
        # Generate recommendations
        if len(target_repertoire.as_white) < 3:
            suggestions['recommendations'].append({
                'type': 'expand_repertoire',
                'category': 'white',
                'suggestion': "Consider expanding your opening repertoire as White"
            })
        
        if len(target_repertoire.as_black_vs_e4) < 2:
            suggestions['recommendations'].append({
                'type': 'expand_repertoire',
                'category': 'black_vs_e4',
                'suggestion': "Develop more defenses against 1.e4"
            })
        
        if len(target_repertoire.as_black_vs_d4) < 2:
            suggestions['recommendations'].append({
                'type': 'expand_repertoire',
                'category': 'black_vs_d4',
                'suggestion': "Develop more defenses against 1.d4"
            })
        
        return suggestions

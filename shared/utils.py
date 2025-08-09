from typing import Optional, List
import re
from pathlib import Path

class ChessUtils:
    """Utility functions for chess-related operations"""
    
    @staticmethod
    def is_valid_pgn(pgn_content: str) -> bool:
        """Check if PGN content is valid"""
        if not pgn_content.strip():
            return False
        
        # Basic PGN validation - should contain game metadata and moves
        has_result = any(result in pgn_content for result in ["1-0", "0-1", "1/2-1/2", "*"])
        has_moves = bool(re.search(r'\d+\.', pgn_content))
        
        return has_result and has_moves
    
    @staticmethod
    def extract_eco_from_moves(moves: str) -> Optional[str]:
        """Extract ECO code from move sequence if possible"""
        # This would be expanded with a proper ECO database
        common_openings = {
            "1.e4 e5": "C20",  # King's Pawn Game
            "1.e4 c5": "B20",  # Sicilian Defense
            "1.d4 d5": "D00",  # Queen's Pawn Game
            "1.Nf3 Nf6": "A04", # Reti Opening
        }
        
        for opening_moves, eco in common_openings.items():
            if moves.startswith(opening_moves):
                return eco
        return None
    
    @staticmethod
    def get_game_phase(move_number: int) -> str:
        """Determine game phase based on move number"""
        if move_number <= 15:
            return "opening"
        elif move_number <= 40:
            return "middlegame"
        else:
            return "endgame"
    
    @staticmethod
    def centipawns_to_advantage(centipawns: float) -> str:
        """Convert centipawn evaluation to human-readable advantage"""
        abs_cp = abs(centipawns)
        color = "White" if centipawns > 0 else "Black"
        
        if abs_cp < 50:
            return "Equal"
        elif abs_cp < 150:
            return f"Slight advantage for {color}"
        elif abs_cp < 300:
            return f"Clear advantage for {color}"
        else:
            return f"Winning for {color}"

class ValidationUtils:
    """Utility functions for data validation"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_rating(rating: int) -> bool:
        """Validate chess rating range"""
        return 0 <= rating <= 4000
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage"""
        # Remove or replace unsafe characters
        safe_chars = re.sub(r'[^\w\-_.]', '_', filename)
        return safe_chars[:255]  # Limit length

class FileUtils:
    """Utility functions for file operations"""
    
    @staticmethod
    def ensure_directory(directory: Path) -> None:
        """Ensure directory exists, create if not"""
        directory.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def get_file_size(file_path: Path) -> int:
        """Get file size in bytes"""
        return file_path.stat().st_size if file_path.exists() else 0
    
    @staticmethod
    def is_pgn_file(filename: str) -> bool:
        """Check if filename has .pgn extension"""
        return filename.lower().endswith('.pgn')

"""
Bomb Sweep — Game Engine
========================
Pure Python game engine. No web dependencies.
Works on both server-side (Flask) and client-side (PyScript).

This module contains ALL core game logic:
- Bomb placement using Python's random
- Adjacent bomb calculation
- Cell reveal with life deduction
- Win/loss detection
- Statistics tracking
- Board serialization

Author: Yashas K Gangatkar
"""

import random
import json
import time


# ═══════════════════════════════════════════════════════════
# GAME CONSTANTS
# ═══════════════════════════════════════════════════════════

GRID_SIZE = 10
TOTAL_CELLS = GRID_SIZE * GRID_SIZE  # 100 cells
NUM_BOMBS = 5
TOTAL_SAFE = TOTAL_CELLS - NUM_BOMBS  # 95 safe cells
MAX_LIVES = 1


# ═══════════════════════════════════════════════════════════
# BOMB PLACEMENT ENGINE
# ═══════════════════════════════════════════════════════════

class BombPlacer:
    """
    Handles random bomb placement on the grid.
    Uses Python's random.sample for uniform distribution.

    The placement algorithm ensures:
    - Bombs are spread across the entire grid
    - No duplicate positions
    - True randomness using Python's Mersenne Twister
    """

    @staticmethod
    def place(num_bombs=NUM_BOMBS, grid_size=GRID_SIZE):
        """
        Place bombs randomly on the grid.

        Args:
            num_bombs (int): Number of bombs to place (default: 3)
            grid_size (int): Size of the grid (default: 8 for 8x8)

        Returns:
            set: Set of cell indices where bombs are placed

        Example:
            >>> placer = BombPlacer()
            >>> bombs = placer.place(3, 8)
            >>> len(bombs)
            3
            >>> all(0 <= b < 64 for b in bombs)
            True
        """
        total = grid_size * grid_size
        if num_bombs > total:
            raise ValueError(f"Cannot place {num_bombs} bombs on a {grid_size}x{grid_size} grid")
        indices = random.sample(range(total), num_bombs)
        return set(indices)

    @staticmethod
    def place_with_safe_zone(safe_index, num_bombs=NUM_BOMBS, grid_size=GRID_SIZE):
        """
        Place bombs avoiding a specific cell (useful for first-click safety).

        Args:
            safe_index (int): Cell index to avoid placing a bomb
            num_bombs (int): Number of bombs to place
            grid_size (int): Size of the grid

        Returns:
            set: Set of cell indices where bombs are placed
        """
        total = grid_size * grid_size
        available = [i for i in range(total) if i != safe_index]
        indices = random.sample(available, num_bombs)
        return set(indices)


# ═══════════════════════════════════════════════════════════
# ADJACENT CALCULATOR
# ═══════════════════════════════════════════════════════════

class AdjacentCalculator:
    """
    Calculates how many bombs are adjacent to each cell.

    Uses 8-directional adjacency checking (including diagonals).
    This is the core mechanic that tells the player how close
    they are to danger.

    The calculation uses row/column math:
    - Convert flat index to (row, col) using divmod
    - Check all 8 neighbors
    - Convert back to flat index for comparison
    """

    @staticmethod
    def calculate_for_cell(cell_index, bomb_indices, grid_size=GRID_SIZE):
        """
        Count adjacent bombs for a single cell.

        Args:
            cell_index (int): The cell to check
            bomb_indices (set): Set of bomb positions
            grid_size (int): Grid dimension

        Returns:
            int: Number of adjacent bombs (0-8)
        """
        row, col = divmod(cell_index, grid_size)
        count = 0
        for delta_row in (-1, 0, 1):
            for delta_col in (-1, 0, 1):
                if delta_row == 0 and delta_col == 0:
                    continue
                neighbor_row = row + delta_row
                neighbor_col = col + delta_col
                if 0 <= neighbor_row < grid_size and 0 <= neighbor_col < grid_size:
                    neighbor_idx = neighbor_row * grid_size + neighbor_col
                    if neighbor_idx in bomb_indices:
                        count += 1
        return count

    @staticmethod
    def calculate_all(bomb_indices, grid_size=GRID_SIZE):
        """
        Pre-calculate adjacent bomb counts for ALL cells.

        This runs once at game start so we don't need to
        recalculate on every click.

        Args:
            bomb_indices (set): Set of bomb positions
            grid_size (int): Grid dimension

        Returns:
            dict: Mapping of cell_index -> adjacent_bomb_count
        """
        adjacent_map = {}
        for i in range(grid_size * grid_size):
            adjacent_map[i] = AdjacentCalculator.calculate_for_cell(
                i, bomb_indices, grid_size
            )
        return adjacent_map


# ═══════════════════════════════════════════════════════════
# CELL REVEAL RESULT
# ═══════════════════════════════════════════════════════════

class RevealResult:
    """
    Data class representing the result of revealing a cell.

    Encapsulates all information the UI needs to update:
    - Whether the cell was safe or a bomb
    - Current game status (playing, won, lost)
    - Remaining lives
    - Adjacent bomb count (for safe cells)
    - Progress information

    This is returned by the game engine and consumed by
    both the Flask API and the PyScript UI layer.
    """

    def __init__(self, safe, status, lives, bomb_index=None,
                 adjacent=None, revealed_count=0, error=None):
        self.safe = safe
        self.status = status
        self.lives = lives
        self.bomb_index = bomb_index
        self.adjacent = adjacent
        self.revealed_count = revealed_count
        self.error = error

    def to_dict(self):
        """Convert to dictionary for JSON serialization (Flask API)."""
        result = {
            "safe": self.safe,
            "status": self.status,
            "lives": self.lives,
            "revealed_count": self.revealed_count,
        }
        if self.bomb_index is not None:
            result["bomb_index"] = self.bomb_index
        if self.adjacent is not None:
            result["adjacent"] = self.adjacent
        if self.error is not None:
            result["error"] = self.error
        return result

    def to_json(self):
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


# ═══════════════════════════════════════════════════════════
# GAME STATISTICS
# ═══════════════════════════════════════════════════════════

class GameStatistics:
    """
    Tracks player statistics across multiple games.

    Persists data using Python's json module.
    On PyScript, uses localStorage as a fallback.

    Tracked metrics:
    - Total games played
    - Total wins and losses
    - Current win streak
    - Best win streak ever
    - Win rate percentage
    - Average revealed cells per game
    """

    def __init__(self):
        self.games_played = 0
        self.total_wins = 0
        self.total_losses = 0
        self.current_streak = 0
        self.best_streak = 0
        self.total_cells_revealed = 0

    @property
    def win_rate(self):
        """Calculate win rate as a percentage."""
        if self.games_played == 0:
            return 0.0
        return (self.total_wins / self.games_played) * 100

    @property
    def avg_revealed(self):
        """Calculate average cells revealed per game."""
        if self.games_played == 0:
            return 0.0
        return self.total_cells_revealed / self.games_played

    def record_win(self, cells_revealed):
        """Record a game win."""
        self.games_played += 1
        self.total_wins += 1
        self.current_streak += 1
        self.total_cells_revealed += cells_revealed
        if self.current_streak > self.best_streak:
            self.best_streak = self.current_streak

    def record_loss(self, cells_revealed):
        """Record a game loss."""
        self.games_played += 1
        self.total_losses += 1
        self.current_streak = 0
        self.total_cells_revealed += cells_revealed

    def to_dict(self):
        """Convert to dictionary for serialization."""
        return {
            "games_played": self.games_played,
            "total_wins": self.total_wins,
            "total_losses": self.total_losses,
            "current_streak": self.current_streak,
            "best_streak": self.best_streak,
            "win_rate": round(self.win_rate, 1),
            "avg_revealed": round(self.avg_revealed, 1),
        }

    def to_json(self):
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


# ═══════════════════════════════════════════════════════════
# MAIN GAME CLASS
# ═══════════════════════════════════════════════════════════

class BombSweepGame:
    """
    Complete Bomb Sweep game engine — 100% Python.

    This class manages the entire game lifecycle:
    1. Creating a new game with random bomb placement
    2. Processing cell reveal requests
    3. Tracking lives and game state
    4. Detecting win/loss conditions
    5. Providing board data for UI rendering

    The game rules:
    - 10x10 grid with 35 hidden bombs
    - Player has 1 life
    - Clicking a bomb costs 1 life (instant Game Over)
    - Losing all lives = Game Over
    - Revealing all 65 safe cells = Win (5-Star Chocolate!)
    - Approximately 1% win probability

    Usage:
        >>> game = BombSweepGame()
        >>> game.new_game()
        >>> result = game.reveal_cell(0)
        >>> print(result.status)
        'playing'
    """

    def __init__(self, grid_size=GRID_SIZE, num_bombs=NUM_BOMBS,
                 max_lives=MAX_LIVES):
        """
        Initialize a new game instance.

        Args:
            grid_size (int): Grid dimension (default: 8)
            num_bombs (int): Number of hidden bombs (default: 3)
            max_lives (int): Starting lives (default: 2)
        """
        self.grid_size = grid_size
        self.num_bombs = num_bombs
        self.max_lives = max_lives
        self.total_cells = grid_size * grid_size
        self.total_safe = self.total_cells - num_bombs

        # Game state
        self.bomb_indices = set()
        self.adjacent_map = {}
        self.revealed = set()
        self.lives = max_lives
        self.status = "idle"  # idle | playing | won | lost
        self.created_at = None

        # Statistics
        self.stats = GameStatistics()

        # Bomb placement and calculation engines
        self._placer = BombPlacer()
        self._calculator = AdjacentCalculator()

    def new_game(self):
        """
        Start a new game with fresh bomb placement.

        This method:
        1. Places bombs randomly using Python's random.sample
        2. Pre-calculates adjacent counts for all 64 cells
        3. Resets game state (lives, revealed cells, status)
        4. Records the creation timestamp

        Returns:
            dict: Game configuration for the UI
        """
        # Place bombs using Python's random
        self.bomb_indices = self._placer.place(
            self.num_bombs, self.grid_size
        )

        # Pre-calculate all adjacent counts
        self.adjacent_map = self._calculator.calculate_all(
            self.bomb_indices, self.grid_size
        )

        # Reset state
        self.revealed = set()
        self.lives = self.max_lives
        self.status = "playing"
        self.created_at = time.time()

        print(f"[PYTHON] New game: {self.num_bombs} bombs at "
              f"{sorted(self.bomb_indices)}, {self.max_lives} lives")

        return {
            "grid_size": self.grid_size,
            "total_cells": self.total_cells,
            "num_bombs": self.num_bombs,
            "lives": self.lives,
            "total_safe": self.total_safe,
        }

    def reveal_cell(self, cell_index):
        """
        Reveal a cell on the grid — core game logic.

        This is the main interaction method. When a player
        clicks a cell, this method determines:
        - Is it a bomb? (lose a life or game over)
        - Is it safe? (show adjacent count)
        - Did they win? (all safe cells revealed)

        Args:
            cell_index (int): The cell to reveal (0-63)

        Returns:
            RevealResult: Complete result with status, lives, etc.
        """
        # Validation
        if self.status != "playing":
            return RevealResult(
                safe=False, status=self.status, lives=self.lives,
                error="Game not in progress"
            )

        if cell_index in self.revealed:
            return RevealResult(
                safe=False, status=self.status, lives=self.lives,
                error="Cell already revealed"
            )

        if cell_index < 0 or cell_index >= self.total_cells:
            return RevealResult(
                safe=False, status=self.status, lives=self.lives,
                error=f"Cell index must be 0-{self.total_cells - 1}"
            )

        # ═══ BOMB HIT ═══
        if cell_index in self.bomb_indices:
            self.revealed.add(cell_index)
            self.lives -= 1

            if self.lives <= 0:
                # GAME OVER — all lives lost
                self.status = "lost"
                self.stats.record_loss(len(self.revealed))
                print(f"[PYTHON] BOOM at cell {cell_index}! GAME OVER!")
                return RevealResult(
                    safe=False, status="lost", lives=0,
                    bomb_index=cell_index,
                    revealed_count=len(self.revealed)
                )
            else:
                # Lost a life but still playing
                print(f"[PYTHON] BOOM at cell {cell_index}! "
                      f"{self.lives} lives remaining")
                return RevealResult(
                    safe=False, status="playing", lives=self.lives,
                    bomb_index=cell_index,
                    revealed_count=len(self.revealed)
                )

        # ═══ SAFE CELL ═══
        self.revealed.add(cell_index)
        adjacent = self.adjacent_map[cell_index]
        revealed_count = len(self.revealed)

        # ═══ WIN CHECK ═══
        if revealed_count >= self.total_safe:
            self.status = "won"
            self.stats.record_win(revealed_count)
            print(f"[PYTHON] WIN! Streak: {self.stats.current_streak}")
            return RevealResult(
                safe=True, status="won", lives=self.lives,
                adjacent=adjacent,
                revealed_count=revealed_count
            )

        # Normal safe reveal
        return RevealResult(
            safe=True, status="playing", lives=self.lives,
            adjacent=adjacent,
            revealed_count=revealed_count
        )

    def reveal_all(self):
        """
        Get the full board data for end-of-game reveal.

        Returns all cell information including bomb positions
        and adjacent counts for cells not yet revealed.

        Returns:
            dict: Complete board data with cell map
        """
        cell_map = {}
        for i in range(self.total_cells):
            cell_map[i] = {
                "is_bomb": i in self.bomb_indices,
                "adjacent": self.adjacent_map[i],
                "revealed": i in self.revealed,
            }
        return {
            "status": self.status,
            "cell_map": cell_map,
            "bomb_indices": list(self.bomb_indices),
            "lives": self.lives,
        }

    def get_bombs_remaining(self):
        """
        Calculate how many bombs haven't been found yet.

        Returns:
            int: Number of unfound bombs
        """
        found_bombs = sum(1 for idx in self.revealed
                         if idx in self.bomb_indices)
        return self.num_bombs - found_bombs

    def get_progress(self):
        """
        Get current game progress information.

        Returns:
            dict: Progress data (revealed count, total safe, percentage)
        """
        safe_revealed = len(self.revealed) - sum(
            1 for idx in self.revealed if idx in self.bomb_indices
        )
        percentage = (safe_revealed / self.total_safe) * 100
        return {
            "revealed_count": len(self.revealed),
            "total_safe": self.total_safe,
            "percentage": round(percentage, 1),
        }

    def is_game_over(self):
        """Check if the game has ended."""
        return self.status in ("won", "lost")

    def is_playing(self):
        """Check if the game is currently in progress."""
        return self.status == "playing"

    def get_cell_info(self, cell_index):
        """
        Get information about a specific cell.

        Args:
            cell_index (int): Cell to query

        Returns:
            dict: Cell information (bomb, adjacent, revealed)
        """
        return {
            "is_bomb": cell_index in self.bomb_indices,
            "adjacent": self.adjacent_map.get(cell_index, 0),
            "revealed": cell_index in self.revealed,
        }

    def __repr__(self):
        return (f"BombSweepGame(status={self.status}, "
                f"lives={self.lives}, "
                f"revealed={len(self.revealed)}/{self.total_safe})")

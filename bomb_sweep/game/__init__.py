"""
Bomb Sweep — Game Package
=========================
Core Python game engine for Bomb Sweep.

This package contains all game logic, fully implemented in Python:
- engine.py: BombSweepGame class, bomb placement, adjacent calculation,
  reveal logic, lives system, win/loss detection, statistics
"""

from .engine import (
    BombSweepGame,
    BombPlacer,
    AdjacentCalculator,
    RevealResult,
    GameStatistics,
    GRID_SIZE,
    TOTAL_CELLS,
    NUM_BOMBS,
    TOTAL_SAFE,
    MAX_LIVES,
)

__version__ = "2.0.0"
__all__ = [
    "BombSweepGame",
    "BombPlacer",
    "AdjacentCalculator",
    "RevealResult",
    "GameStatistics",
    "GRID_SIZE",
    "TOTAL_CELLS",
    "NUM_BOMBS",
    "TOTAL_SAFE",
    "MAX_LIVES",
]

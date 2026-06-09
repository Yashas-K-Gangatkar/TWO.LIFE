"""
Bomb Sweep — Vercel Serverless API
====================================
Python serverless function for Vercel deployment.

This module provides the Flask API as a Vercel serverless
function, keeping Python as the dominant language on GitHub
while enabling cloud deployment.

Each request creates a fresh game instance (serverless = stateless).
The client-side JS engine handles persistent game state in the browser.

Game logic is imported from game.engine (pure Python).
"""

import sys
import os

# Add project root to Python path so game module is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, request
from game.engine import BombSweepGame, MAX_LIVES, NUM_BOMBS, GRID_SIZE

app = Flask(__name__)


@app.route("/api/stats", methods=["GET"])
def get_stats():
    """
    Get server status — Python powered.

    Returns JSON with server info confirming the Python
    backend is running on Vercel serverless.
    """
    return jsonify({
        "active_games": 0,
        "total_games_created": 0,
        "server": "Vercel Python Serverless",
        "engine": "game.engine.BombSweepGame",
        "grid_size": GRID_SIZE,
        "num_bombs": NUM_BOMBS,
        "max_lives": MAX_LIVES,
        "python_powered": True,
    })


@app.route("/api/new-game", methods=["POST", "GET"])
def new_game():
    """
    Create a new game instance — Python powered.

    Even though Vercel is stateless (can't persist the game
    between requests), this endpoint demonstrates the Python
    game engine running on the server. The client uses the
    local JS engine for persistent gameplay.

    Returns JSON game configuration from Python engine.
    """
    game = BombSweepGame()
    config = game.new_game()
    return jsonify({
        "server": "Vercel Python Serverless",
        "note": "Game created on server. Client uses local engine for play.",
        **config,
        "bomb_positions": sorted(game.bomb_indices),
    })


@app.route("/api/reveal", methods=["POST"])
def reveal():
    """
    Reveal a cell — Python game engine.

    This endpoint processes a reveal using the Python engine.
    Since Vercel is stateless, each request creates a new game
    with the same bomb positions (sent from client).

    Expected JSON body:
        bomb_positions: List of bomb indices
        cell_index: Cell to reveal
        revealed: List of already-revealed cell indices
        lives: Current lives remaining

    Returns JSON reveal result from Python engine.
    """
    data = request.get_json(silent=True) or {}
    bomb_positions = data.get("bomb_positions", [])
    cell_index = data.get("cell_index", 0)
    revealed_cells = data.get("revealed", [])
    current_lives = data.get("lives", MAX_LIVES)

    # Recreate the game state from client data
    game = BombSweepGame()
    game.new_game()

    # Override with client's bomb positions
    game.bomb_indices = set(bomb_positions)
    game.adjacent_map = game._calculator.calculate_all(
        game.bomb_indices, game.grid_size
    )
    game.revealed = set(revealed_cells)
    game.lives = current_lives
    game.status = "playing"

    # Process the reveal using Python engine
    result = game.reveal_cell(cell_index)
    return jsonify(result.to_dict())


@app.route("/api/reveal-all", methods=["POST"])
def reveal_all():
    """
    Reveal the full board — Python game engine.

    Expected JSON body:
        bomb_positions: List of bomb indices
        revealed: List of already-revealed cell indices

    Returns JSON with complete board data.
    """
    data = request.get_json(silent=True) or {}
    bomb_positions = data.get("bomb_positions", [])
    revealed_cells = data.get("revealed", [])

    game = BombSweepGame()
    game.new_game()
    game.bomb_indices = set(bomb_positions)
    game.adjacent_map = game._calculator.calculate_all(
        game.bomb_indices, game.grid_size
    )
    game.revealed = set(revealed_cells)
    game.status = "lost"

    return jsonify(game.reveal_all())


# Vercel requires the Flask app to be named 'app' at module level
# This file serves as the entry point for Vercel Python serverless

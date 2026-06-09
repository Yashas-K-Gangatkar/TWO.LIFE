"""
Bomb Sweep — Flask API Server
==============================
Python Flask server that provides REST API endpoints
for the Bomb Sweep game.

All game logic is delegated to the Python game engine
(game.engine.BombSweepGame). This server handles:
- HTTP routing
- JSON request/response parsing
- Session management with UUID keys
- Periodic cleanup of old games

Run:  python3 server.py
Open: http://127.0.0.1:5001
"""

import os
import uuid
import time
from flask import Flask, jsonify, request, send_file, send_from_directory
from game.engine import BombSweepGame, MAX_LIVES, NUM_BOMBS, GRID_SIZE

app = Flask(__name__)

# Serve the project root so PyScript can load .py files
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# ═══════════════════════════════════════════════════════════
# IN-MEMORY GAME STORAGE
# ═══════════════════════════════════════════════════════════

games = {}
GAME_EXPIRY_SECONDS = 1800  # 30 minutes


def cleanup_expired_games():
    """Remove games older than GAME_EXPIRY_SECONDS to prevent memory leaks."""
    now = time.time()
    expired_ids = [
        game_id for game_id, game in games.items()
        if now - game.created_at > GAME_EXPIRY_SECONDS
    ]
    for game_id in expired_ids:
        del games[game_id]
    if expired_ids:
        print(f"[SERVER] Cleaned up {len(expired_ids)} expired games")


# ═══════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════

@app.route("/")
def index():
    """Serve the game page (Python-powered HTML)."""
    return send_file("templates/index.html")


@app.route("/<path:filename>")
def serve_project_file(filename):
    """
    Serve project files so PyScript can load .py files.

    This allows the HTML page to reference:
      <py-script src="pyscript_app.py">

    And PyScript can import from the game package.
    """
    safe_path = os.path.join(PROJECT_ROOT, filename)
    if os.path.isfile(safe_path):
        return send_from_directory(PROJECT_ROOT, filename)
    return jsonify({"error": "File not found"}), 404


@app.route("/api/new-game", methods=["POST"])
def new_game():
    """
    Start a new game.

    Creates a BombSweepGame instance (Python), places bombs
    randomly, and returns the game configuration.

    Returns JSON:
        game_id: Unique game identifier (UUID)
        grid_size: 8
        total_cells: 64
        num_bombs: 3
        lives: 2
        total_safe: 61
    """
    cleanup_expired_games()

    game_id = str(uuid.uuid4())
    game = BombSweepGame()
    config = game.new_game()
    games[game_id] = game

    print(f"[SERVER] New game: {game_id[:8]}... "
          f"bombs={sorted(game.bomb_indices)} lives={MAX_LIVES}")

    return jsonify({
        "game_id": game_id,
        **config,
    })


@app.route("/api/reveal", methods=["POST"])
def reveal():
    """
    Reveal a cell in an existing game.

    The Python game engine processes the reveal and returns
    whether the cell was safe or a bomb, remaining lives,
    and the current game status.

    Expected JSON body:
        game_id: Game identifier from /api/new-game
        cell_index: Cell to reveal (0-63)

    Returns JSON:
        safe: True/False
        status: "playing" | "won" | "lost"
        lives: Remaining lives
        adjacent: Adjacent bomb count (if safe)
        bomb_index: Bomb position (if bomb hit)
        revealed_count: Total cells revealed
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    game_id = data.get("game_id")
    cell_index = data.get("cell_index")

    if game_id is None or cell_index is None:
        return jsonify({"error": "Missing game_id or cell_index"}), 400

    if game_id not in games:
        return jsonify({"error": "Game not found. Start a new game."}), 404

    game = games[game_id]

    try:
        cell_index = int(cell_index)
    except (ValueError, TypeError):
        return jsonify({"error": "cell_index must be an integer"}), 400

    # Call the Python game engine
    result = game.reveal_cell(cell_index)

    if result.error:
        return jsonify(result.to_dict()), 400

    return jsonify(result.to_dict())


@app.route("/api/reveal-all", methods=["POST"])
def reveal_all():
    """
    Reveal the complete board after game over.

    Shows all bomb positions and adjacent counts for
    cells that weren't revealed during gameplay.

    Expected JSON body:
        game_id: Game identifier

    Returns JSON:
        status: Game status
        cell_map: Dict of all cells with bomb/adjacent data
        bomb_indices: List of bomb positions
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    game_id = data.get("game_id")
    if game_id not in games:
        return jsonify({"error": "Game not found"}), 404

    game = games[game_id]
    return jsonify(game.reveal_all())


@app.route("/api/stats", methods=["GET"])
def get_stats():
    """
    Get global game statistics.

    Aggregates stats across all games played on this server.

    Returns JSON:
        total_games: Total games created
        active_games: Currently active games
        aggregate_stats: Combined player statistics
    """
    aggregate = {
        "total_games_created": len(games),
        "active_games": sum(
            1 for g in games.values() if g.is_playing()
        ),
        "completed_games": sum(
            1 for g in games.values() if g.is_game_over()
        ),
    }

    # Aggregate stats from all game instances
    total_wins = sum(g.stats.total_wins for g in games.values())
    total_losses = sum(g.stats.total_losses for g in games.values())
    best_streak = max(
        (g.stats.best_streak for g in games.values()), default=0
    )

    aggregate["total_wins"] = total_wins
    aggregate["total_losses"] = total_losses
    aggregate["best_streak"] = best_streak

    return jsonify(aggregate)


# ═══════════════════════════════════════════════════════════
# STARTUP
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  BOMB SWEEP — Python Flask Server")
    print("=" * 50)
    print(f"  Grid:    {GRID_SIZE}x{GRID_SIZE}")
    print(f"  Bombs:   {NUM_BOMBS}")
    print(f"  Lives:   {MAX_LIVES}")
    print(f"  URL:     http://127.0.0.1:5001")
    print("=" * 50 + "\n")
    app.run(debug=True, host="0.0.0.0", port=5001)

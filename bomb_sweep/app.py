"""
Bomb Sweep — Python Flask Backend
All game logic (bomb placement, reveal, win/loss detection) runs server-side.
Frontend communicates via REST API endpoints.

Run:  python app.py
Open: http://127.0.0.1:5000
"""

from flask import Flask, render_template, jsonify, request
import random
import uuid
import time

app = Flask(__name__)

# ──────────────────────────────────────────────
# In-memory game storage
# ──────────────────────────────────────────────
games = {}

stats = {
    "games_played": 0,
    "best_streak": 0,
    "current_streak": 0,
    "total_wins": 0,
    "total_losses": 0,
}

GRID_SIZE = 8
TOTAL_CELLS = GRID_SIZE * GRID_SIZE  # 64
NUM_BOMBS = 1


def calculate_adjacent(bomb_indices, cell_index, grid_size=8):
    """Count how many bombs are adjacent to a given cell."""
    cell_row, cell_col = divmod(cell_index, grid_size)
    count = 0
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr, nc = cell_row + dr, cell_col + dc
            if 0 <= nr < grid_size and 0 <= nc < grid_size:
                neighbor_idx = nr * grid_size + nc
                if neighbor_idx in bomb_indices:
                    count += 1
    return count


def get_all_adjacent(bomb_indices, grid_size=8):
    """Pre-calculate adjacent counts for every cell."""
    adjacent_map = {}
    for i in range(grid_size * grid_size):
        adjacent_map[i] = calculate_adjacent(bomb_indices, i, grid_size)
    return adjacent_map


# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the game page."""
    return render_template("index.html")


@app.route("/api/new-game", methods=["POST"])
def new_game():
    """Start a new game — server picks a random bomb position."""
    game_id = str(uuid.uuid4())
    bomb_index = random.randint(0, TOTAL_CELLS - 1)

    games[game_id] = {
        "id": game_id,
        "bomb_index": bomb_index,
        "bomb_indices": {bomb_index},
        "revealed": set(),
        "flagged": set(),
        "status": "playing",       # playing | won | lost
        "created_at": time.time(),
        "adjacent_map": get_all_adjacent({bomb_index}, GRID_SIZE),
    }

    stats["games_played"] += 1

    print(f"[NEW GAME] id={game_id}  bomb={bomb_index}")

    return jsonify({
        "game_id": game_id,
        "grid_size": GRID_SIZE,
        "total_cells": TOTAL_CELLS,
        "num_bombs": NUM_BOMBS,
    })


@app.route("/api/reveal", methods=["POST"])
def reveal():
    """Reveal a cell — returns safe/boom + adjacent count."""
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

    if game["status"] != "playing":
        return jsonify({"error": "Game already ended", "status": game["status"]}), 400

    try:
        cell_index = int(cell_index)
    except (ValueError, TypeError):
        return jsonify({"error": "cell_index must be an integer"}), 400

    if cell_index < 0 or cell_index >= TOTAL_CELLS:
        return jsonify({"error": f"cell_index must be 0-{TOTAL_CELLS - 1}"}), 400

    if cell_index in game["revealed"]:
        return jsonify({"error": "Cell already revealed"}), 400

    # ── Check for bomb ──
    if cell_index in game["bomb_indices"]:
        game["status"] = "lost"
        game["revealed"].add(cell_index)
        stats["total_losses"] += 1
        stats["current_streak"] = 0

        print(f"[BOOM] id={game_id}  cell={cell_index}")

        return jsonify({
            "safe": False,
            "status": "lost",
            "bomb_index": cell_index,
            "revealed_count": len(game["revealed"]),
            "total_safe": TOTAL_CELLS - NUM_BOMBS,
        })

    # ── Safe cell ──
    game["revealed"].add(cell_index)
    adjacent = game["adjacent_map"][cell_index]
    revealed_count = len(game["revealed"])
    total_safe = TOTAL_CELLS - NUM_BOMBS

    # ── Check for win ──
    if revealed_count >= total_safe:
        game["status"] = "won"
        stats["total_wins"] += 1
        stats["current_streak"] += 1
        if stats["current_streak"] > stats["best_streak"]:
            stats["best_streak"] = stats["current_streak"]

        print(f"[WIN] id={game_id}  streak={stats['current_streak']}")

        return jsonify({
            "safe": True,
            "status": "won",
            "adjacent": adjacent,
            "revealed_count": revealed_count,
            "total_safe": total_safe,
        })

    return jsonify({
        "safe": True,
        "status": "playing",
        "adjacent": adjacent,
        "revealed_count": revealed_count,
        "total_safe": total_safe,
    })


@app.route("/api/reveal-all", methods=["POST"])
def reveal_all():
    """Reveal the full board after game over."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    game_id = data.get("game_id")
    if game_id not in games:
        return jsonify({"error": "Game not found"}), 404

    game = games[game_id]
    cell_map = {}
    for i in range(TOTAL_CELLS):
        is_bomb = i in game["bomb_indices"]
        cell_map[i] = {
            "is_bomb": is_bomb,
            "adjacent": game["adjacent_map"][i],
            "revealed": i in game["revealed"],
        }

    return jsonify({
        "game_id": game_id,
        "status": game["status"],
        "cell_map": cell_map,
        "bomb_indices": list(game["bomb_indices"]),
    })


@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Return global game statistics."""
    return jsonify(stats)


# ──────────────────────────────────────────────
# Cleanup old games (run periodically)
# ──────────────────────────────────────────────
@app.before_request
def cleanup_old_games():
    """Remove games older than 30 minutes to prevent memory leak."""
    now = time.time()
    expired = [gid for gid, g in games.items() if now - g["created_at"] > 1800]
    for gid in expired:
        del games[gid]


if __name__ == "__main__":
    print("\n💣  Bomb Sweep Server Starting...")
    print("   Open http://127.0.0.1:5000 in your browser\n")
    app.run(debug=True, host="0.0.0.0", port=5000)

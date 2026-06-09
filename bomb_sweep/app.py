"""
Bomb Sweep — Flask Server Entry Point
======================================
Serves the Python-powered game page.
All game logic is in Python files:
  - game/engine.py: Core game engine (BombSweepGame)
  - pyscript_app.py: PyScript UI controller
  - server.py: This Flask server with API routes

Run:  python3 app.py
Open: http://127.0.0.1:5001
"""

from server import app

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  BOMB SWEEP — Python Flask Server")
    print("  All game logic is in Python!")
    print("  - game/engine.py: Core engine")
    print("  - pyscript_app.py: Browser UI")
    print("  - server.py: API routes")
    print("=" * 50)
    print("  Open: http://127.0.0.1:5001")
    print("=" * 50 + "\n")
    app.run(debug=True, host="0.0.0.0", port=5001)

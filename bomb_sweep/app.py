"""
Bomb Sweep — Python-Powered Edition
Uses PyScript to run all game logic in Python inside the browser.

Run:  python3 app.py
Open: http://127.0.0.1:5001

Note: The game also works as a standalone HTML file — just open
pyscript_index.html in any browser. No server needed!
"""

from flask import Flask, send_file

app = Flask(__name__)


@app.route("/")
def index():
    """Serve the PyScript-powered game page."""
    return send_file("pyscript_index.html")


if __name__ == "__main__":
    print("\n💣  Bomb Sweep — Python Edition Starting...")
    print("   PyScript runs Python in the browser — no API needed!")
    print("   Open http://127.0.0.1:5001\n")
    app.run(debug=True, host="0.0.0.0", port=5001)

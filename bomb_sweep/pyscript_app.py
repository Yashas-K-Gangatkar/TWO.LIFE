"""
Bomb Sweep — PyScript UI Controller
=====================================
This Python file runs inside the browser via PyScript.
It handles all UI interactions and uses the Python game engine.

Every click, animation, and DOM update is controlled by Python.
The HTML file is just a minimal shell — Python does the rest.

This module:
- Creates and manages the game grid (DOM elements)
- Handles cell click events
- Updates lives, progress, stats displays
- Controls shuffle animations
- Triggers visual effects via JS bridge
- Shows modals and toasts
"""

import random
import asyncio
from game.engine import (
    BombSweepGame, GRID_SIZE, TOTAL_CELLS,
    NUM_BOMBS, TOTAL_SAFE, MAX_LIVES
)

try:
    from pyscript import document, window
    from pyodide.ffi import create_proxy
    PYScript_AVAILABLE = True
except ImportError:
    PYScript_AVAILABLE = False
    document = None
    window = None
    create_proxy = None


# ═══════════════════════════════════════════════════════════
# GAME INSTANCE
# ═══════════════════════════════════════════════════════════

game = BombSweepGame()
game_starting = False


# ═══════════════════════════════════════════════════════════
# DOM HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════

def el(element_id):
    """Get a DOM element by ID — Python shortcut."""
    return document.getElementById(element_id)


def update_lives_ui(new_lives, animate_idx):
    """
    Update the heart display for lives.

    Python controls which hearts are alive, dead, or breaking.
    The breaking animation is a CSS class that Python applies
    and then removes after the animation completes.

    Args:
        new_lives (int): Current number of lives
        animate_idx (int): Index of the heart that should break
    """
    for i in range(MAX_LIVES):
        heart = el(f"heart-{i}")
        if i < new_lives:
            heart.className = "heart alive"
        elif i == animate_idx:
            heart.className = "heart breaking"
            def set_dead(heart_el=heart):
                heart_el.className = "heart dead"
            window.setTimeout(create_proxy(set_dead), 700)
        else:
            heart.className = "heart dead"


def reset_lives_ui():
    """Reset both hearts to alive state — Python."""
    for i in range(MAX_LIVES):
        el(f"heart-{i}").className = "heart alive"


def update_progress():
    """
    Update the progress bar and counter.

    Python calculates the progress from game state and
    updates the DOM elements directly.
    """
    progress = game.get_progress()
    pct = min(100, progress["percentage"])
    el("progress-fill").style.width = f"{pct}%"
    el("progress-text").textContent = (
        f"{progress['revealed_count']} / {progress['total_safe']}"
    )


def update_stats():
    """Update the statistics display — Python."""
    el("best-streak").textContent = str(game.stats.best_streak)
    el("current-streak").textContent = str(game.stats.current_streak)


def get_num_css_class(adjacent_count):
    """
    Get CSS class name for adjacent number display.

    Each adjacent count (1-4+) gets a unique color:
    - 1: Blue (#5bc0de)
    - 2: Green (#5cb85c)
    - 3: Orange (#f0ad4e)
    - 4+: Red (#e94560)

    Args:
        adjacent_count (int): Number of adjacent bombs

    Returns:
        str: CSS class name
    """
    return f"num-{min(adjacent_count, 4)}"


def disable_grid():
    """Disable all cells so they can't be clicked — Python."""
    cells = document.querySelectorAll(".cell")
    for i in range(cells.length):
        cells.item(i).classList.add("disabled")


def show_toast(message, toast_type=""):
    """
    Show a toast notification.

    Python creates the DOM element, sets the class and text,
    and schedules automatic removal after 3 seconds.

    Args:
        message (str): Toast message text
        toast_type (str): CSS type class (error, success, warning)
    """
    container = el("toast-container")
    toast = document.createElement("div")
    toast.className = f"toast {toast_type}"
    toast.textContent = message
    container.appendChild(toast)

    def remove_toast(toast_el=toast):
        if toast_el.parentNode:
            toast_el.remove()
    window.setTimeout(create_proxy(remove_toast), 3200)


def show_modal(modal_type, title, text):
    """
    Show the game over or win modal.

    Python sets up the modal content including:
    - Emoji (chocolate star for win, explosion for loss)
    - Title text
    - Lives summary with grayed-out lost hearts
    - Description text

    Args:
        modal_type (str): "win" or "lose"
        title (str): Modal title
        text (str): Modal description
    """
    overlay = el("modal-overlay")
    modal = el("modal")
    modal.className = f"modal {modal_type}"

    # Build lives summary
    lives_div = el("modal-lives")
    lives_div.innerHTML = ""
    for i in range(MAX_LIVES):
        span = document.createElement("span")
        span.textContent = "\u2764\ufe0f"  # ❤️
        if i >= game.lives:
            span.style.opacity = "0.3"
            span.style.filter = "grayscale(1)"
        lives_div.appendChild(span)

    # Set content based on type
    if modal_type == "win":
        el("modal-emoji").textContent = "\U0001f36b\u2b50"  # 🍫⭐
    else:
        el("modal-emoji").textContent = "\U0001f4a5"  # 💥

    el("modal-title").textContent = title
    el("modal-text").textContent = text
    overlay.classList.add("active")


def close_modal():
    """Close the modal overlay — Python."""
    el("modal-overlay").classList.remove("active")


# ═══════════════════════════════════════════════════════════
# GRID BUILDER — Python creates all 64 DOM elements
# ═══════════════════════════════════════════════════════════

def build_grid():
    """
    Build the 8x8 game grid.

    Python creates each cell as a DOM div element,
    sets up accessibility attributes, and attaches
    click event listeners using PyScript proxies.

    Each cell gets:
    - Unique ID: cell-0 through cell-63
    - Click handler that calls on_cell_click()
    - ARIA label for screen readers
    - Keyboard navigation support (tabindex)
    """
    grid = el("grid")
    grid.innerHTML = ""

    for i in range(TOTAL_CELLS):
        cell = document.createElement("div")
        cell.className = "cell"
        cell.id = f"cell-{i}"
        cell.setAttribute("tabindex", "0")
        cell.setAttribute("role", "button")

        row = i // GRID_SIZE + 1
        col = i % GRID_SIZE + 1
        cell.setAttribute("aria-label", f"Cell {row}, {col}")

        # Create click handler using closure
        def make_handler(cell_idx):
            def handler(event=None):
                on_cell_click(cell_idx)
            return handler

        cell.addEventListener("click", create_proxy(make_handler(i)))
        grid.appendChild(cell)


# ═══════════════════════════════════════════════════════════
# CELL CLICK HANDLER — Pure Python game logic
# ═══════════════════════════════════════════════════════════

def on_cell_click(cell_index):
    """
    Handle a cell click — all game logic in Python.

    This is the main interaction handler. When a player
    clicks a cell, this method:

    1. Validates the click (game in progress, cell not revealed)
    2. Calls the Python game engine (game.reveal_cell)
    3. Updates the DOM based on the result:
       - Bomb hit: show bomb emoji, flash screen, particles
       - Safe cell: show adjacent count, green particles
    4. Checks for win/loss and shows appropriate modal

    Args:
        cell_index (int): The clicked cell index (0-63)
    """
    global game_starting

    # Guard checks — Python
    if game.status != "playing" or game_starting:
        return
    if cell_index in game.revealed:
        return

    cell = el(f"cell-{cell_index}")
    if not cell:
        return

    # ═══ CALL PYTHON GAME ENGINE ═══
    result = game.reveal_cell(cell_index)

    if result.error:
        show_toast(result.error, "error")
        return

    if not result.safe:
        # ── BOMB HIT ──
        handle_bomb_hit(cell, cell_index, result)
    else:
        # ── SAFE CELL ──
        handle_safe_cell(cell, cell_index, result)


def handle_bomb_hit(cell, cell_index, result):
    """
    Handle a bomb hit — Python processes and updates UI.

    Args:
        cell: DOM element of the clicked cell
        cell_index (int): Cell index
        result: RevealResult from the game engine
    """
    cell.classList.add("revealed", "bomb-hit")
    cell.innerHTML = "\U0001f4a3"  # 💣

    # Trigger visual effects via JS bridge
    window.jsBurstAt(
        f"cell-{cell_index}",
        ["#e94560", "#ff6b6b", "#ff4444", "#ff8800"],
        40
    )
    window.jsScreenFlash()

    # Update bombs remaining counter
    bombs_remaining = game.get_bombs_remaining()
    el("bombs-left").textContent = str(bombs_remaining)

    if result.status == "lost":
        # ── GAME OVER ──
        old_lives = game.lives + 1
        update_lives_ui(0, old_lives - 1)
        update_progress()
        disable_grid()
        el("btn-reveal").style.display = ""

        def show_lose():
            show_modal(
                "lose", "Game Over!",
                "You ran out of lives. Better luck next time!"
            )
        window.setTimeout(create_proxy(show_lose), 700)

    else:
        # ── Lost a life, still playing ──
        old_lives = game.lives + 1
        update_lives_ui(result.lives, old_lives - 1)
        update_progress()
        lives_word = "life" if result.lives == 1 else "lives"
        show_toast(
            f"Life lost! {result.lives} {lives_word} remaining",
            "warning"
        )


def handle_safe_cell(cell, cell_index, result):
    """
    Handle a safe cell reveal — Python processes and updates UI.

    Args:
        cell: DOM element of the clicked cell
        cell_index (int): Cell index
        result: RevealResult from the game engine
    """
    cell.classList.add("revealed")
    adj = result.adjacent

    if adj > 0:
        css_class = get_num_css_class(adj)
        cell.innerHTML = f'<span class="num {css_class}">{adj}</span>'
    else:
        cell.innerHTML = '<span class="num num-0">\u00b7</span>'

    # Safe particle burst
    window.jsBurstAt(
        f"cell-{cell_index}",
        ["#4ade80", "#0f9b58", "#5bc0de"],
        12
    )
    update_progress()

    if result.status == "won":
        # ── WIN! ──
        disable_grid()
        update_stats()
        window.jsCelebrationBurst()

        lives_word = "life" if game.lives == 1 else "lives"
        msg = (
            f"You swept all bombs with {game.lives} "
            f"{lives_word} left! Here's your 5-Star Chocolate!"
        )

        def show_win():
            show_modal("win", "You Win!", msg)
        window.setTimeout(create_proxy(show_win), 800)


# ═══════════════════════════════════════════════════════════
# REVEAL ALL — Python
# ═══════════════════════════════════════════════════════════

def reveal_all():
    """
    Reveal the full board after game over.

    Python reads the board state from the game engine
    and updates every cell's DOM element to show
    bomb positions and adjacent counts.
    """
    board = game.reveal_all()

    # Show all bombs
    for bomb_idx in board["bomb_indices"]:
        cell = el(f"cell-{bomb_idx}")
        if cell:
            class_list = cell.classList.toString()
            if "bomb-hit" not in class_list:
                cell.classList.add("revealed", "bomb-reveal")
                cell.innerHTML = "\U0001f4a3"

    # Show all remaining safe cells
    for i in range(TOTAL_CELLS):
        cell = el(f"cell-{i}")
        if not cell:
            continue
        class_list = cell.classList.toString()
        if "revealed" not in class_list:
            cell.classList.add("revealed", "safe-reveal-end")
            adj = board["cells"][i]["adjacent"]
            if adj > 0:
                css_class = get_num_css_class(adj)
                cell.innerHTML = f'<span class="num {css_class}">{adj}</span>'
            else:
                cell.innerHTML = '<span class="num num-0">\u00b7</span>'

    disable_grid()
    el("btn-reveal").style.display = "none"


# ═══════════════════════════════════════════════════════════
# SHUFFLE ANIMATION — Python orchestrates timing
# ═══════════════════════════════════════════════════════════

async def shuffle_animation():
    """
    3-phase shuffle animation orchestrated by Python.

    Phase 1: Wave Flip
    - Each cell flips in a wave pattern (diagonal sweep)
    - Repeated 3 times for dramatic effect
    - Python calculates the delay for each cell based on
      its row and column position

    Phase 2: Random Sparkle
    - 20 random cells light up with gradient highlights
    - Python's random.randint picks the cells
    - Staggered timing creates a twinkling effect

    Phase 3: Settle Wave
    - All cells briefly shrink and bounce back
    - Same diagonal wave pattern as Phase 1
    - Signals the grid is ready for play
    """
    global game_starting
    game_starting = True

    cells = document.querySelectorAll(".cell")
    total = cells.length

    # ── Phase 1: Wave Flip (3 rounds) ──
    for round_num in range(3):
        for i in range(total):
            row = i // GRID_SIZE
            col = i % GRID_SIZE
            delay = (row + col) * 30 + round_num * 200

            def make_flip(idx):
                def do_flip():
                    cells.item(idx).classList.add("shuffling")
                    def remove_shuffling():
                        cells.item(idx).classList.remove("shuffling")
                    window.setTimeout(
                        create_proxy(remove_shuffling), 150
                    )
                return do_flip

            window.setTimeout(create_proxy(make_flip(i)), delay)
        await asyncio.sleep(0.55)

    # ── Phase 2: Random Sparkle (20 highlights) ──
    for j in range(20):
        idx = random.randint(0, total - 1)

        def make_sparkle(idx2):
            def do_sparkle():
                cells.item(idx2).classList.add("shuffle-highlight")
                def remove_highlight():
                    cells.item(idx2).classList.remove(
                        "shuffle-highlight"
                    )
                window.setTimeout(
                    create_proxy(remove_highlight), 300
                )
            return do_sparkle

        window.setTimeout(create_proxy(make_sparkle(idx)), j * 60)

    await asyncio.sleep(1.5)

    # ── Phase 3: Settle Wave ──
    for i in range(total):
        row = i // GRID_SIZE
        col = i % GRID_SIZE
        delay = (row + col) * 25

        def make_settle(idx):
            def do_settle():
                cells.item(idx).style.transform = "scale(0.9)"
                def undo_settle():
                    cells.item(idx).style.transform = ""
                window.setTimeout(create_proxy(undo_settle), 100)
            return do_settle

        window.setTimeout(create_proxy(make_settle(i)), delay)

    await asyncio.sleep(0.5)
    game_starting = False


# ═══════════════════════════════════════════════════════════
# NEW GAME — Python master controller
# ═══════════════════════════════════════════════════════════

async def start_new_game():
    """
    Start a new game — Python orchestrates the entire flow.

    1. Closes any open modal
    2. Creates a new game via Python engine
    3. Resets all UI elements (lives, progress, stats)
    4. Builds the grid (Python creates DOM elements)
    5. Runs shuffle animation (Python controls timing)
    """
    close_modal()

    # Python game engine creates new game
    game.new_game()

    # Reset UI — Python updates DOM
    el("btn-reveal").style.display = "none"
    el("bombs-left").textContent = str(NUM_BOMBS)
    reset_lives_ui()
    update_progress()
    update_stats()
    build_grid()

    # Python-controlled animation
    await shuffle_animation()
    print("[PYTHON] Game ready!")


# ═══════════════════════════════════════════════════════════
# EVENT BINDING — Python attaches all listeners
# ═══════════════════════════════════════════════════════════

def on_new_game_click(event=None):
    """New Game button handler — starts async game creation."""
    asyncio.ensure_future(start_new_game())


def on_reveal_click(event=None):
    """Reveal Board button handler — shows full board."""
    reveal_all()


def on_play_again_click(event=None):
    """Play Again button in modal — starts new game."""
    asyncio.ensure_future(start_new_game())


def on_overlay_click(event=None):
    """Close modal when clicking outside of it."""
    target = event.target if event else None
    if target and target == el("modal-overlay"):
        close_modal()


def bind_events():
    """
    Bind all event listeners — Python style.

    Attaches click handlers to:
    - New Game button
    - Reveal Board button
    - Play Again button (in modal)
    - Modal overlay (click to close)
    """
    el("btn-new").addEventListener(
        "click", create_proxy(on_new_game_click)
    )
    el("btn-reveal").addEventListener(
        "click", create_proxy(on_reveal_click)
    )
    el("btn-play-again").addEventListener(
        "click", create_proxy(on_play_again_click)
    )
    el("modal-overlay").addEventListener(
        "click", create_proxy(on_overlay_click)
    )


# ═══════════════════════════════════════════════════════════
# INITIALIZATION
# ═══════════════════════════════════════════════════════════

def hide_loading_screen():
    """Hide the Python loading overlay."""
    overlay = el("loading-overlay")
    if overlay:
        overlay.classList.add("hidden")

        def remove_overlay():
            o = el("loading-overlay")
            if o and o.parentNode:
                o.remove()
        window.setTimeout(create_proxy(remove_overlay), 600)


def load_saved_stats():
    """Load saved best streak from localStorage."""
    try:
        val = window.localStorage.getItem("bombSweep_best")
        if val:
            game.stats.best_streak = int(val)
    except Exception:
        pass


def save_stats():
    """Save best streak to localStorage."""
    try:
        window.localStorage.setItem(
            "bombSweep_best", str(game.stats.best_streak)
        )
    except Exception:
        pass


def init():
    """
    Main initialization — Python boots the entire game.

    1. Hides the loading screen
    2. Loads saved statistics
    3. Binds all event listeners
    4. Starts the first game
    """
    hide_loading_screen()
    load_saved_stats()
    bind_events()

    # Start first game
    asyncio.ensure_future(start_new_game())

    print("[PYTHON] Bomb Sweep loaded! "
          "All game logic running in Python!")
    print(f"[PYTHON] Grid: {GRID_SIZE}x{GRID_SIZE} | "
          f"Bombs: {NUM_BOMBS} | Lives: {MAX_LIVES}")


# ═══════════════════════════════════════════════════════════
# RUN ON PYScript LOAD
# ═══════════════════════════════════════════════════════════

init()

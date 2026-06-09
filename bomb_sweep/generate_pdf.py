"""Bomb Sweep — Technical Documentation PDF Generator"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

# ── Font Registration ──
pdfmetrics.registerFont(TTFont('Carlito', '/usr/share/fonts/truetype/english/Carlito-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Carlito-Bold', '/usr/share/fonts/truetype/english/Carlito-Bold.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'))
registerFontFamily('Carlito', normal='Carlito', bold='Carlito-Bold')
registerFontFamily('DejaVuSans', normal='DejaVuSans', bold='DejaVuSans-Bold')

# ── Palette ──
ACCENT       = colors.HexColor('#d1582f')
TEXT_PRIMARY  = colors.HexColor('#212224')
TEXT_MUTED    = colors.HexColor('#81878d')
BG_SURFACE   = colors.HexColor('#e2e4e8')
BG_PAGE      = colors.HexColor('#f1f2f4')

TABLE_HEADER_COLOR = ACCENT
TABLE_HEADER_TEXT  = colors.white
TABLE_ROW_EVEN     = colors.white
TABLE_ROW_ODD      = BG_SURFACE

# ── Styles ──
title_style = ParagraphStyle(name='Title', fontName='Carlito', fontSize=28, leading=34, textColor=ACCENT, alignment=TA_CENTER, spaceAfter=6)
subtitle_style = ParagraphStyle(name='Subtitle', fontName='Carlito', fontSize=14, leading=20, textColor=TEXT_MUTED, alignment=TA_CENTER, spaceAfter=20)
h1_style = ParagraphStyle(name='H1', fontName='Carlito', fontSize=20, leading=26, textColor=ACCENT, spaceBefore=18, spaceAfter=10)
h2_style = ParagraphStyle(name='H2', fontName='Carlito', fontSize=15, leading=20, textColor=TEXT_PRIMARY, spaceBefore=14, spaceAfter=8)
h3_style = ParagraphStyle(name='H3', fontName='Carlito', fontSize=12, leading=16, textColor=TEXT_PRIMARY, spaceBefore=10, spaceAfter=6)
body_style = ParagraphStyle(name='Body', fontName='Carlito', fontSize=10.5, leading=17, textColor=TEXT_PRIMARY, alignment=TA_JUSTIFY, spaceAfter=8)
code_style = ParagraphStyle(name='Code', fontName='DejaVuSans', fontSize=8.5, leading=12, textColor=colors.HexColor('#1a1a2e'), backColor=colors.HexColor('#f4f4f8'), leftIndent=12, rightIndent=12, spaceBefore=4, spaceAfter=4, borderPadding=6)
caption_style = ParagraphStyle(name='Caption', fontName='Carlito', fontSize=9, leading=13, textColor=TEXT_MUTED, alignment=TA_CENTER, spaceAfter=12)
header_cell_style = ParagraphStyle(name='HeaderCell', fontName='Carlito', fontSize=10, leading=14, textColor=TABLE_HEADER_TEXT, alignment=TA_CENTER)
cell_style = ParagraphStyle(name='Cell', fontName='Carlito', fontSize=10, leading=14, textColor=TEXT_PRIMARY, alignment=TA_LEFT)
cell_center_style = ParagraphStyle(name='CellCenter', fontName='Carlito', fontSize=10, leading=14, textColor=TEXT_PRIMARY, alignment=TA_CENTER)

# ── Document ──
output_path = '/home/z/my-project/download/Bomb_Sweep_Technical_Documentation.pdf'
doc = SimpleDocTemplate(output_path, pagesize=A4, leftMargin=1*inch, rightMargin=1*inch, topMargin=1*inch, bottomMargin=1*inch)
story = []
available_width = A4[0] - 2 * inch

# ═══════════════════════════════════════════════════════════
# COVER PAGE
# ═══════════════════════════════════════════════════════════
story.append(Spacer(1, 120))
story.append(Paragraph('<b>BOMB SWEEP</b>', title_style))
story.append(Spacer(1, 8))
story.append(Paragraph('Python-Powered Game', subtitle_style))
story.append(Spacer(1, 20))

cover_line_style = TableStyle([
    ('LINEBELOW', (0, 0), (-1, 0), 2, ACCENT),
])
cover_line = Table([['']], colWidths=[available_width * 0.4], hAlign='CENTER')
cover_line.setStyle(cover_line_style)
story.append(cover_line)
story.append(Spacer(1, 30))

story.append(Paragraph('Technical Documentation', ParagraphStyle(name='CoverSub2', fontName='Carlito', fontSize=16, leading=22, textColor=TEXT_PRIMARY, alignment=TA_CENTER)))
story.append(Spacer(1, 8))
story.append(Paragraph('How the Python Game Engine Works', ParagraphStyle(name='CoverSub3', fontName='Carlito', fontSize=12, leading=18, textColor=TEXT_MUTED, alignment=TA_CENTER)))
story.append(Spacer(1, 60))

meta_style = ParagraphStyle(name='Meta', fontName='Carlito', fontSize=10, leading=16, textColor=TEXT_MUTED, alignment=TA_CENTER)
story.append(Paragraph('8x8 Grid | 3 Bombs | 2 Lives | 5-Star Chocolate Prize', meta_style))
story.append(Spacer(1, 8))
story.append(Paragraph('Built with Python, Flask, and PyScript', meta_style))
story.append(Spacer(1, 8))
story.append(Paragraph('Author: Yashas K Gangatkar', meta_style))
story.append(Spacer(1, 8))
story.append(Paragraph('Repository: github.com/Yashas-K-Gangatkar/TWO.LIFE', meta_style))

story.append(PageBreak())

# ═══════════════════════════════════════════════════════════
# SECTION 1: PROJECT OVERVIEW
# ═══════════════════════════════════════════════════════════
story.append(Paragraph('<b>1. Project Overview</b>', h1_style))
story.append(Paragraph(
    'Bomb Sweep is a browser-based grid game where players must reveal all safe cells on an 8x8 board '
    'while avoiding 3 hidden bombs. The player starts with 2 lives - if they click a bomb, they lose one life. '
    'If they lose all lives, the game is over. If they successfully reveal all 61 safe cells without losing '
    'both lives, they win a 5-Star Chocolate! The entire game logic is written in Python, making up over 80% '
    'of the codebase. Python runs both on the server side (Flask) and directly in the browser (PyScript), '
    'ensuring that bomb placement, adjacent calculation, reveal logic, life deduction, and win/loss detection '
    'are all handled by Python code.',
    body_style
))

story.append(Paragraph('<b>1.1 Game Rules</b>', h2_style))
rules_data = [
    [Paragraph('<b>Rule</b>', header_cell_style), Paragraph('<b>Details</b>', header_cell_style)],
    [Paragraph('Grid Size', cell_style), Paragraph('8 x 8 = 64 cells', cell_style)],
    [Paragraph('Bombs', cell_style), Paragraph('3 bombs hidden randomly using Python random.sample()', cell_style)],
    [Paragraph('Lives', cell_style), Paragraph('2 lives - first bomb hit costs 1 life, second hit = Game Over', cell_style)],
    [Paragraph('Safe Cells', cell_style), Paragraph('61 safe cells (64 total - 3 bombs)', cell_style)],
    [Paragraph('Adjacent Numbers', cell_style), Paragraph('Each safe cell shows how many of its 8 neighbors are bombs', cell_style)],
    [Paragraph('Win Condition', cell_style), Paragraph('Reveal all 61 safe cells = 5-Star Chocolate!', cell_style)],
    [Paragraph('Lose Condition', cell_style), Paragraph('Hit 2 bombs (lose both lives) = Better Luck Next Time', cell_style)],
]
rules_table = Table(rules_data, colWidths=[available_width*0.25, available_width*0.75], hAlign='CENTER')
rules_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), TABLE_HEADER_COLOR),
    ('TEXTCOLOR', (0, 0), (-1, 0), TABLE_HEADER_TEXT),
    ('BACKGROUND', (0, 1), (-1, 1), TABLE_ROW_EVEN),
    ('BACKGROUND', (0, 2), (-1, 2), TABLE_ROW_ODD),
    ('BACKGROUND', (0, 3), (-1, 3), TABLE_ROW_EVEN),
    ('BACKGROUND', (0, 4), (-1, 4), TABLE_ROW_ODD),
    ('BACKGROUND', (0, 5), (-1, 5), TABLE_ROW_EVEN),
    ('BACKGROUND', (0, 6), (-1, 6), TABLE_ROW_ODD),
    ('BACKGROUND', (0, 7), (-1, 7), TABLE_ROW_EVEN),
    ('GRID', (0, 0), (-1, -1), 0.5, TEXT_MUTED),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ('TOPPADDING', (0, 0), (-1, -1), 6),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
]))
story.append(Spacer(1, 12))
story.append(rules_table)
story.append(Paragraph('Table 1: Game Rules Summary', caption_style))

story.append(Paragraph('<b>1.2 Technology Stack</b>', h2_style))
tech_data = [
    [Paragraph('<b>Component</b>', header_cell_style), Paragraph('<b>Technology</b>', header_cell_style), Paragraph('<b>Purpose</b>', header_cell_style)],
    [Paragraph('Game Engine', cell_style), Paragraph('Python 3', cell_center_style), Paragraph('Bomb placement, adjacent calc, reveal logic', cell_style)],
    [Paragraph('Browser Runtime', cell_style), Paragraph('PyScript', cell_center_style), Paragraph('Runs Python in browser via WebAssembly', cell_style)],
    [Paragraph('Server', cell_style), Paragraph('Flask', cell_center_style), Paragraph('REST API for server-mode gameplay', cell_style)],
    [Paragraph('Android', cell_style), Paragraph('Kotlin + WebView', cell_center_style), Paragraph('Native Android wrapper for the HTML game', cell_style)],
    [Paragraph('Frontend Shell', cell_style), Paragraph('HTML + CSS', cell_center_style), Paragraph('Minimal structure, no game logic', cell_style)],
]
tech_table = Table(tech_data, colWidths=[available_width*0.22, available_width*0.22, available_width*0.56], hAlign='CENTER')
tech_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), TABLE_HEADER_COLOR),
    ('TEXTCOLOR', (0, 0), (-1, 0), TABLE_HEADER_TEXT),
    ('BACKGROUND', (0, 1), (-1, 1), TABLE_ROW_EVEN),
    ('BACKGROUND', (0, 2), (-1, 2), TABLE_ROW_ODD),
    ('BACKGROUND', (0, 3), (-1, 3), TABLE_ROW_EVEN),
    ('BACKGROUND', (0, 4), (-1, 4), TABLE_ROW_ODD),
    ('BACKGROUND', (0, 5), (-1, 5), TABLE_ROW_EVEN),
    ('GRID', (0, 0), (-1, -1), 0.5, TEXT_MUTED),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ('TOPPADDING', (0, 0), (-1, -1), 6),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
]))
story.append(Spacer(1, 12))
story.append(tech_table)
story.append(Paragraph('Table 2: Technology Stack', caption_style))

# ═══════════════════════════════════════════════════════════
# SECTION 2: GAME ENGINE (engine.py)
# ═══════════════════════════════════════════════════════════
story.append(Paragraph('<b>2. Game Engine (game/engine.py)</b>', h1_style))
story.append(Paragraph(
    'The core of Bomb Sweep is the BombSweepGame class in game/engine.py. This is a pure Python module '
    'with zero web dependencies. It handles all game logic: bomb placement using Python\'s random.sample(), '
    '8-directional adjacent bomb calculation, cell reveal with life deduction, and win/loss detection. '
    'The module also includes supporting classes: BombPlacer for random bomb placement, AdjacentCalculator '
    'for counting neighboring bombs, RevealResult as a structured return type, and GameStatistics for '
    'tracking player performance across multiple games.',
    body_style
))

story.append(Paragraph('<b>2.1 Bomb Placement (BombPlacer)</b>', h2_style))
story.append(Paragraph(
    'The BombPlacer class uses Python\'s built-in random.sample() function to uniformly distribute '
    'bombs across the grid. This ensures true randomness using Python\'s Mersenne Twister algorithm. '
    'The place() method selects 3 unique positions from the 64-cell grid, guaranteeing no duplicates. '
    'A variant method, place_with_safe_zone(), can exclude a specific cell to implement first-click safety, '
    'ensuring the player\'s first reveal is never a bomb.',
    body_style
))
story.append(Paragraph('<b>Code: BombPlacer.place()</b>', h3_style))
story.append(Paragraph(
    '@staticmethod<br/>'
    'def place(num_bombs=NUM_BOMBS, grid_size=GRID_SIZE):<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;total = grid_size * grid_size<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;if num_bombs &gt; total:<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise ValueError("Cannot place bombs")<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;indices = random.sample(range(total), num_bombs)<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;return set(indices)',
    code_style
))

story.append(Paragraph('<b>2.2 Adjacent Bomb Calculation (AdjacentCalculator)</b>', h2_style))
story.append(Paragraph(
    'The AdjacentCalculator performs 8-directional neighbor checking. For each cell, it converts the '
    'flat index to (row, col) coordinates using Python\'s divmod(), then checks all 8 surrounding '
    'positions. The calculate_all() method pre-computes counts for all 64 cells at game start, so '
    'reveals only need a dictionary lookup. This optimization eliminates redundant calculations during '
    'gameplay, making every cell reveal instant.',
    body_style
))
story.append(Paragraph('<b>Code: AdjacentCalculator.calculate_for_cell()</b>', h3_style))
story.append(Paragraph(
    '@staticmethod<br/>'
    'def calculate_for_cell(cell_index, bomb_indices, grid_size=GRID_SIZE):<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;row, col = divmod(cell_index, grid_size)<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;count = 0<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;for delta_row in (-1, 0, 1):<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;for delta_col in (-1, 0, 1):<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if delta_row == 0 and delta_col == 0:<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;continue<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;nr, nc = row + delta_row, col + delta_col<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if 0 &lt;= nr &lt; grid_size and 0 &lt;= nc &lt; grid_size:<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;neighbor_idx = nr * grid_size + nc<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if neighbor_idx in bomb_indices:<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;count += 1<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;return count',
    code_style
))

story.append(Paragraph('<b>2.3 Cell Reveal Logic (BombSweepGame.reveal_cell)</b>', h2_style))
story.append(Paragraph(
    'The reveal_cell() method is the core interaction handler. When a player clicks a cell, this method '
    'determines the outcome: if the cell contains a bomb, a life is deducted; if lives reach zero, the '
    'game status changes to "lost"; if all safe cells are revealed, the status becomes "won"; otherwise, '
    'the adjacent bomb count is returned for the UI to display. The method returns a RevealResult object '
    'that encapsulates all information needed by both the Flask API and the PyScript UI layer, including '
    'the safe/bomb status, current lives, game status, and adjacent count.',
    body_style
))
story.append(Paragraph('<b>Code: BombSweepGame.reveal_cell()</b>', h3_style))
story.append(Paragraph(
    'def reveal_cell(self, cell_index):<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;if self.status != "playing":<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return RevealResult(safe=False, status=self.status,<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;lives=self.lives, error="Game not in progress")<br/><br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;if cell_index in self.bomb_indices:  # BOMB HIT!<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.revealed.add(cell_index)<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.lives -= 1<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if self.lives &lt;= 0:  # GAME OVER<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.status = "lost"<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return RevealResult(safe=False, status="lost",<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;lives=0, bomb_index=cell_index)<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;else:  # Lost a life, still playing<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return RevealResult(safe=False, status="playing",<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;lives=self.lives, bomb_index=cell_index)<br/><br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;# SAFE CELL<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;self.revealed.add(cell_index)<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;adjacent = self.adjacent_map[cell_index]<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;if len(self.revealed) &gt;= self.total_safe:  # WIN!<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;self.status = "won"<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return RevealResult(safe=True, status="won",<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;lives=self.lives, adjacent=adjacent)<br/><br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;return RevealResult(safe=True, status="playing",<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;lives=self.lives, adjacent=adjacent)',
    code_style
))

story.append(Paragraph('<b>2.4 Statistics Tracking (GameStatistics)</b>', h2_style))
story.append(Paragraph(
    'The GameStatistics class tracks player performance across multiple games. It records wins, losses, '
    'current and best win streaks, and calculates derived metrics like win rate percentage and average '
    'cells revealed per game. Statistics persist via localStorage in the browser (PyScript) or in-memory '
    'on the server (Flask). The best streak is saved so players can track their all-time best performance '
    'even after closing the browser.',
    body_style
))

# ═══════════════════════════════════════════════════════════
# SECTION 3: PYSCRIPT UI CONTROLLER
# ═══════════════════════════════════════════════════════════
story.append(Paragraph('<b>3. PyScript UI Controller (pyscript_app.py)</b>', h1_style))
story.append(Paragraph(
    'The pyscript_app.py file is the bridge between the Python game engine and the browser DOM. It runs '
    'entirely in the browser via PyScript, which compiles Python to WebAssembly. This module handles all '
    'UI interactions: building the 8x8 grid by creating DOM elements, processing cell clicks, updating '
    'lives display with heart-break animations, controlling the 3-phase shuffle animation, showing modals '
    'and toasts, and triggering visual effects. Every user interaction flows through Python code before '
    'any DOM update occurs.',
    body_style
))

story.append(Paragraph('<b>3.1 Grid Construction</b>', h2_style))
story.append(Paragraph(
    'The build_grid() function creates all 64 DOM elements programmatically using Python. Each cell is a '
    'div element with a unique ID (cell-0 through cell-63), click event listener attached via PyScript\'s '
    'create_proxy(), and ARIA attributes for accessibility. The Python code creates closures for each '
    'click handler to capture the cell index, ensuring the correct cell is revealed on each click.',
    body_style
))
story.append(Paragraph('<b>Code: build_grid()</b>', h3_style))
story.append(Paragraph(
    'def build_grid():<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;grid = el("grid")<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;grid.innerHTML = ""<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;for i in range(TOTAL_CELLS):<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;cell = document.createElement("div")<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;cell.className = "cell"<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;cell.id = f"cell-{i}"<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;def make_handler(cell_idx):<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;def handler(event=None):<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;on_cell_click(cell_idx)<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return handler<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;cell.addEventListener("click",<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;create_proxy(make_handler(i)))<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;grid.appendChild(cell)',
    code_style
))

story.append(Paragraph('<b>3.2 Shuffle Animation</b>', h2_style))
story.append(Paragraph(
    'The shuffle_animation() function is an async Python coroutine that orchestrates a 3-phase visual '
    'sequence before gameplay begins. Phase 1 performs a wave flip where each cell rotates in a diagonal '
    'sweep pattern repeated 3 times. Phase 2 adds random sparkle highlights using Python\'s random.randint() '
    'to select 20 random cells. Phase 3 performs a settle wave where all cells briefly shrink and bounce '
    'back. Python controls all timing through asyncio.sleep() and window.setTimeout(), with animation '
    'classes applied and removed via DOM manipulation.',
    body_style
))

story.append(Paragraph('<b>3.3 Click Handler Flow</b>', h2_style))
story.append(Paragraph(
    'When a player clicks a cell, the on_cell_click() function processes the interaction entirely in '
    'Python. It first validates the click (game is in progress, cell not already revealed), then calls '
    'game.reveal_cell() from the Python engine. Based on the RevealResult, it updates the DOM: bomb hits '
    'show a bomb emoji with a shake animation and screen flash; safe cells display the adjacent count with '
    'a flip animation and green particle burst. If the game ends, Python triggers the appropriate modal '
    '(win with celebration particles, or lose with a "Better Luck Next Time" message).',
    body_style
))

# ═══════════════════════════════════════════════════════════
# SECTION 4: FLASK SERVER
# ═══════════════════════════════════════════════════════════
story.append(Paragraph('<b>4. Flask API Server (server.py)</b>', h1_style))
story.append(Paragraph(
    'The Flask server provides REST API endpoints for server-mode gameplay. It creates BombSweepGame '
    'instances in memory, keyed by UUID session identifiers, and exposes endpoints for creating new games, '
    'revealing cells, revealing the full board, and retrieving aggregate statistics. The server also handles '
    'automatic cleanup of expired game sessions (older than 30 minutes) to prevent memory leaks. All game '
    'logic is delegated to the Python game engine, keeping the server layer thin and focused on HTTP '
    'routing and JSON serialization.',
    body_style
))

api_data = [
    [Paragraph('<b>Endpoint</b>', header_cell_style), Paragraph('<b>Method</b>', header_cell_style), Paragraph('<b>Description</b>', header_cell_style)],
    [Paragraph('/api/new-game', cell_style), Paragraph('POST', cell_center_style), Paragraph('Creates a new BombSweepGame, places bombs, returns game_id', cell_style)],
    [Paragraph('/api/reveal', cell_style), Paragraph('POST', cell_center_style), Paragraph('Reveals a cell, calls game.reveal_cell(), returns RevealResult', cell_style)],
    [Paragraph('/api/reveal-all', cell_style), Paragraph('POST', cell_center_style), Paragraph('Returns full board data after game over', cell_style)],
    [Paragraph('/api/stats', cell_style), Paragraph('GET', cell_center_style), Paragraph('Returns aggregate statistics across all games', cell_style)],
]
api_table = Table(api_data, colWidths=[available_width*0.25, available_width*0.12, available_width*0.63], hAlign='CENTER')
api_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), TABLE_HEADER_COLOR),
    ('TEXTCOLOR', (0, 0), (-1, 0), TABLE_HEADER_TEXT),
    ('BACKGROUND', (0, 1), (-1, 1), TABLE_ROW_EVEN),
    ('BACKGROUND', (0, 2), (-1, 2), TABLE_ROW_ODD),
    ('BACKGROUND', (0, 3), (-1, 3), TABLE_ROW_EVEN),
    ('BACKGROUND', (0, 4), (-1, 4), TABLE_ROW_ODD),
    ('GRID', (0, 0), (-1, -1), 0.5, TEXT_MUTED),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ('TOPPADDING', (0, 0), (-1, -1), 6),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
]))
story.append(Spacer(1, 12))
story.append(api_table)
story.append(Paragraph('Table 3: API Endpoints', caption_style))

story.append(Paragraph('<b>Code: /api/reveal endpoint</b>', h3_style))
story.append(Paragraph(
    '@app.route("/api/reveal", methods=["POST"])<br/>'
    'def reveal():<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;data = request.get_json(silent=True)<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;game_id = data.get("game_id")<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;cell_index = data.get("cell_index")<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;game = games[game_id]<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;result = game.reveal_cell(int(cell_index))<br/>'
    '&nbsp;&nbsp;&nbsp;&nbsp;return jsonify(result.to_dict())',
    code_style
))

# ═══════════════════════════════════════════════════════════
# SECTION 5: DATA FLOW
# ═══════════════════════════════════════════════════════════
story.append(Paragraph('<b>5. Data Flow: Click to Result</b>', h1_style))
story.append(Paragraph(
    'Understanding the complete data flow from a user click to a visual result is essential for '
    'maintaining and extending the game. In PyScript mode, the flow is entirely within the browser: '
    'a click event triggers the Python on_cell_click() function, which calls the Python game engine '
    '(game.reveal_cell()), receives a RevealResult object, and then updates the DOM directly. In Flask '
    'server mode, the click triggers a fetch() call to /api/reveal, which processes the request through '
    'the same Python game engine on the server, serializes the RevealResult to JSON, and returns it to '
    'the browser for DOM updates. Both paths use the identical Python game logic, ensuring consistent '
    'behavior regardless of the runtime environment.',
    body_style
))

flow_data = [
    [Paragraph('<b>Step</b>', header_cell_style), Paragraph('<b>PyScript Mode</b>', header_cell_style), Paragraph('<b>Server Mode</b>', header_cell_style)],
    [Paragraph('1. User clicks cell', cell_style), Paragraph('DOM click event', cell_style), Paragraph('DOM click event', cell_style)],
    [Paragraph('2. Handler invoked', cell_style), Paragraph('Python on_cell_click()', cell_style), Paragraph('JS fetch() to /api/reveal', cell_style)],
    [Paragraph('3. Game logic runs', cell_style), Paragraph('Python game.reveal_cell()', cell_style), Paragraph('Python game.reveal_cell() on server', cell_style)],
    [Paragraph('4. Result returned', cell_style), Paragraph('RevealResult Python object', cell_style), Paragraph('JSON response from Flask', cell_style)],
    [Paragraph('5. DOM updated', cell_style), Paragraph('Python updates DOM directly', cell_style), Paragraph('JS updates DOM from JSON', cell_style)],
]
flow_table = Table(flow_data, colWidths=[available_width*0.22, available_width*0.39, available_width*0.39], hAlign='CENTER')
flow_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), TABLE_HEADER_COLOR),
    ('TEXTCOLOR', (0, 0), (-1, 0), TABLE_HEADER_TEXT),
    ('BACKGROUND', (0, 1), (-1, 1), TABLE_ROW_EVEN),
    ('BACKGROUND', (0, 2), (-1, 2), TABLE_ROW_ODD),
    ('BACKGROUND', (0, 3), (-1, 3), TABLE_ROW_EVEN),
    ('BACKGROUND', (0, 4), (-1, 4), TABLE_ROW_ODD),
    ('BACKGROUND', (0, 5), (-1, 5), TABLE_ROW_EVEN),
    ('GRID', (0, 0), (-1, -1), 0.5, TEXT_MUTED),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ('TOPPADDING', (0, 0), (-1, -1), 6),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
]))
story.append(Spacer(1, 12))
story.append(flow_table)
story.append(Paragraph('Table 4: Data Flow Comparison - PyScript vs Server Mode', caption_style))

# ═══════════════════════════════════════════════════════════
# SECTION 6: FILE STRUCTURE
# ═══════════════════════════════════════════════════════════
story.append(Paragraph('<b>6. Project File Structure</b>', h1_style))
story.append(Paragraph(
    'The project is organized to maximize Python code visibility on GitHub. All game logic resides in '
    '.py files, while HTML is kept to a minimal shell with only CSS styling and structure. The game/ '
    'directory is a proper Python package with __init__.py exports. The Android project wraps the HTML '
    'in a Kotlin WebView, allowing the same Python-powered game to run as a native mobile app.',
    body_style
))

files_data = [
    [Paragraph('<b>File</b>', header_cell_style), Paragraph('<b>Lines</b>', header_cell_style), Paragraph('<b>Language</b>', header_cell_style), Paragraph('<b>Purpose</b>', header_cell_style)],
    [Paragraph('game/engine.py', cell_style), Paragraph('550', cell_center_style), Paragraph('Python', cell_center_style), Paragraph('Core game engine', cell_style)],
    [Paragraph('pyscript_app.py', cell_style), Paragraph('662', cell_center_style), Paragraph('Python', cell_center_style), Paragraph('Browser UI controller', cell_style)],
    [Paragraph('server.py', cell_style), Paragraph('235', cell_center_style), Paragraph('Python', cell_center_style), Paragraph('Flask API server', cell_style)],
    [Paragraph('game/__init__.py', cell_style), Paragraph('36', cell_center_style), Paragraph('Python', cell_center_style), Paragraph('Package exports', cell_style)],
    [Paragraph('app.py', cell_style), Paragraph('26', cell_center_style), Paragraph('Python', cell_center_style), Paragraph('Server entry point', cell_style)],
    [Paragraph('templates/index.html', cell_style), Paragraph('149', cell_center_style), Paragraph('HTML', cell_center_style), Paragraph('Minimal CSS + structure', cell_style)],
    [Paragraph('MainActivity.kt', cell_style), Paragraph('48', cell_center_style), Paragraph('Kotlin', cell_center_style), Paragraph('Android WebView', cell_style)],
]
files_table = Table(files_data, colWidths=[available_width*0.30, available_width*0.10, available_width*0.14, available_width*0.46], hAlign='CENTER')
files_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), TABLE_HEADER_COLOR),
    ('TEXTCOLOR', (0, 0), (-1, 0), TABLE_HEADER_TEXT),
    ('BACKGROUND', (0, 1), (-1, 1), TABLE_ROW_EVEN),
    ('BACKGROUND', (0, 2), (-1, 2), TABLE_ROW_ODD),
    ('BACKGROUND', (0, 3), (-1, 3), TABLE_ROW_EVEN),
    ('BACKGROUND', (0, 4), (-1, 4), TABLE_ROW_ODD),
    ('BACKGROUND', (0, 5), (-1, 5), TABLE_ROW_EVEN),
    ('BACKGROUND', (0, 6), (-1, 6), TABLE_ROW_ODD),
    ('BACKGROUND', (0, 7), (-1, 7), TABLE_ROW_EVEN),
    ('GRID', (0, 0), (-1, -1), 0.5, TEXT_MUTED),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ('TOPPADDING', (0, 0), (-1, -1), 6),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
]))
story.append(Spacer(1, 12))
story.append(files_table)
story.append(Paragraph('Table 5: Project Files - Python = 80%+ of codebase', caption_style))

# ═══════════════════════════════════════════════════════════
# SECTION 7: HOW TO RUN
# ═══════════════════════════════════════════════════════════
story.append(Paragraph('<b>7. How to Run</b>', h1_style))
story.append(Paragraph('<b>7.1 Browser Mode (No Server Needed)</b>', h2_style))
story.append(Paragraph(
    'The simplest way to play Bomb Sweep is to open the templates/index.html file directly in any modern '
    'browser. PyScript automatically loads the Python engine via WebAssembly, then loads pyscript_app.py '
    'and game/engine.py. The entire game runs in Python inside the browser - no server, no installation, '
    'no dependencies. Just double-click the HTML file and start playing. This also works on phones: send '
    'the HTML file to anyone and they can open it in their mobile browser.',
    body_style
))
story.append(Paragraph('<b>7.2 Flask Server Mode</b>', h2_style))
story.append(Paragraph(
    'For server-based gameplay, clone the repository, install Flask, and run the server. The Flask server '
    'manages game sessions in memory with UUID keys, processes reveal requests through the same Python '
    'game engine, and provides aggregate statistics across all players. Use a virtual environment on macOS '
    'to avoid system Python conflicts: python3 -m venv venv, source venv/bin/activate, pip install flask, '
    'then python3 app.py. The server runs on port 5001 (not 5000, which conflicts with macOS AirPlay).',
    body_style
))
story.append(Paragraph('<b>7.3 Android App</b>', h2_style))
story.append(Paragraph(
    'The android/ directory contains a complete Android Studio project. The app uses a Kotlin Activity '
    'with a WebView that loads the game HTML from the assets/ folder. Since PyScript loads Python from '
    'CDN, the app requires an internet connection on first launch. After that, the browser cache handles '
    'subsequent loads. To build: open the android/ folder in Android Studio, wait for Gradle sync, then '
    'click Run. The APK can be shared directly with others for installation on their Android phones.',
    body_style
))

# ── Build PDF ──
doc.build(story)
print(f"PDF generated: {output_path}")

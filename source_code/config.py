# ============================================================
#  config.py  –  Caro AI  –  Global Configuration
# ============================================================

BOARD_SIZE   = 15
WIN_LENGTH   = 4        # ← đề yêu cầu 4 quân liên tiếp
EMPTY        = 0
HUMAN        = 1
AI           = 2
CANDIDATE_RADIUS = 2

# ── Window ────────────────────────────────────────────────────
WIN_W = 1280
WIN_H = 780

# ── Board render ──────────────────────────────────────────────
CELL  = 40
BX    = 30          # board left offset
BY    = 70          # board top  offset

# Panel (right side of board)
PANEL_X = BX + BOARD_SIZE * CELL + 18
PANEL_W = WIN_W - PANEL_X - 6

FPS   = 60

# ── Colors ───────────────────────────────────────────────────
C_BG         = (13, 15, 22)
C_BOARD      = (20, 25, 38)
C_GRID       = (38, 50, 72)
C_GRID_HI    = (60, 80, 115)
C_DOT        = (70, 90, 130)

C_X          = (70,  190, 255)   # Human  – blue
C_O          = (255, 85,  110)   # AI     – red
C_LAST       = (255, 215, 50)
C_HOVER      = (255, 255, 255, 35)
C_WIN_CELL   = (0,   255, 150)

C_PANEL      = (15, 19, 30)
C_BORDER     = (40, 55, 82)

C_W          = (215, 225, 255)   # text white
C_DIM        = (110, 130, 170)   # text dim
C_ACC        = (70,  190, 255)   # accent cyan
C_GOOD       = (70,  230, 140)
C_BAD        = (255, 85,  110)
C_WARN       = (255, 175, 55)

C_BTN        = (28, 36, 58)
C_BTN_H      = (45, 60, 98)
C_BTN_A      = (50, 110, 190)
C_BTN_BD     = (55, 72, 115)

# ── Evaluation weights ────────────────────────────────────────
SC_WIN       =  1_000_000
SC_LOSE      = -1_000_000

SC_AI_O4     =  500_000   # open 4
SC_AI_C4     =   80_000   # closed 4
SC_AI_O3     =   10_000
SC_AI_C3     =    2_000
SC_AI_O2     =    1_000
SC_AI_C2     =      200

SC_EN_O4     = -900_000   # enemy open-4 = near-win → MUST block (higher than SC_AI_O4)
SC_EN_C4     = -150_000
SC_EN_O3     =  -20_000
SC_EN_C3     =   -4_000
SC_EN_O2     =   -1_500
SC_EN_C2     =     -300

# ── Difficulty depths ─────────────────────────────────────────
DEPTHS = {"Easy": 1, "Medium": 2, "Hard": 3}

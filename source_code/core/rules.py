import numpy as np
from config import BOARD_SIZE, WIN_LENGTH, EMPTY

DIRS = [(0, 1), (1, 0), (1, 1), (1, -1)]


def check_win(grid, r, c, player, size=BOARD_SIZE, wl=WIN_LENGTH):
    for dr, dc in DIRS:
        cnt = 1
        nr, nc = r + dr, c + dc
        while 0 <= nr < size and 0 <= nc < size and grid[nr][nc] == player:
            cnt += 1; nr += dr; nc += dc
        nr, nc = r - dr, c - dc
        while 0 <= nr < size and 0 <= nc < size and grid[nr][nc] == player:
            cnt += 1; nr -= dr; nc -= dc
        if cnt >= wl:
            return True
    return False


def get_win_cells(grid, r, c, player, size=BOARD_SIZE, wl=WIN_LENGTH):
    for dr, dc in DIRS:
        cells = [(r, c)]
        nr, nc = r + dr, c + dc
        while 0 <= nr < size and 0 <= nc < size and grid[nr][nc] == player:
            cells.append((nr, nc)); nr += dr; nc += dc
        nr, nc = r - dr, c - dc
        while 0 <= nr < size and 0 <= nc < size and grid[nr][nc] == player:
            cells.append((nr, nc)); nr -= dr; nc -= dc
        if len(cells) >= wl:
            return cells
    return []


def is_draw(grid, size=BOARD_SIZE):
    return not np.any(grid == EMPTY)

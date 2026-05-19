import numpy as np
from config import (BOARD_SIZE, WIN_LENGTH, EMPTY, HUMAN, AI,
                    SC_WIN, SC_LOSE,
                    SC_AI_O4, SC_AI_C4, SC_AI_O3, SC_AI_C3, SC_AI_O2, SC_AI_C2,
                    SC_EN_O4, SC_EN_C4, SC_EN_O3, SC_EN_C3, SC_EN_O2, SC_EN_C2)

DIRS = [(0, 1), (1, 0), (1, 1), (1, -1)]


def _run(grid, r, c, dr, dc, player, size):
    """Count run length + openness starting at (r,c) going (dr,dc)."""
    cnt = 0
    nr, nc = r, c
    while 0 <= nr < size and 0 <= nc < size and grid[nr][nc] == player:
        cnt += 1; nr += dr; nc += dc
    tail_open = (0 <= nr < size and 0 <= nc < size and grid[nr][nc] == EMPTY)
    hr, hc = r - dr, c - dc
    head_open = (0 <= hr < size and 0 <= hc < size and grid[hr][hc] == EMPTY)
    return cnt, head_open, tail_open


def evaluate(grid, size=BOARD_SIZE):
    score = 0
    seen_ai = set(); seen_hu = set()

    for r in range(size):
        for c in range(size):
            cell = grid[r][c]
            if cell == EMPTY:
                continue
            for dr, dc in DIRS:
                pr, pc = r - dr, c - dc
                if 0 <= pr < size and 0 <= pc < size and grid[pr][pc] == cell:
                    continue          # not start of run
                key = (r, c, dr, dc)
                if cell == AI:
                    if key in seen_ai: continue
                    seen_ai.add(key)
                    cnt, ho, ot = _run(grid, r, c, dr, dc, AI, size)
                    score += _pat(cnt, ho, ot, True)
                else:
                    if key in seen_hu: continue
                    seen_hu.add(key)
                    cnt, ho, ot = _run(grid, r, c, dr, dc, HUMAN, size)
                    score += _pat(cnt, ho, ot, False)
    return score


def _pat(cnt, ho, ot, is_ai):
    opens = int(ho) + int(ot)
    if cnt >= WIN_LENGTH:
        return SC_WIN if is_ai else SC_LOSE
    
    #Nếu chuỗi bị chặn cả 2 đầu (opens == 0), nó là chuỗi chết, không có giá trị
    if opens == 0:
        return 0

    if is_ai:
        if cnt == 3: return SC_AI_O4 if opens == 2 else SC_AI_C4
        if cnt == 2: return SC_AI_O3 if opens == 2 else SC_AI_C3   # note: WIN=4, so 3-in-row is near-win
        if cnt == 1: return SC_AI_O2 if opens == 2 else SC_AI_C2
    else:
        if cnt == 3: return SC_EN_O4 if opens == 2 else SC_EN_C4
        if cnt == 2: return SC_EN_O3 if opens == 2 else SC_EN_C3
        if cnt == 1: return SC_EN_O2 if opens == 2 else SC_EN_C2
    return 0

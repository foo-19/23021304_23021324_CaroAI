import numpy as np
from config import BOARD_SIZE, EMPTY, CANDIDATE_RADIUS, AI, HUMAN, WIN_LENGTH

DIRS = [(0, 1), (1, 0), (1, 1), (1, -1)]


def get_candidates(grid, size=BOARD_SIZE, radius=CANDIDATE_RADIUS):
    """Trả về các ô trống trong bán kính radius quanh quân đã đặt."""
    if not np.any(grid != EMPTY):
        c = size // 2
        return [(c, c)]
    cands = set()
    rs, cs = np.where(grid != EMPTY)
    for r, c in zip(rs.tolist(), cs.tolist()):
        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                nr, nc = r + dr, c + dc
                if 0 <= nr < size and 0 <= nc < size and grid[nr][nc] == EMPTY:
                    cands.add((nr, nc))
    return list(cands)


def _quick_score(grid, r, c, size):
    """
    Heuristic nhanh để sắp xếp candidate – KHÔNG simulate đặt quân,
    chỉ đếm quân lân cận và chuỗi kề liền.
    Ưu tiên: ô kề cạnh quân địch (phòng thủ) > ô kề cạnh quân mình (tấn công).
    """
    s = 0.0
    center = size / 2.0
    # Khoảng cách trung tâm (tiebreaker nhỏ)
    s -= (abs(r - center) + abs(c - center)) * 0.1

    for dr, dc in DIRS:
        ai_run = 0; hu_run = 0
        # đếm chuỗi AI và HUMAN kề ô (r,c) theo cả 2 phía
        for sign in (1, -1):
            nr, nc = r + sign*dr, c + sign*dc
            while 0 <= nr < size and 0 <= nc < size:
                if grid[nr][nc] == AI:
                    ai_run += 1; nr += sign*dr; nc += sign*dc
                else:
                    break
            nr, nc = r + sign*dr, c + sign*dc
            while 0 <= nr < size and 0 <= nc < size:
                if grid[nr][nc] == HUMAN:
                    hu_run += 1; nr += sign*dr; nc += sign*dc
                else:
                    break

        # Chặn địch thắng ngay > tạo thắng > chuỗi dài
        if hu_run >= WIN_LENGTH - 1: s += 5000.0
        elif hu_run == WIN_LENGTH - 2: s += 200.0
        elif hu_run == 1: s += 20.0

        if ai_run >= WIN_LENGTH - 1: s += 4000.0
        elif ai_run == WIN_LENGTH - 2: s += 150.0
        elif ai_run == 1: s += 15.0

    return s


def get_ordered_candidates(grid, player, size=BOARD_SIZE, radius=CANDIDATE_RADIUS):
    """Trả về danh sách candidate đã sắp xếp theo _quick_score."""
    cands = get_candidates(grid, size, radius)
    cands.sort(key=lambda pos: _quick_score(grid, pos[0], pos[1], size), reverse=True)
    return cands

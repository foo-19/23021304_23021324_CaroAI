"""Pure Minimax – no pruning. Used for Level 1 and benchmark baseline."""
from __future__ import annotations
import time
import numpy as np
from dataclasses import dataclass
from core.rules import check_win, is_draw
from core.moves import get_candidates, get_ordered_candidates
from ai.eval import evaluate
from config import BOARD_SIZE, AI, HUMAN, SC_WIN, SC_LOSE, EMPTY


@dataclass
class MoveResult:
    move: tuple | None = None
    value: int = 0
    nodes: int = 0
    depth: int = 0
    elapsed: float = 0.0
    algo: str = "Minimax"


def _find_immediate(grid, player, size):
    """Trả về (ô_thắng, số_node_đã_duyệt) hoặc (None, số_node_đã_duyệt)."""
    nodes = 0
    rs, cs = np.where(grid == EMPTY)
    for r, c in zip(rs.tolist(), cs.tolist()):
        grid[r][c] = player
        nodes += 1
        win = check_win(grid, r, c, player, size)
        grid[r][c] = EMPTY
        if win:
            return (r, c), nodes
    return None, nodes


class Minimax:
    def __init__(self, depth=2, size=BOARD_SIZE):
        self.depth = depth
        self.size  = size
        self.nodes = 0

    def get_move(self, grid: np.ndarray) -> MoveResult:
        self.nodes = 1
        t0 = time.perf_counter()
        center = self.size / 2.0

        # Pass 1: AI thắng ngay?
        win_move, n1 = _find_immediate(grid, AI, self.size)
        self.nodes += n1
        if win_move:
            return MoveResult(win_move, SC_WIN, self.nodes,
                              self.depth, time.perf_counter() - t0, "Minimax")

        # Pass 2: chặn địch thắng ngay (quét toàn bàn, không giới hạn radius)
        block_move, n2 = _find_immediate(grid, HUMAN, self.size)
        self.nodes += n2
        if block_move:
            return MoveResult(block_move, SC_LOSE + 1, self.nodes,
                              self.depth, time.perf_counter() - t0, "Minimax")

        # Pass 3: Minimax search trên candidates đã sắp xếp
        best_val  = -10**9
        best_move = None

        for r, c in get_ordered_candidates(grid, AI, self.size):
            grid[r][c] = AI
            self.nodes += 1
            val = self._mm(grid, self.depth - 1, False)
            grid[r][c] = EMPTY
            if best_move is None or val > best_val or (
                val == best_val and
                (abs(r - center) + abs(c - center)) <
                (abs(best_move[0] - center) + abs(best_move[1] - center))
            ):
                best_val = val; best_move = (r, c)

        return MoveResult(best_move, best_val, self.nodes,
                          self.depth, time.perf_counter() - t0, "Minimax")

    def _mm(self, grid, depth, is_max):
        if depth == 0 or is_draw(grid, self.size):
            return evaluate(grid, self.size)

        if is_max:  # Lượt AI (MAX node)
            best = -10**9
            for r, c in get_ordered_candidates(grid, AI, self.size):
                grid[r][c] = AI
                self.nodes += 1
                if check_win(grid, r, c, AI, self.size):
                    grid[r][c] = EMPTY
                    return SC_WIN + depth
                best = max(best, self._mm(grid, depth - 1, False))
                grid[r][c] = EMPTY
            return best
        else:       # Lượt HUMAN (MIN node)
            best = 10**9
            for r, c in get_ordered_candidates(grid, HUMAN, self.size):
                grid[r][c] = HUMAN
                self.nodes += 1
                if check_win(grid, r, c, HUMAN, self.size):
                    grid[r][c] = EMPTY
                    return SC_LOSE - depth
                best = min(best, self._mm(grid, depth - 1, True))
                grid[r][c] = EMPTY
            return best

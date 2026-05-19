"""Alpha-Beta pruning AI. Same eval as Minimax for fair comparison."""
from __future__ import annotations
import time
import numpy as np
from core.rules import check_win, is_draw
from core.moves import get_ordered_candidates
from ai.eval import evaluate
from ai.minimax import MoveResult, _find_immediate
from config import BOARD_SIZE, AI, HUMAN, SC_WIN, SC_LOSE, EMPTY

EXACT = 0; LOWER = 1; UPPER = 2


class AlphaBeta:
    def __init__(self, depth=3, size=BOARD_SIZE, use_tt=True):
        self.depth  = depth
        self.size   = size
        self.use_tt = use_tt
        self._tt: dict = {}
        self.nodes  = 0

    def get_move(self, grid: np.ndarray, clear_tt=True) -> MoveResult:
        self.nodes = 1
        if clear_tt:
            self._tt.clear()
        t0     = time.perf_counter()
        center = self.size / 2.0

        # Pass 1: AI thắng ngay?
        win_move, n1 = _find_immediate(grid, AI, self.size)
        self.nodes += n1
        if win_move:
            return MoveResult(win_move, SC_WIN, self.nodes,
                              self.depth, time.perf_counter() - t0, "AlphaBeta")

        # Pass 2: chặn địch thắng ngay (quét toàn bàn)
        block_move, n2 = _find_immediate(grid, HUMAN, self.size)
        self.nodes += n2
        if block_move:
            return MoveResult(block_move, SC_LOSE + 1, self.nodes,
                              self.depth, time.perf_counter() - t0, "AlphaBeta")

        # Pass 3: Alpha-Beta search
        best_val  = -10**9
        best_move = None
        alpha     = -10**9
        beta      =  10**9

        for r, c in get_ordered_candidates(grid, AI, self.size):
            grid[r][c] = AI
            self.nodes += 1
            val = self._ab(grid, self.depth - 1, alpha, beta, False)
            grid[r][c] = EMPTY
            if best_move is None or val > best_val or (
                val == best_val and
                (abs(r - center) + abs(c - center)) <
                (abs(best_move[0] - center) + abs(best_move[1] - center))
            ):
                best_val = val; best_move = (r, c)
            alpha = max(alpha, best_val)

        return MoveResult(best_move, best_val, self.nodes,
                          self.depth, time.perf_counter() - t0, "AlphaBeta")

    def _ab(self, grid, depth, alpha, beta, is_max):
        key = hash(grid.tobytes())
        if self.use_tt:
            e = self._tt.get(key)
            if e and e[1] >= depth:
                sc, _, flag, _ = e
                if flag == EXACT: return sc
                if flag == LOWER: alpha = max(alpha, sc)
                if flag == UPPER: beta  = min(beta,  sc)
                if alpha >= beta: return sc

        if depth == 0 or is_draw(grid, self.size):
            return evaluate(grid, self.size)

        orig_a = alpha
        orig_b = beta
        best   = -10**9 if is_max else 10**9
        player = AI if is_max else HUMAN

        for r, c in get_ordered_candidates(grid, player, self.size):
            grid[r][c] = player
            self.nodes += 1
            if check_win(grid, r, c, player, self.size):
                grid[r][c] = EMPTY
                best = SC_WIN + depth if is_max else SC_LOSE - depth
                break
            val = self._ab(grid, depth - 1, alpha, beta, not is_max)
            grid[r][c] = EMPTY
            if is_max:
                if val > best: best = val
                alpha = max(alpha, best)
            else:
                if val < best: best = val
                beta  = min(beta,  best)
            if alpha >= beta:
                break

        if self.use_tt:
            flag = EXACT
            if best <= orig_a: flag = UPPER
            elif best >= orig_b: flag = LOWER
            if len(self._tt) < 150_000:
                self._tt[key] = (best, depth, flag, None)

        return best

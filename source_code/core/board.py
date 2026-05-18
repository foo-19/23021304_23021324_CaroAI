import numpy as np
from config import BOARD_SIZE, EMPTY


class Board:
    def __init__(self, size=BOARD_SIZE):
        self.size = size
        self.grid = np.zeros((size, size), dtype=np.int8)
        self._stack = []          # move history
        self.move_count = 0

    def place(self, r, c, player):
        if not self.is_valid(r, c):
            return False
        self.grid[r][c] = player
        self._stack.append((r, c))
        self.move_count += 1
        return True

    def undo(self):
        if not self._stack:
            return None
        r, c = self._stack.pop()
        self.grid[r][c] = EMPTY
        self.move_count -= 1
        return r, c

    def is_valid(self, r, c):
        return 0 <= r < self.size and 0 <= c < self.size and self.grid[r][c] == EMPTY

    def is_full(self):
        return self.move_count == self.size * self.size

    def last_move(self):
        return self._stack[-1] if self._stack else None

    def copy(self):
        b = Board(self.size)
        b.grid = self.grid.copy()
        b._stack = list(self._stack)
        b.move_count = self.move_count
        return b

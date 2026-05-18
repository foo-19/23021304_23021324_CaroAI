"""Reusable board widget – can be placed anywhere on screen."""
from __future__ import annotations
import math
import pygame
from config import (BOARD_SIZE, EMPTY, HUMAN, AI, WIN_LENGTH,
                    CELL, C_BOARD, C_GRID, C_GRID_HI, C_DOT,
                    C_X, C_O, C_LAST, C_HOVER, C_WIN_CELL, C_DIM, C_W)


class BoardWidget:
    """
    Draws a Caro board at (ox, oy) with given cell_size.
    Accepts an external numpy grid (read-only view).
    """

    def __init__(self, ox: int, oy: int, cell: int = CELL,
                 size: int = BOARD_SIZE, fonts=None,
                 interactive: bool = True):
        self.ox   = ox
        self.oy   = oy
        self.cell = cell
        self.size = size
        self.fonts= fonts or {}
        self.interactive = interactive

        self._hover: tuple | None = None
        self._win_cells: list     = []
        self._win_tick            = 0
        self._place_anim: list    = []   # [(cx,cy,color,tick,max_tick)]

    # ── Public API ────────────────────────────────────────────
    def set_win_cells(self, cells):
        self._win_cells = cells
        self._win_tick  = 0

    def clear_win_cells(self):
        self._win_cells = []
        self._win_tick  = 0

    def trigger_anim(self, r, c, player):
        cx, cy = self._px(r, c)
        col = C_X if player == HUMAN else C_O
        self._place_anim.append([cx, cy, col, 0, 10])

    def update(self):
        self._win_tick += 1
        self._place_anim = [a for a in self._place_anim if a[3] < a[4]]
        for a in self._place_anim:
            a[3] += 1

    def handle_event(self, ev):
        """Returns (r,c) if user clicked a valid cell, else None."""
        if not self.interactive:
            return None
        if ev.type == pygame.MOUSEMOTION:
            self._hover = self._cell_at(ev.pos)
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            return self._cell_at(ev.pos)
        return None

    def draw(self, surf, grid, current_player=None, enabled=True):
        self._draw_bg(surf)
        self._draw_grid(surf)
        self._draw_labels(surf)
        self._draw_stones(surf, grid)
        self._draw_last_move(surf, grid)
        if enabled and self.interactive and current_player == HUMAN:
            self._draw_hover(surf, grid)
        self._draw_win_anim(surf)
        self._draw_place_anim(surf)

    # ── Internals ─────────────────────────────────────────────
    def _px(self, r, c):
        return (self.ox + c * self.cell, self.oy + r * self.cell)

    def _cell_at(self, pos):
        px, py = pos
        col = round((px - self.ox) / self.cell)
        row = round((py - self.oy) / self.cell)
        if 0 <= row < self.size and 0 <= col < self.size:
            return row, col
        return None

    def _draw_bg(self, surf):
        bw = (self.size - 1) * self.cell + self.cell
        pygame.draw.rect(surf, C_BOARD,
                         (self.ox - self.cell//2, self.oy - self.cell//2, bw, bw),
                         border_radius=4)

    def _draw_grid(self, surf):
        for i in range(self.size):
            x0 = self.ox; x1 = self.ox + (self.size-1)*self.cell
            y  = self.oy + i*self.cell
            col = C_GRID_HI if i in (0, self.size-1, self.size//2) else C_GRID
            pygame.draw.line(surf, col, (x0, y), (x1, y))
        for j in range(self.size):
            y0 = self.oy; y1 = self.oy + (self.size-1)*self.cell
            x  = self.ox + j*self.cell
            col = C_GRID_HI if j in (0, self.size-1, self.size//2) else C_GRID
            pygame.draw.line(surf, col, (x, y0), (x, y1))
        # star points
        for r, c in [(3,3),(3,11),(11,3),(11,11),(7,7)]:
            if r < self.size and c < self.size:
                cx, cy = self._px(r, c)
                pygame.draw.circle(surf, C_DOT, (cx, cy), 3)

    def _draw_labels(self, surf):
        if not self.fonts:
            return
        f = self.fonts.get("small")
        if not f:
            return
        letters = "ABCDEFGHJKLMNOP"
        for i in range(self.size):
            x = self.ox + i*self.cell
            t = f.render(letters[i], True, C_DIM)
            surf.blit(t, t.get_rect(center=(x, self.oy - 18)))
            t2 = f.render(str(i+1), True, C_DIM)
            surf.blit(t2, t2.get_rect(center=(self.ox - 18, self.oy + i*self.cell)))

    def _draw_stones(self, surf, grid):
        rad = self.cell // 2 - 3
        for r in range(self.size):
            for c in range(self.size):
                p = grid[r][c]
                if p == EMPTY:
                    continue
                cx, cy = self._px(r, c)
                col = C_X if p == HUMAN else C_O
                # glow
                gs = pygame.Surface((rad*2+10, rad*2+10), pygame.SRCALPHA)
                pygame.draw.circle(gs, (*col, 40), (rad+5, rad+5), rad+4)
                surf.blit(gs, (cx-rad-5, cy-rad-5))
                # stone
                pygame.draw.circle(surf, col, (cx, cy), rad)
                # highlight
                hl = tuple(min(255, v+70) for v in col)
                pygame.draw.circle(surf, hl, (cx-rad//4, cy-rad//4), rad//3)

    def _draw_last_move(self, surf, grid):
        # find last move from grid iteration is not possible, handled externally
        pass  # caller calls trigger_anim instead

    def _draw_hover(self, surf, grid):
        if self._hover is None:
            return
        r, c = self._hover
        if not (0 <= r < self.size and 0 <= c < self.size and grid[r][c] == EMPTY):
            return
        cx, cy = self._px(r, c)
        rad = self.cell // 2 - 3
        s = pygame.Surface((rad*2+2, rad*2+2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255,255,255,40), (rad+1,rad+1), rad)
        surf.blit(s, (cx-rad-1, cy-rad-1))

    def _draw_win_anim(self, surf):
        if not self._win_cells:
            return
        t = (self._win_tick % 40) / 40
        alpha = int(100 + 100 * math.sin(t * math.pi * 2))
        rad   = self.cell // 2 - 1
        for r, c in self._win_cells:
            cx, cy = self._px(r, c)
            s = pygame.Surface((rad*2+4, rad*2+4), pygame.SRCALPHA)
            pygame.draw.circle(s, (0, 255, 150, alpha), (rad+2, rad+2), rad+1)
            surf.blit(s, (cx-rad-2, cy-rad-2))

    def _draw_place_anim(self, surf):
        for cx, cy, col, tick, max_tick in self._place_anim:
            t   = tick / max_tick
            rad = int((self.cell//2 - 3) * t)
            if rad <= 0:
                continue
            s = pygame.Surface((rad*2+2, rad*2+2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*col, int(200*(1-t))), (rad+1,rad+1), rad)
            surf.blit(s, (cx-rad-1, cy-rad-1))

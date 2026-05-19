"""Reusable board widget : ô vuông, quân X vẽ 2 đường chéo, O vẽ tròn rỗng."""
from __future__ import annotations
import math
import pygame
from config import (BOARD_SIZE, EMPTY, HUMAN, AI,
                    CELL, C_CELL_FILL, C_CELL_BD,
                    C_X, C_O, C_WIN_CELL, C_DIM)


class BoardWidget:
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
        self._place_anim: list    = []   # [r, c, player, tick, max_tick]

    #  Public API 
    def set_win_cells(self, cells):
        self._win_cells = cells
        self._win_tick  = 0

    def clear_win_cells(self):
        self._win_cells = []
        self._win_tick  = 0

    def trigger_anim(self, r, c, player):
        self._place_anim.append([r, c, player, 0, 10])

    def update(self):
        self._win_tick += 1
        self._place_anim = [a for a in self._place_anim if a[3] < a[4]]
        for a in self._place_anim:
            a[3] += 1

    def handle_event(self, ev):
        if not self.interactive:
            return None
        if ev.type == pygame.MOUSEMOTION:
            self._hover = self._cell_at(ev.pos)
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            return self._cell_at(ev.pos)
        return None

    def draw(self, surf, grid, current_player=None, enabled=True):
        self._draw_cells(surf)
        self._draw_labels(surf)
        self._draw_stones(surf, grid)
        self._draw_win_anim(surf)
        self._draw_place_anim(surf)
        if enabled and self.interactive and current_player == HUMAN:
            self._draw_hover(surf, grid)

    #  Helpers 
    def _cell_rect(self, r, c):
        return pygame.Rect(self.ox + c * self.cell,
                           self.oy + r * self.cell,
                           self.cell, self.cell)

    def _cell_center(self, r, c):
        rect = self._cell_rect(r, c)
        return rect.centerx, rect.centery

    def _cell_at(self, pos):
        px, py = pos
        c = (px - self.ox) // self.cell
        r = (py - self.oy) // self.cell
        if (0 <= r < self.size and 0 <= c < self.size and
                self.ox <= px < self.ox + self.size * self.cell and
                self.oy <= py < self.oy + self.size * self.cell):
            return r, c
        return None

    #  Draw helpers 
    def _draw_X(self, surf, r, c, col, alpha=255, thickness=None):
        rect  = self._cell_rect(r, c)
        pad   = self.cell // 5
        thick = thickness or max(3, self.cell // 10)
        x0, y0 = rect.x + pad, rect.y + pad
        x1, y1 = rect.right - pad, rect.bottom - pad

        if alpha < 255:
            s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            pygame.draw.line(s, (*col, alpha), (pad, pad),
                             (rect.w-pad, rect.h-pad), thick)
            pygame.draw.line(s, (*col, alpha), (rect.w-pad, pad),
                             (pad, rect.h-pad), thick)
            surf.blit(s, rect.topleft)
        else:
            # glow
            gs = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            pygame.draw.line(gs, (*col, 35), (pad-2, pad-2),
                             (rect.w-pad+2, rect.h-pad+2), thick+6)
            pygame.draw.line(gs, (*col, 35), (rect.w-pad+2, pad-2),
                             (pad-2, rect.h-pad+2), thick+6)
            surf.blit(gs, rect.topleft)
            pygame.draw.line(surf, col, (x0, y0), (x1, y1), thick)
            pygame.draw.line(surf, col, (x1, y0), (x0, y1), thick)

    def _draw_O(self, surf, r, c, col, alpha=255, thickness=None):
        rect   = self._cell_rect(r, c)
        pad    = self.cell // 5
        thick  = thickness or max(3, self.cell // 10)
        cx, cy = rect.centerx, rect.centery
        radius = self.cell // 2 - pad

        if alpha < 255:
            s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            pygame.draw.circle(s, (*col, alpha),
                               (rect.w//2, rect.h//2), radius, thick)
            surf.blit(s, rect.topleft)
        else:
            # glow
            gs = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            pygame.draw.circle(gs, (*col, 35),
                               (rect.w//2, rect.h//2), radius+4, thick+6)
            surf.blit(gs, rect.topleft)
            pygame.draw.circle(surf, col, (cx, cy), radius, thick)

    # Draw methods 
    def _draw_cells(self, surf):
        for r in range(self.size):
            for c in range(self.size):
                rect = self._cell_rect(r, c)
                pygame.draw.rect(surf, C_CELL_FILL, rect)
                pygame.draw.rect(surf, C_CELL_BD, rect, 1)

    def _draw_labels(self, surf):
        f = self.fonts.get("small")
        if not f:
            return
        letters = "ABCDEFGHI"
        for i in range(self.size):
            cx, _ = self._cell_center(0, i)
            t = f.render(letters[i], True, C_DIM)
            surf.blit(t, t.get_rect(center=(cx, self.oy - 16)))
            _, cy = self._cell_center(i, 0)
            t2 = f.render(str(i + 1), True, C_DIM)
            surf.blit(t2, t2.get_rect(center=(self.ox - 16, cy)))

    def _draw_stones(self, surf, grid):
        for r in range(self.size):
            for c in range(self.size):
                p = grid[r][c]
                if p == EMPTY:
                    continue
                if p == HUMAN:
                    self._draw_X(surf, r, c, C_X)
                else:
                    self._draw_O(surf, r, c, C_O)

    def _draw_hover(self, surf, grid):
        if self._hover is None:
            return
        r, c = self._hover
        if not (0 <= r < self.size and 0 <= c < self.size and grid[r][c] == EMPTY):
            return
        rect = self._cell_rect(r, c)
        s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        s.fill((255, 255, 255, 20))
        surf.blit(s, rect.topleft)
        # preview X mờ
        self._draw_X(surf, r, c, C_X, alpha=60)

    def _draw_win_anim(self, surf):
        if not self._win_cells:
            return
        t     = (self._win_tick % 40) / 40
        alpha = int(70 + 70 * math.sin(t * math.pi * 2))
        for r, c in self._win_cells:
            rect = self._cell_rect(r, c)
            s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            s.fill((0, 255, 150, alpha))
            surf.blit(s, rect.topleft)
            pygame.draw.rect(surf, C_WIN_CELL, rect, 2)

    def _draw_place_anim(self, surf):
        """Hiệu ứng quân xuất hiện dần (scale từ 0 → 1)."""
        for r, c, player, tick, max_tick in self._place_anim:
            t = tick / max_tick          # 0.0 → 1.0
            if t <= 0:
                continue
            rect  = self._cell_rect(r, c)
            pad   = self.cell // 5
            thick = max(3, self.cell // 10)

            # Scale ô xung quanh tâm
            cx, cy = rect.centerx, rect.centery
            half   = int((self.cell // 2 - pad) * t)
            if half < 2:
                continue

            if player == HUMAN:
                # vẽ X thu nhỏ
                s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
                a = int(220 * t)
                pygame.draw.line(s, (*C_X, a),
                                 (rect.w//2 - half, rect.h//2 - half),
                                 (rect.w//2 + half, rect.h//2 + half), thick)
                pygame.draw.line(s, (*C_X, a),
                                 (rect.w//2 + half, rect.h//2 - half),
                                 (rect.w//2 - half, rect.h//2 + half), thick)
                surf.blit(s, rect.topleft)
            else:
                # vẽ O thu nhỏ
                s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
                a = int(220 * t)
                pygame.draw.circle(s, (*C_O, a),
                                   (rect.w//2, rect.h//2), half, thick)
                surf.blit(s, rect.topleft)

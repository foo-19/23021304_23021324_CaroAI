"""Shared UI helpers used by all screens."""
from __future__ import annotations
import pygame
from config import (C_BTN, C_BTN_H, C_BTN_A, C_BTN_BD,
                    C_W, C_DIM, C_ACC, C_GOOD, C_BAD, C_WARN,
                    C_BORDER, C_PANEL)


def make_fonts():
    pygame.font.init()
    return {
        "title":  pygame.font.SysFont("consolas", 26, bold=True),
        "header": pygame.font.SysFont("consolas", 16, bold=True),
        "body":   pygame.font.SysFont("consolas", 13),
        "small":  pygame.font.SysFont("consolas", 11),
        "btn":    pygame.font.SysFont("consolas", 13, bold=True),
        "big":    pygame.font.SysFont("consolas", 40, bold=True),
    }


class Button:
    def __init__(self, x, y, w, h, label, font, active=False,
                 cn=C_BTN, ch=C_BTN_H, ca=C_BTN_A):
        self.rect   = pygame.Rect(x, y, w, h)
        self.label  = label
        self.font   = font
        self.cn=cn; self.ch=ch; self.ca=ca
        self.active = active
        self._hov   = False

    def handle(self, ev) -> bool:
        if ev.type == pygame.MOUSEMOTION:
            self._hov = self.rect.collidepoint(ev.pos)
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            return self.rect.collidepoint(ev.pos)
        return False

    def draw(self, surf):
        col = self.ca if self.active else (self.ch if self._hov else self.cn)
        pygame.draw.rect(surf, col, self.rect, border_radius=5)
        pygame.draw.rect(surf, C_BTN_BD, self.rect, 1, border_radius=5)
        t = self.font.render(self.label, True, C_W)
        surf.blit(t, t.get_rect(center=self.rect.center))

    def move_to(self, x, y):
        self.rect.topleft = (x, y)


class MoveLog:
    """Scrollable log panel showing move history with stats."""
    MAX = 80

    def __init__(self, x, y, w, h, fonts):
        self.rect  = pygame.Rect(x, y, w, h)
        self.fonts = fonts
        self.entries: list[dict] = []
        self._scroll = 0

    def add(self, entry: dict):
        """entry keys: turn, player, move, value, nodes, time, algo"""
        self.entries.append(entry)
        if len(self.entries) > self.MAX:
            self.entries.pop(0)
        # auto-scroll to bottom
        fh = 17
        total = len(self.entries) * fh
        visible = self.rect.h - 30
        self._scroll = max(0, total - visible)

    def clear(self):
        self.entries.clear()
        self._scroll = 0

    def handle(self, ev):
        if ev.type == pygame.MOUSEWHEEL and self.rect.collidepoint(pygame.mouse.get_pos()):
            fh = 17
            total = len(self.entries) * fh
            visible = self.rect.h - 30
            self._scroll = max(0, min(max(0, total - visible),
                                      self._scroll - ev.y * 20))

    def draw(self, surf):
        pygame.draw.rect(surf, C_PANEL, self.rect)
        pygame.draw.rect(surf, C_BORDER, self.rect, 1)

        f = self.fonts["small"]
        fh = 17
        hdr = self.fonts["body"]

        # Header
        surf.blit(hdr.render("  # │ Player │ Move  │  Value  │  Nodes │  Time  │ Algo",
                              True, C_ACC), (self.rect.x + 4, self.rect.y + 4))
        pygame.draw.line(surf, C_BORDER,
                         (self.rect.x, self.rect.y + 22),
                         (self.rect.right, self.rect.y + 22))

        clip = pygame.Rect(self.rect.x, self.rect.y + 24,
                           self.rect.w, self.rect.h - 26)
        surf.set_clip(clip)

        y0 = self.rect.y + 24 - self._scroll
        for i, e in enumerate(self.entries):
            y = y0 + i * fh
            if y + fh < clip.top or y > clip.bottom:
                continue
            # Support custom pname (e.g. HvH uses "Player 1" / "Player 2")
            pname = e.get("pname") or ("Human" if e.get("player") == 1 else "AI")
            pcol  = C_ACC if e.get("player") == 1 else C_BAD
            mv    = str(e.get("move", "-"))
            val   = str(e.get("value", "-"))
            nd    = f"{e.get('nodes', 0):,}"
            tm    = f"{e.get('time', 0):.3f}s"
            algo  = e.get("algo", "-")
            turn  = str(e.get("turn", i + 1))

            line = f"{turn:>3} │ {pname:<8} │ {mv:<7}│ {val:>7} │ {nd:>7} │ {tm:<7}│ {algo}"
            col  = C_DIM if e.get("player") == 1 else C_W
            surf.blit(f.render(line, True, col), (self.rect.x + 4, y))

        surf.set_clip(None)


def draw_separator(surf, x, y, w, color=C_BORDER):
    pygame.draw.line(surf, color, (x, y), (x + w, y))


def draw_label(surf, text, x, y, font, color=C_DIM):
    surf.blit(font.render(text, True, color), (x, y))

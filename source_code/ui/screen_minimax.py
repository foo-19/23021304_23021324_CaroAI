"""Screen 1 : Human vs Minimax (pure, no alpha-beta)."""
from __future__ import annotations
import threading
import pygame
from config import (WIN_W, WIN_H, BOARD_SIZE, CELL, BX, BY,
                    HUMAN, AI, EMPTY,
                    C_BG, C_ACC, C_W, C_DIM, C_GOOD, C_BAD, C_WARN,
                    C_PANEL, C_BORDER, DEPTHS)
from core.board import Board
from core.rules import check_win, get_win_cells, is_draw
from core.moves import get_candidates
from ai.minimax import Minimax
from ui.board_widget import BoardWidget
from ui.common import Button, MoveLog, make_fonts, draw_label, draw_separator


PANEL_X = BX + BOARD_SIZE * CELL + 24
PANEL_W = WIN_W - PANEL_X - 10
LOG_H   = 195


class ScreenMinimax:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.fonts  = make_fonts()
        self._build_ui()
        self._new_game()

    def _build_ui(self):
        f = self.fonts["btn"]
        px = PANEL_X
        self.board_w = BoardWidget(BX, BY, CELL, BOARD_SIZE, self.fonts)

        # Depth buttons
        self._depth = 2
        self.depth_btns = []
        for i, (label, d) in enumerate(DEPTHS.items()):
            b = Button(px + i*68, 34, 64, 28, f"{label}(d{d})", f,
                       active=(d == self._depth))
            self.depth_btns.append((b, d))

        self.btn_new  = Button(px,       WIN_H-60, 120, 34, "New Game", f)
        self.btn_back = Button(px+130,   WIN_H-60, 100, 34, "← Menu",   f)

        # First/second mover selector
        self._human_first = True
        self.btn_you_first = Button(px,      112, 100, 28, "You First", f, active=True)
        self.btn_ai_first  = Button(px+108,  112, 100, 28, "AI First",  f, active=False)

        # Log
        self.log = MoveLog(0, WIN_H - LOG_H, WIN_W, LOG_H - 2, self.fonts)

        # Stats panel
        self.last_res = None
        self._turn_no = 0

    def _new_game(self):
        self.board = Board(BOARD_SIZE)
        self.board_w.clear_win_cells()
        self.board_w._place_anim.clear()
        self.winner = None
        self.win_cells = []
        self.current = HUMAN if self._human_first else AI
        self.state  = "playing"   # playing / thinking / win / draw
        if self.current == AI:
            self.state = "thinking"
            self._launch_ai()
        self.last_res = None
        self._turn_no = 0
        self.log.clear()

    #  Main API 
    def handle_event(self, ev) -> str | None:
        self.log.handle(ev)

        for b, d in self.depth_btns:
            if b.handle(ev):
                self._depth = d
                for b2, d2 in self.depth_btns:
                    b2.active = (d2 == d)

        if self.btn_new.handle(ev):
            self._new_game()
        if self.btn_back.handle(ev):
            return "menu"

        if self.btn_you_first.handle(ev):
            self._human_first = True
            self.btn_you_first.active = True
            self.btn_ai_first.active  = False
            self._new_game()
        if self.btn_ai_first.handle(ev):
            self._human_first = False
            self.btn_you_first.active = False
            self.btn_ai_first.active  = True
            self._new_game()

        if self.state == "playing" and self.current == HUMAN:
            cell = self.board_w.handle_event(ev)
            if cell:
                self._human_move(*cell)
        return None

    def update(self):
        self.board_w.update()
        if self.state == "thinking" and not hasattr(self, '_thread_alive'):
            pass   # handled via _ai_result

    def draw(self):
        self.screen.fill(C_BG)
        self.board_w.draw(self.screen, self.board.grid,
                          self.current, enabled=(self.state=="playing"))
        self._draw_panel()
        self.log.draw(self.screen)
        # status bar
        self._draw_status()

    # Internal 
    def _human_move(self, r, c):
        if not self.board.is_valid(r, c):
            return
        self._turn_no += 1
        self.board.place(r, c, HUMAN)
        self.board_w.trigger_anim(r, c, HUMAN)
        # log human move (no AI stats)
        self.log.add({"turn": self._turn_no, "player": HUMAN,
                      "move": (r+1, c+1), "value": "-",
                      "nodes": 0, "time": 0, "algo": "-"})
        if check_win(self.board.grid, r, c, HUMAN, BOARD_SIZE):
            self.winner = HUMAN
            self.win_cells = get_win_cells(self.board.grid, r, c, HUMAN, BOARD_SIZE)
            self.board_w.set_win_cells(self.win_cells)
            self.state = "win"
            return
        if is_draw(self.board.grid):
            self.state = "draw"; return
        self.current = AI
        self.state   = "thinking"
        self._launch_ai()

    def _launch_ai(self):
        grid_copy = self.board.grid.copy()
        depth     = self._depth

        def worker():
            ai  = Minimax(depth=depth, size=BOARD_SIZE)
            res = ai.get_move(grid_copy)
            self._ai_result = res

        self._ai_result = None
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        # poll in update loop
        self._poll_thread = t

    def update(self):
        self.board_w.update()
        if self.state == "thinking":
            if hasattr(self, '_poll_thread') and not self._poll_thread.is_alive():
                if self._ai_result is not None:
                    self._apply_ai(self._ai_result)
                    self._ai_result = None

    def _apply_ai(self, res):
        if res.move is None:
            self.state = "playing"; self.current = HUMAN; return
        r, c = res.move
        self._turn_no += 1
        self.board.place(r, c, AI)
        self.board_w.trigger_anim(r, c, AI)
        self.last_res = res
        self.log.add({"turn": self._turn_no, "player": AI,
                      "move": (r+1, c+1), "value": res.value,
                      "nodes": res.nodes, "time": res.elapsed,
                      "algo": "Minimax"})
        if check_win(self.board.grid, r, c, AI, BOARD_SIZE):
            self.winner = AI
            self.win_cells = get_win_cells(self.board.grid, r, c, AI, BOARD_SIZE)
            self.board_w.set_win_cells(self.win_cells)
            self.state = "win"; return
        if is_draw(self.board.grid):
            self.state = "draw"; return
        self.current = HUMAN
        self.state   = "playing"

    def _draw_panel(self):
        px = PANEL_X
        f  = self.fonts
        surf = self.screen

        pygame.draw.rect(surf, C_PANEL, (px-6, 0, PANEL_W+12, WIN_H - LOG_H))
        pygame.draw.line(surf, C_BORDER, (px-6, 0), (px-6, WIN_H - LOG_H))

        surf.blit(f["title"].render("MINIMAX", True, C_ACC), (px, 6))
        draw_label(surf, "Human vs Minimax (no pruning)", px, 36, f["small"])

        # Depth selector
        y = 68
        draw_label(surf, "Search Depth:", px, y, f["body"])
        for i, (b, _) in enumerate(self.depth_btns):
            b.move_to(px + i*68, y+18)
            b.draw(surf)
        y += 50

        draw_separator(surf, px, y, PANEL_W-10)
        y += 8
        draw_label(surf, "LAST AI MOVE", px, y, f["header"], C_ACC); y += 22
        r = self.last_res
        kv = [
            ("Algo",   r.algo if r else "-"),
            ("Depth",  str(r.depth if r else self._depth)),
            ("Move",   str(r.move) if r else "-"),
            ("Value",  str(r.value) if r else "-"),
            ("Nodes",  f"{r.nodes:,}" if r else "-"),
            ("Time",   f"{r.elapsed:.3f}s" if r else "-"),
        ]
        for k, v in kv:
            draw_label(surf, k+":", px, y, f["body"])
            surf.blit(f["body"].render(v, True, C_W), (px+80, y))
            y += 20

        # Board info
        y += 10
        draw_separator(surf, px, y, PANEL_W-10); y += 8
        draw_label(surf, "BOARD", px, y, f["header"], C_ACC); y += 22
        draw_label(surf, f"Moves:  {self.board.move_count}", px, y, f["body"]); y += 20
        draw_label(surf, f"Empty:  {BOARD_SIZE**2 - self.board.move_count}", px, y, f["body"]); y += 28

        # Lượt đi selector
        draw_separator(surf, px, y, PANEL_W-10); y += 8
        draw_label(surf, "Lượt đi:", px, y, f["body"]); y += 20
        self.btn_you_first.move_to(px,     y)
        self.btn_ai_first.move_to(px+108,  y)
        self.btn_you_first.draw(surf)
        self.btn_ai_first.draw(surf)

        # Buttons
        self.btn_new.move_to(px, WIN_H - LOG_H - 46)
        self.btn_back.move_to(px+130, WIN_H - LOG_H - 46)
        self.btn_new.draw(surf)
        self.btn_back.draw(surf)

    def _draw_status(self):
        surf = self.screen
        f    = self.fonts["header"]
        if self.state == "win":
            name = "HUMAN WINS! 🎉" if self.winner == HUMAN else "AI WINS!"
            col  = (70, 190, 255) if self.winner == HUMAN else (255, 85, 110)
            t = f.render(name, True, col)
            surf.blit(t, t.get_rect(center=(BX + (BOARD_SIZE-1)*CELL//2, BY - 38)))
        elif self.state == "draw":
            t = f.render("DRAW!", True, C_WARN)
            surf.blit(t, t.get_rect(center=(BX + (BOARD_SIZE-1)*CELL//2, BY - 38)))
        elif self.state == "thinking":
            t = f.render("AI THINKING…", True, C_WARN)
            surf.blit(t, t.get_rect(center=(BX + (BOARD_SIZE-1)*CELL//2, BY - 38)))
        else:
            turn = "YOUR TURN (X)" if self.current == HUMAN else "AI TURN (O)"
            col  = (70,190,255) if self.current == HUMAN else (255,85,110)
            t = f.render(turn, True, col)
            surf.blit(t, t.get_rect(center=(BX + (BOARD_SIZE-1)*CELL//2, BY - 38)))

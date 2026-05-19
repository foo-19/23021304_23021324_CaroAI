"""Screen 6 – Human vs Human (2 người chơi cùng máy)."""
from __future__ import annotations
import pygame
from config import (WIN_W, WIN_H, BOARD_SIZE, CELL, BX, BY,
                    HUMAN, AI, EMPTY, C_BG, C_ACC, C_W, C_DIM,
                    C_WARN, C_PANEL, C_BORDER, C_X, C_O)
from core.board import Board
from core.rules import check_win, get_win_cells, is_draw
from ui.board_widget import BoardWidget
from ui.common import Button, MoveLog, make_fonts, draw_label, draw_separator

# Đặt lại player 2 dùng constant AI (số 2) nhưng hiển thị là "Player 2"
P1 = HUMAN   # = 1
P2 = AI      # = 2  (dùng lại constant, chỉ là số)

PANEL_X = BX + BOARD_SIZE * CELL + 24
PANEL_W = WIN_W - PANEL_X - 10
LOG_H   = 195

PLAYER_NAME  = {P1: "Player 1 (X)", P2: "Player 2 (O)"}
PLAYER_COLOR = {P1: C_X,            P2: C_O}


class ScreenHvH:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.fonts  = make_fonts()
        self._build_ui()
        self._new_game()

    def _build_ui(self):
        f  = self.fonts["btn"]
        px = PANEL_X
        self.board_w = BoardWidget(BX, BY, CELL, BOARD_SIZE, self.fonts,
                                   interactive=True)
        self.btn_new  = Button(px,     WIN_H-LOG_H-46, 120, 34, "New Game", f)
        self.btn_back = Button(px+130, WIN_H-LOG_H-46, 100, 34, "← Menu",   f)
        self.log      = MoveLog(0, WIN_H-LOG_H, WIN_W, LOG_H-2, self.fonts)
        self._turn_no = 0

    def _new_game(self):
        self.board    = Board(BOARD_SIZE)
        self.board_w.clear_win_cells()
        self.board_w._place_anim.clear()
        self.winner   = None
        self.win_cells= []
        self.state    = "playing"   # playing / win / draw
        self.current  = P1
        self._turn_no = 0
        self.log.clear()
        self._scores  = {P1: 0, P2: 0}   # win tally across games

    def handle_event(self, ev) -> str | None:
        self.log.handle(ev)
        if self.btn_new.handle(ev):  self._new_game()
        if self.btn_back.handle(ev): return "menu"

        if self.state == "playing":
            cell = self.board_w.handle_event(ev)
            if cell:
                self._place(*cell)
        return None

    def update(self):
        self.board_w.update()

    def draw(self):
        self.screen.fill(C_BG)
        # Board: always interactive (both players click)
        self.board_w.draw(self.screen, self.board.grid,
                          self.current,
                          enabled=(self.state == "playing"))
        self._draw_panel()
        self.log.draw(self.screen)
        self._draw_status()

    #  Place move 
    def _place(self, r, c):
        if not self.board.is_valid(r, c):
            return
        player = self.current
        self._turn_no += 1
        self.board.place(r, c, player)
        self.board_w.trigger_anim(r, c, player)

        self.log.add({
            "turn":   self._turn_no,
            "player": player,
            "move":   (r+1, c+1),
            "value":  "—",
            "nodes":  0,
            "time":   0,
            "pname":  PLAYER_NAME[player],   # "Player 1 (X)" or "Player 2 (O)"
            "algo":   PLAYER_NAME[player],
        })

        if check_win(self.board.grid, r, c, player, BOARD_SIZE):
            self.winner    = player
            self.win_cells = get_win_cells(self.board.grid, r, c, player, BOARD_SIZE)
            self.board_w.set_win_cells(self.win_cells)
            self._scores[player] += 1
            self.state = "win"
            return

        if is_draw(self.board.grid):
            self.state = "draw"
            return

        # Switch player
        self.current = P2 if player == P1 else P1

    # ── Panel ─────────────────────────────────────────────────
    def _draw_panel(self):
        px = PANEL_X; f = self.fonts; surf = self.screen

        pygame.draw.rect(surf, C_PANEL, (px-6, 0, PANEL_W+12, WIN_H-LOG_H))
        pygame.draw.line(surf, C_BORDER, (px-6, 0), (px-6, WIN_H-LOG_H))

        # Title
        surf.blit(f["title"].render("HUMAN vs HUMAN", True, C_ACC), (px, 6))
        draw_label(surf, "2 người chơi luân phiên trên cùng máy", px, 36, f["small"])

        y = 62; draw_separator(surf, px, y, PANEL_W-10); y += 10

        # Current turn
        draw_label(surf, "LƯỢT HIỆN TẠI", px, y, f["header"], C_ACC); y += 22
        if self.state == "playing":
            name = PLAYER_NAME[self.current]
            col  = PLAYER_COLOR[self.current]
            sym  = "✕" if self.current == P1 else "○"
            t = f["body"].render(f"{sym}  {name}", True, col)
            surf.blit(t, (px, y)); y += 22
        elif self.state == "win":
            name = PLAYER_NAME[self.winner]
            col  = PLAYER_COLOR[self.winner]
            surf.blit(f["header"].render(f"🏆 {name} thắng!", True, col), (px, y)); y += 22
        else:
            surf.blit(f["header"].render("HÒA!", True, C_WARN), (px, y)); y += 22

        y += 6; draw_separator(surf, px, y, PANEL_W-10); y += 10

        # Scoreboard
        draw_label(surf, "BẢNG ĐIỂM", px, y, f["header"], C_ACC); y += 22
        for p in [P1, P2]:
            col  = PLAYER_COLOR[p]
            name = PLAYER_NAME[p]
            sc   = self._scores[p]
            draw_label(surf, name, px, y, f["body"], col)
            surf.blit(f["header"].render(str(sc), True, col), (px+160, y))
            y += 22

        y += 6; draw_separator(surf, px, y, PANEL_W-10); y += 10

        # Board info
        draw_label(surf, "BOARD", px, y, f["header"], C_ACC); y += 22
        draw_label(surf, f"Số nước: {self.board.move_count}", px, y, f["body"]); y += 20
        draw_label(surf, f"Còn trống: {BOARD_SIZE**2 - self.board.move_count}", px, y, f["body"]); y += 20

        y += 6; draw_separator(surf, px, y, PANEL_W-10); y += 10

        # Rules reminder
        draw_label(surf, "LUẬT CHƠI", px, y, f["header"], C_ACC); y += 20
        for line in ["• Bàn cờ 9×9",
                     "• Thắng: 4 quân liên tiếp",
                     "• Ngang / dọc / chéo",
                     "• Không xét luật chặn 2 đầu"]:
            draw_label(surf, line, px, y, f["small"]); y += 16

        # Buttons
        self.btn_new.move_to(px, WIN_H-LOG_H-46)
        self.btn_back.move_to(px+130, WIN_H-LOG_H-46)
        self.btn_new.draw(surf)
        self.btn_back.draw(surf)

    # Status bar 
    def _draw_status(self):
        f  = self.fonts["header"]
        cx = BX + (BOARD_SIZE-1)*CELL//2

        if self.state == "win":
            name = PLAYER_NAME[self.winner]
            col  = PLAYER_COLOR[self.winner]
            t = f.render(f"🏆 {name} thắng!", True, col)
        elif self.state == "draw":
            t = f.render("HÒA! Bàn cờ đầy.", True, C_WARN)
        else:
            name = PLAYER_NAME[self.current]
            col  = PLAYER_COLOR[self.current]
            sym  = "✕" if self.current == P1 else "○"
            t = f.render(f"Lượt: {sym} {name}", True, col)

        self.screen.blit(t, t.get_rect(center=(cx, BY-38)))

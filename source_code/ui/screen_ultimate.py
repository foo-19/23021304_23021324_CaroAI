"""Screen 4 – Ultimate: Best AI (AlphaBeta + Iterative Deepening + TT)."""
from __future__ import annotations
import threading, time
import pygame
from config import (WIN_W, WIN_H, BOARD_SIZE, CELL, BX, BY,
                    HUMAN, AI, DEPTHS, C_BG, C_ACC, C_W, C_WARN,
                    C_PANEL, C_BORDER, C_GOOD)
from core.board import Board
from core.rules import check_win, get_win_cells, is_draw
from core.moves import get_ordered_candidates
from ai.alphabeta import AlphaBeta
from ai.minimax import MoveResult
from ui.board_widget import BoardWidget
from ui.common import Button, MoveLog, make_fonts, draw_label, draw_separator


PANEL_X = BX + BOARD_SIZE * CELL + 24
PANEL_W = WIN_W - PANEL_X - 10
LOG_H   = 195


def _dynamic_depth(move_count):
    if move_count < 6:  return 2
    if move_count < 16: return 3
    return 4


class IterativeDeepeningAB:
    """AlphaBeta with iterative deepening + dynamic depth."""
    def __init__(self, max_depth=None, size=BOARD_SIZE):
        self.max_depth = max_depth
        self.size = size
        self.nodes = 0
        self.depth_used = 0

    def get_move(self, grid, move_count=0) -> MoveResult:
        t0 = time.perf_counter()
        max_d = self.max_depth or _dynamic_depth(move_count)
        best_move = None; best_val = -10**9
        total_nodes = 0; depth_used = 1

        ab = AlphaBeta(size=self.size, use_tt=True)
        for d in range(1, max_d+1):
            ab.depth = d
            res = ab.get_move(grid.copy(), clear_tt=False)
            total_nodes += res.nodes
            if res.move:
                best_move = res.move; best_val = res.value; depth_used = d

        elapsed = time.perf_counter() - t0
        return MoveResult(best_move, best_val, total_nodes,
                          depth_used, elapsed, f"AB+ID(d{depth_used})")


class ScreenUltimate:
    def __init__(self, screen):
        self.screen = screen
        self.fonts  = make_fonts()
        self._build_ui()
        self._new_game()

    def _build_ui(self):
        f  = self.fonts["btn"]
        px = PANEL_X
        self.board_w = BoardWidget(BX, BY, CELL, BOARD_SIZE, self.fonts)
        self.btn_new  = Button(px,     WIN_H-LOG_H-46, 120, 34, "New Game", f)
        self.btn_back = Button(px+130, WIN_H-LOG_H-46, 100, 34, "← Menu",   f)

        # First/second mover selector
        self._human_first = True
        self.btn_you_first = Button(px,     112, 100, 28, "You First", f, active=True)
        self.btn_ai_first  = Button(px+108, 112, 100, 28, "AI First",  f, active=False)
        self.log      = MoveLog(0, WIN_H-LOG_H, WIN_W, LOG_H-2, self.fonts)
        self.last_res = None; self._turn_no = 0

    def _new_game(self):
        self.board = Board(BOARD_SIZE)
        self.board_w.clear_win_cells(); self.board_w._place_anim.clear()
        self.winner=None; self.state="playing"; self.current=HUMAN if self._human_first else AI
        self.last_res=None; self._turn_no=0
        self._ai_result=None; self._poll_thread=None
        self.log.clear()
        if self.current == AI:
            self.state = "thinking"
            self._launch_ai()

    def handle_event(self, ev):
        self.log.handle(ev)
        if self.btn_new.handle(ev):  self._new_game()
        if self.btn_back.handle(ev): return "menu"
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
        if self.state=="playing" and self.current==HUMAN:
            cell = self.board_w.handle_event(ev)
            if cell: self._human_move(*cell)
        return None

    def update(self):
        self.board_w.update()
        if self.state=="thinking":
            if self._poll_thread and not self._poll_thread.is_alive():
                if self._ai_result:
                    self._apply_ai(self._ai_result); self._ai_result=None

    def draw(self):
        self.screen.fill(C_BG)
        self.board_w.draw(self.screen, self.board.grid, self.current,
                          enabled=(self.state=="playing"))
        self._draw_panel()
        self.log.draw(self.screen)
        self._draw_status()

    def _human_move(self, r, c):
        if not self.board.is_valid(r, c): return
        self._turn_no += 1
        self.board.place(r, c, HUMAN)
        self.board_w.trigger_anim(r, c, HUMAN)
        self.log.add({"turn":self._turn_no,"player":HUMAN,
                      "move":(r+1,c+1),"value":"-","nodes":0,"time":0,"algo":"-"})
        if check_win(self.board.grid,r,c,HUMAN,BOARD_SIZE):
            self.winner=HUMAN
            self.board_w.set_win_cells(get_win_cells(self.board.grid,r,c,HUMAN,BOARD_SIZE))
            self.state="win"; return
        if is_draw(self.board.grid): self.state="draw"; return
        self.current=AI; self.state="thinking"; self._launch_ai()

    def _launch_ai(self):
        grid_copy = self.board.grid.copy()
        mc        = self.board.move_count
        def worker():
            ai = IterativeDeepeningAB(size=BOARD_SIZE)
            self._ai_result = ai.get_move(grid_copy, mc)
        self._ai_result=None
        self._poll_thread = threading.Thread(target=worker, daemon=True)
        self._poll_thread.start()

    def _apply_ai(self, res):
        if not res.move: self.state="playing"; self.current=HUMAN; return
        r,c = res.move
        self._turn_no += 1
        self.board.place(r,c,AI); self.board_w.trigger_anim(r,c,AI)
        self.last_res = res
        self.log.add({"turn":self._turn_no,"player":AI,
                      "move":(r+1,c+1),"value":res.value,
                      "nodes":res.nodes,"time":res.elapsed,"algo":res.algo})
        if check_win(self.board.grid,r,c,AI,BOARD_SIZE):
            self.winner=AI
            self.board_w.set_win_cells(get_win_cells(self.board.grid,r,c,AI,BOARD_SIZE))
            self.state="win"; return
        if is_draw(self.board.grid): self.state="draw"; return
        self.current=HUMAN; self.state="playing"

    def _draw_panel(self):
        px=PANEL_X; f=self.fonts; surf=self.screen
        pygame.draw.rect(surf,C_PANEL,(px-6,0,PANEL_W+12,WIN_H-LOG_H))
        pygame.draw.line(surf,C_BORDER,(px-6,0),(px-6,WIN_H-LOG_H))
        surf.blit(f["title"].render("ULTIMATE AI",True,C_ACC),(px,6))
        draw_label(surf,"AlphaBeta + Iterative Deepening + TT",px,36,f["small"])

        y=68; draw_separator(surf,px,y,PANEL_W-10); y+=8
        draw_label(surf,"AI MODE",px,y,f["header"],C_ACC); y+=20
        draw_label(surf,"Algorithm: AlphaBeta+ID+TT",px,y,f["body"]); y+=18
        draw_label(surf,"Depth:     Dynamic (2→4)",  px,y,f["body"]); y+=18
        draw_label(surf,"Pruning:   Alpha-Beta",      px,y,f["body"]); y+=18
        draw_label(surf,"TT:        Enabled",         px,y,f["body"]); y+=18

        y+=4; draw_separator(surf,px,y,PANEL_W-10); y+=8
        draw_label(surf,"LAST AI MOVE",px,y,f["header"],C_ACC); y+=22
        r=self.last_res
        for k,v in [("Algo",  r.algo if r else "-"),
                    ("Depth", str(r.depth if r else "-")),
                    ("Move",  str(r.move) if r else "-"),
                    ("Value", str(r.value) if r else "-"),
                    ("Nodes", f"{r.nodes:,}" if r else "-"),
                    ("Time",  f"{r.elapsed:.3f}s" if r else "-")]:
            draw_label(surf,k+":",px,y,f["body"])
            surf.blit(f["body"].render(v,True,C_W),(px+80,y)); y+=20

        y+=4; draw_separator(surf,px,y,PANEL_W-10); y+=8
        draw_label(surf,"BOARD",px,y,f["header"],C_ACC); y+=22
        draw_label(surf,f"Moves:  {self.board.move_count}",px,y,f["body"]); y+=20
        draw_label(surf,f"Empty:  {BOARD_SIZE**2-self.board.move_count}",px,y,f["body"]); y+=28

        # Lượt đi selector
        draw_separator(surf,px,y,PANEL_W-10); y+=8
        draw_label(surf,"Lượt đi:",px,y,f["body"]); y+=20
        self.btn_you_first.move_to(px,     y)
        self.btn_ai_first.move_to(px+108,  y)
        self.btn_you_first.draw(surf)
        self.btn_ai_first.draw(surf)

        self.btn_new.draw(surf); self.btn_back.draw(surf)

    def _draw_status(self):
        f=self.fonts["header"]
        cx=BX+(BOARD_SIZE-1)*CELL//2
        if self.state=="win":
            name="HUMAN WINS! 🎉" if self.winner==HUMAN else "AI WINS!"
            col=(70,190,255) if self.winner==HUMAN else (255,85,110)
            t=f.render(name,True,col)
        elif self.state=="draw":   t=f.render("DRAW!",True,C_WARN)
        elif self.state=="thinking":t=f.render("ULTIMATE AI THINKING…",True,C_WARN)
        else:
            turn="YOUR TURN (X)" if self.current==HUMAN else "AI TURN (O)"
            col=(70,190,255) if self.current==HUMAN else (255,85,110)
            t=f.render(turn,True,col)
        self.screen.blit(t,t.get_rect(center=(cx,BY-38)))

"""Screen 3 – Side-by-side comparison: Minimax (left) vs AlphaBeta (right).
Both boards mirror the SAME game. Each AI computes independently and we
show their stats side-by-side. The human plays on the LEFT board; moves
are mirrored to the right."""
from __future__ import annotations
import threading
import pygame
from config import (WIN_W, WIN_H, BOARD_SIZE, CELL, HUMAN, AI, DEPTHS,
                    C_BG, C_ACC, C_W, C_DIM, C_WARN, C_GOOD, C_BAD,
                    C_PANEL, C_BORDER, C_X, C_O)
from core.board import Board
from core.rules import check_win, get_win_cells, is_draw
from ai.minimax  import Minimax
from ai.alphabeta import AlphaBeta
from ui.board_widget import BoardWidget
from ui.common import Button, MoveLog, make_fonts, draw_label, draw_separator

# ── Layout constants ──────────────────────────────────────────
SMALL_CELL = 28          # smaller cells to fit 2 boards
LEFT_BX    = 10
RIGHT_BX   = LEFT_BX + BOARD_SIZE * SMALL_CELL + 30
MID_X      = RIGHT_BX + BOARD_SIZE * SMALL_CELL + 14
PANEL_W    = WIN_W - MID_X - 6
BY2        = 55
LOG_H      = 155


class ScreenCompare:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.fonts  = make_fonts()
        self._build_ui()
        self._new_game()

    def _build_ui(self):
        f = self.fonts["btn"]
        self.bw_left  = BoardWidget(LEFT_BX,  BY2, SMALL_CELL, BOARD_SIZE, self.fonts)
        self.bw_right = BoardWidget(RIGHT_BX,  BY2, SMALL_CELL, BOARD_SIZE, self.fonts, interactive=False)

        self._depth = 2
        self.depth_btns = []
        for i, (label, d) in enumerate(DEPTHS.items()):
            b = Button(MID_X + i*70, 30, 66, 26, f"{label}(d{d})", f, active=(d==self._depth))
            self.depth_btns.append((b, d))

        self.btn_new  = Button(MID_X,      WIN_H-LOG_H-46, 120, 32, "New Game", f)
        self.btn_back = Button(MID_X+130,  WIN_H-LOG_H-46, 100, 32, "← Menu",   f)

        # Two separate logs
        half = WIN_W // 2
        self.log_mm = MoveLog(0,    WIN_H-LOG_H, half-2,   LOG_H-2, self.fonts)
        self.log_ab = MoveLog(half, WIN_H-LOG_H, WIN_W-half, LOG_H-2, self.fonts)

        self.res_mm = None; self.res_ab = None
        self._turn_no = 0

    def _new_game(self):
        self.board = Board(BOARD_SIZE)
        for bw in (self.bw_left, self.bw_right):
            bw.clear_win_cells(); bw._place_anim.clear()
        self.winner   = None
        self.state    = "playing"
        self.current  = HUMAN
        self.res_mm   = None; self.res_ab = None
        self._turn_no = 0
        self._mm_result = None; self._ab_result = None
        self._mm_thread = None; self._ab_thread  = None
        self.log_mm.clear(); self.log_ab.clear()

    def handle_event(self, ev) -> str | None:
        self.log_mm.handle(ev)
        self.log_ab.handle(ev)
        for b, d in self.depth_btns:
            if b.handle(ev):
                self._depth = d
                for b2, d2 in self.depth_btns: b2.active = (d2==d)
        if self.btn_new.handle(ev):  self._new_game()
        if self.btn_back.handle(ev): return "menu"
        if self.state == "playing" and self.current == HUMAN:
            cell = self.bw_left.handle_event(ev)
            if cell: self._human_move(*cell)
        return None

    def update(self):
        self.bw_left.update(); self.bw_right.update()
        if self.state == "thinking":
            if hasattr(self, '_worker_thread') and self._worker_thread and not self._worker_thread.is_alive():
                self._apply_ai_results()

    def draw(self):
        self.screen.fill(C_BG)
        # Column headers
        f = self.fonts["header"]
        self.screen.blit(f.render("MINIMAX", True, C_ACC),
                         (LEFT_BX + (BOARD_SIZE*SMALL_CELL)//2 - 40, 8))
        self.screen.blit(f.render("ALPHA-BETA", True, (255,85,110)),
                         (RIGHT_BX + (BOARD_SIZE*SMALL_CELL)//2 - 55, 8))

        # Boards
        self.bw_left.draw(self.screen, self.board.grid, self.current,
                          enabled=(self.state=="playing"))
        self.bw_right.draw(self.screen, self.board.grid, None, enabled=False)

        # Centre divider
        mx = RIGHT_BX + BOARD_SIZE*SMALL_CELL + 10
        pygame.draw.line(self.screen, C_BORDER, (mx,0),(mx,WIN_H-LOG_H))

        self._draw_panel()
        self._draw_log_headers()
        self.log_mm.draw(self.screen)
        self.log_ab.draw(self.screen)
        self._draw_status()

    def _human_move(self, r, c):
        if not self.board.is_valid(r, c): return
        self._turn_no += 1
        self.board.place(r, c, HUMAN)
        for bw in (self.bw_left, self.bw_right):
            bw.trigger_anim(r, c, HUMAN)
        entry = {"turn": self._turn_no, "player": HUMAN,
                 "move": (r+1,c+1), "value":"-","nodes":0,"time":0,"algo":"-"}
        self.log_mm.add(dict(entry)); self.log_ab.add(dict(entry))
        if check_win(self.board.grid, r, c, HUMAN, BOARD_SIZE):
            self.winner = HUMAN
            wc = get_win_cells(self.board.grid,r,c,HUMAN,BOARD_SIZE)
            for bw in (self.bw_left, self.bw_right): bw.set_win_cells(wc)
            self.state = "win"; return
        if is_draw(self.board.grid): self.state="draw"; return
        self.current = AI; self.state = "thinking"
        self._launch_both()

    def _launch_both(self):
        grid_copy = self.board.grid.copy()
        d = self._depth
        self._mm_result = None; self._ab_result = None

        def worker():
            # Chạy tuần tự để tránh Python GIL làm sai lệch kết quả đo thời gian
            self._mm_result = Minimax(depth=d).get_move(grid_copy.copy())
            self._ab_result = AlphaBeta(depth=d, use_tt=False).get_move(grid_copy.copy())

        self._worker_thread = threading.Thread(target=worker, daemon=True)
        self._worker_thread.start()

    def _apply_ai_results(self):
        """Both done – apply the AlphaBeta move (canonical), show both stats."""
        mm = self._mm_result; ab = self._ab_result
        # Use AlphaBeta's chosen move as the game move
        move = ab.move if (ab and ab.move) else (mm.move if mm else None)
        if move is None: self.state="playing"; self.current=HUMAN; return

        r, c = move
        self._turn_no += 1
        self.board.place(r, c, AI)
        for bw in (self.bw_left, self.bw_right): bw.trigger_anim(r, c, AI)

        self.res_mm = mm; self.res_ab = ab

        # Log to respective columns
        if mm:
            self.log_mm.add({"turn":self._turn_no,"player":AI,
                             "move":(r+1,c+1),"value":mm.value,
                             "nodes":mm.nodes,"time":mm.elapsed,"algo":"Minimax"})
        if ab:
            self.log_ab.add({"turn":self._turn_no,"player":AI,
                             "move":(r+1,c+1),"value":ab.value,
                             "nodes":ab.nodes,"time":ab.elapsed,"algo":"AlphaBeta"})

        if check_win(self.board.grid, r, c, AI, BOARD_SIZE):
            self.winner = AI
            wc = get_win_cells(self.board.grid,r,c,AI,BOARD_SIZE)
            for bw in (self.bw_left, self.bw_right): bw.set_win_cells(wc)
            self.state="win"; return
        if is_draw(self.board.grid): self.state="draw"; return
        self.current=HUMAN; self.state="playing"

    def _draw_panel(self):
        px = MID_X; f = self.fonts; surf = self.screen
        pygame.draw.rect(surf, C_PANEL, (px, 0, PANEL_W, WIN_H-LOG_H))
        pygame.draw.line(surf, C_BORDER, (px,0),(px, WIN_H-LOG_H))
        surf.blit(f["header"].render("COMPARISON", True, C_ACC), (px+8, 6))

        # Depth
        y=32
        for i,(b,_) in enumerate(self.depth_btns): b.move_to(px+8+i*70, y); b.draw(surf)
        y=70; draw_separator(surf,px+4,y,PANEL_W-8); y+=6

        # Stats comparison table
        draw_label(surf,"           Minimax   AlphaBeta",px+4,y,f["body"],C_DIM); y+=18
        mm=self.res_mm; ab=self.res_ab
        def row(label, v1, v2, good="low"):
            nonlocal y
            draw_label(surf, label, px+4, y, f["body"]); 
            surf.blit(f["body"].render(str(v1), True, C_W), (px+100,y))
            # color the AB value
            try:
                n1=float(str(v1).replace(",","").replace("s",""))
                n2=float(str(v2).replace(",","").replace("s",""))
                col = C_GOOD if (n2<n1 if good=="low" else n2>n1) else C_BAD
            except: col=C_W
            surf.blit(f["body"].render(str(v2), True, col), (px+195,y))
            y+=18

        row("Nodes:", f"{mm.nodes:,}" if mm else "-",
                      f"{ab.nodes:,}" if ab else "-", "low")
        row("Time: ", f"{mm.elapsed:.3f}s" if mm else "-",
                      f"{ab.elapsed:.3f}s" if ab else "-", "low")
        row("Value:", str(mm.value) if mm else "-",
                      str(ab.value) if ab else "-", "high")
        row("Move: ", str(mm.move) if mm else "-",
                      str(ab.move) if ab else "-", "")

        if mm and ab and mm.nodes>0:
            red = (mm.nodes-ab.nodes)/mm.nodes*100
            y+=4
            draw_label(surf,"Reduction:", px+4, y, f["body"])
            surf.blit(f["header"].render(f"{red:.1f}%", True, C_GOOD),(px+100,y))
            y+=20

        # same-move indicator
        if mm and ab:
            same = (mm.move == ab.move)
            col  = C_GOOD if same else C_WARN
            msg  = " Same move" if same else " Different move"
            draw_label(surf, msg, px+4, y, f["body"], col)

        self.btn_new.draw(surf); self.btn_back.draw(surf)

    def _draw_log_headers(self):
        f    = self.fonts["small"]
        half = WIN_W//2
        self.screen.blit(f.render(" Minimax Move Log", True, C_ACC),
                         (4, WIN_H-LOG_H-16))
        self.screen.blit(f.render(" AlphaBeta Move Log", True, (255,85,110)),
                         (half+4, WIN_H-LOG_H-16))

    def _draw_status(self):
        f  = self.fonts["header"]
        cx = LEFT_BX + (BOARD_SIZE*SMALL_CELL)//2
        if self.state=="win":
            name = "HUMAN WINS! " if self.winner==HUMAN else "AI WINS!"
            col  = C_X if self.winner==HUMAN else C_O
            t=f.render(name,True,col)
        elif self.state=="draw":
            t=f.render("DRAW!",True,C_WARN)
        elif self.state=="thinking":
            t=f.render("BOTH AIs THINKING…",True,C_WARN)
        else:
            turn="YOUR TURN (X)" if self.current==HUMAN else "AI TURN (O)"
            col=C_X if self.current==HUMAN else C_O
            t=f.render(turn,True,col)
        self.screen.blit(t, t.get_rect(center=(cx, BY2-28)))

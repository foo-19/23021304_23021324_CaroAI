"""Main menu screen."""
from __future__ import annotations
import math, pygame
from config import WIN_W, WIN_H, C_BG, C_ACC, C_DIM, C_W, C_BORDER
from ui.common import Button, make_fonts

MENU_ITEMS = [
    ("menu_hvh",       "0.  Human vs Human",            "2 người chơi luân phiên trên cùng máy"),
    ("menu_minimax",   "1.  Human vs Minimax",           "Human vs Minimax thuần (không cắt nhánh)"),
    ("menu_alphabeta", "2.  Human vs AlphaBeta",         "Human vs Minimax + Alpha-Beta pruning"),
    ("menu_compare",   "3.  So sánh song song",          "Cả 2 AI tính cùng lúc – thấy rõ sự khác biệt"),
    ("menu_ultimate",  "4.  Ultimate AI (mạnh nhất)",    "AlphaBeta + Iterative Deepening + TT"),
]


class ScreenMenu:
    def __init__(self, screen):
        self.screen = screen
        self.fonts  = make_fonts()
        self._tick  = 0
        f  = self.fonts["btn"]
        fs = self.fonts["small"]
        bx = WIN_W//2 - 220
        self.buttons = []
        for i, (action, label, _) in enumerate(MENU_ITEMS):
            b = Button(bx, 195 + i*66, 440, 48, label, f)
            self.buttons.append((b, action))
        self.btn_exit = Button(bx+340, 195+len(MENU_ITEMS)*66+8, 100, 34, "Exit", f)

    def handle_event(self, ev) -> str | None:
        for b, action in self.buttons:
            if b.handle(ev): return action
        if self.btn_exit.handle(ev): return "exit"
        return None

    def update(self): self._tick += 1

    def draw(self):
        self.screen.fill(C_BG)
        self._draw_bg()
        f = self.fonts
        # Title
        t = f["big"].render("CARO  AI", True, C_ACC)
        self.screen.blit(t, t.get_rect(center=(WIN_W//2, 90)))
        t2 = f["body"].render(
            "Minimax  ·  Alpha-Beta Pruning  ·  Iterative Deepening  ·  Transposition Table",
            True, C_DIM)
        self.screen.blit(t2, t2.get_rect(center=(WIN_W//2, 138)))
        t3 = f["small"].render(
            "Thắng: 4 quân liên tiếp  |  Bàn cờ: 15×15  |  Không luật chặn 2 đầu",
            True, C_DIM)
        self.screen.blit(t3, t3.get_rect(center=(WIN_W//2, 160)))

        for i, ((b, _), (_, label, desc)) in enumerate(zip(self.buttons, MENU_ITEMS)):
            b.draw(self.screen)
            d = f["small"].render(desc, True, C_DIM)
            self.screen.blit(d, (b.rect.x+10, b.rect.bottom+2))

        self.btn_exit.draw(self.screen)

        ft = f["small"].render(
            "AlphaBeta giảm trung bình 95% số node so với Minimax  |  "
            "Tie-breaking: cùng điểm → ưu tiên ô gần trung tâm",
            True, C_DIM)
        self.screen.blit(ft, ft.get_rect(center=(WIN_W//2, WIN_H-12)))

    def _draw_bg(self):
        import random
        rng = random.Random(7)
        for _ in range(50):
            x=rng.randint(0,WIN_W); y=rng.randint(0,WIN_H); r=rng.randint(1,2)
            a=int(22+18*math.sin(self._tick*0.03+x*0.01))
            s=pygame.Surface((r*2,r*2),pygame.SRCALPHA)
            pygame.draw.circle(s,(90,200,255,a),(r,r),r)
            self.screen.blit(s,(x-r,y-r))

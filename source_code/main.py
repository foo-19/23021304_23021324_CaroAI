#!/usr/bin/env python3
"""
Caro AI – Main Entry Point
==========================
WIN = 4 quân liên tiếp  |  Bàn cờ 9×9

Màn hình:
  0. Human vs Human        – 2 người chơi cùng máy
  1. Minimax Only          – Human vs Minimax thuần
  2. Human vs AlphaBeta    – Human vs AB pruning
  3. Side-by-Side          – So sánh 2 thuật toán song song
  4. Ultimate AI           – AB + ID + TT
"""
import sys
import pygame

from config import WIN_W, WIN_H, FPS

from ui.screen_menu      import ScreenMenu
from ui.screen_hvh       import ScreenHvH
from ui.screen_minimax   import ScreenMinimax
from ui.screen_alphabeta import ScreenAlphaBeta
from ui.screen_compare   import ScreenCompare
from ui.screen_ultimate  import ScreenUltimate


def main():
    pygame.init()
    pygame.display.set_caption("Caro AI  |  Win=4  |  Minimax · AlphaBeta · ID · TT")
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    clock  = pygame.time.Clock()

    screens = {}
    current = "menu"

    FACTORIES = {
        "menu":      lambda: ScreenMenu(screen),
        "hvh":       lambda: ScreenHvH(screen),
        "minimax":   lambda: ScreenMinimax(screen),
        "alphabeta": lambda: ScreenAlphaBeta(screen),
        "compare":   lambda: ScreenCompare(screen),
        "ultimate":  lambda: ScreenUltimate(screen),
    }

    def get(name):
        if name not in screens:
            screens[name] = FACTORIES[name]()
        return screens[name]

    while True:
        scr = get(current)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            action = scr.handle_event(ev)

            if action == "exit":
                pygame.quit(); sys.exit()
            elif action == "menu":
                current = "menu"
            elif action in ("menu_hvh", "menu_minimax", "menu_alphabeta",
                            "menu_compare", "menu_ultimate"):
                key = action.replace("menu_", "")
                screens[key] = FACTORIES[key]()   # fresh instance each time
                current = key

        scr.update()
        scr.draw()
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()

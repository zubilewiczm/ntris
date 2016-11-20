#!usr/bin/env/python

import pygame
from pygame.locals import *

from blocks import Block
from game import TestGame

SCR_WIDTH = 360
SCR_HEIGHT = 540
FPS = 60

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCR_WIDTH, SCR_HEIGHT))
    pygame.display.set_caption("ntris")
    
    clock  = pygame.time.Clock()
    game   = TestGame(screen)
    
    going = True
    while going:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == QUIT:
                going = False
            else:
                game.event(event)
        game.tick()
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()

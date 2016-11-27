#!usr/bin/env/python
import itertools

import pygame
from pygame.locals import *

import blocks as blk
from game import nTris
import nmino

SCR_WIDTH = 420
SCR_HEIGHT = 540
FPS = 60

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCR_WIDTH, SCR_HEIGHT))
    pygame.display.set_caption("ntris")
    
    clock  = pygame.time.Clock()
    game   = nTris(screen)
    
    going = True
    while going:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == QUIT:
                going = False
            else:
                game.event(event)
        game.tick(dt)
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()
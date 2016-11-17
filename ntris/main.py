#!usr/bin/env/python

import pygame
from pygame.locals import *

SCR_WIDTH = 360
SCR_HEIGHT = 540
FPS = 60

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCR_WIDTH, SCR_HEIGHT))
    pygame.display.set_caption("ntris")
    
    clock = pygame.time.Clock()
    going = True
    while going:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == QUIT:
                going = False
    
    pygame.quit()

if __name__ == "__main__":
    main()

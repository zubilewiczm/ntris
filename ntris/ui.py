import pygame
import utils

class Area:
    
    BD_COL  = [255,255,255]
    BD_COL2 = [x//2 for x in BD_COL]

    def __init__(self, rect):
        self.rect = rect
    
    def draw(self, screen):
        temprect = utils.rect_inflate(self.rect, 2, 2)
        pygame.draw.rect(screen, Area.BD_COL2, temprect, 1)
        temprect = utils.rect_inflate(temprect, -1, -1)
        pygame.draw.rect(screen, Area.BD_COL, temprect, 1)

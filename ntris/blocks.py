import pygame

class Block(pygame.sprite.Sprite):
    size = 16
    looks = pygame.Surface((size, size))
    looks.fill((255,255,255))

    def __init__(self, pos, speed):
        pygame.sprite.Sprite.__init__(self)
        self.x, self.y = pos
        self.rect = pygame.Rect((0,0,Block.size,Block.size))
        self._update_rect()
        self.image = Block.looks
        self.speed = speed
    
    def update(self, *args):
        self.y+= self.speed/60
        self._update_rect()
    
    def _update_rect(self):
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
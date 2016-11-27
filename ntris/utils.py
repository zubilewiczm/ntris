import pygame

def noop(*args, **kwargs):
    pass

def not_implemented(*args, **kwargs):
    raise NotImplementedError()

def rect_inflate(rect, x,y):
    return pygame.Rect(rect.left-x,rect.top-y,rect.width+2*x,rect.height+2*y)

def hsv(i,n, s,v):
    h = 360*i/n
    c = pygame.Color(255)
    c.hsva = h,s,v
    c.a = 255
    return c
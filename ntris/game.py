from collections import deque
import pygame
from pygame.locals import *

from blocks import Block
from utils import noop, not_implemented

class Game:

    def __init__(self, screen):
        self.event_queue = deque()
        self.screen = screen
        
    def tick(self):
        while self.event_queue:
            evt = self.event_queue.pop()
            self.process_event(evt)
        self.update()
        self.draw(self.screen)
    
    update = noop
    draw   = noop
        
    def process_event(self, evt):
        evt_types = {
            ACTIVEEVENT      :
                lambda evt: self.evt_focus(evt.gain, evt.state),
            KEYDOWN          :
                lambda evt: self.evt_keydown(evt.unicode, evt.key, evt.mod),
            KEYUP            :
                lambda evt: self.evt_keyup(evt.key, evt.mod),
            MOUSEMOTION      :
                lambda evt: self.evt_mousemove(evt.pos, evt.rel, evt.buttons),
            MOUSEBUTTONUP    :
                lambda evt: self.evt_mouseup(evt.pos, evt.button),
            MOUSEBUTTONDOWN  :
                lambda evt: self.evt_mousedown(evt.pos, evt.button)
        }
        return evt_types.get(evt.type, noop)(evt)
    
    evt_focus     = noop
    evt_keydown   = noop
    evt_keyup     = noop
    evt_mousemove = noop
    evt_mouseup   = noop
    evt_mousedown = noop
        
    def event(self, event):
        self.event_queue.appendleft(event)
    

class TestGame(Game):
    
    def __init__(self, screen):
        super().__init__(screen)
        self.block = Block((100,0), 20)
        self.bg = pygame.Surface(screen.get_size())
        self.bg.fill((0,0,0))
    
    def update(self):
        self.block.update()
        
    def draw(self, screen):
        self.screen.blit(self.bg, (0,0))
        self.screen.blit(self.block.image, self.block.rect.topleft)
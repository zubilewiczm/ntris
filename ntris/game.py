from collections import deque
import pygame
from pygame.locals import *

import stage
import nmino
import nminoctl
from utils import noop, not_implemented

from enum import Enum

class Game:

    def __init__(self, screen):
        self.screen = screen
        self.keymap = dict() # key -> message
        self.msgmap = dict() # msg -> callback
        self.writing = False
        
    def tick(self, dt):
        self.update(dt)
        self.draw(self.screen)
    
    update = not_implemented
    draw   = not_implemented
        
    def event(self, evt):
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
    
    def evt_keydown(self, unicode, key, mod):
        if not self.writing:
            msg = self.keymap.get(key, None)
            if msg:
                return self.msgmap[msg](True)
        else:
            pass # TODO!
            
    def evt_keyup(self, key, mod):
        msg = self.keymap.get(key, None)
        if msg:
            return self.msgmap[msg](False)
        
    evt_focus     = noop
    evt_mousemove = noop
    evt_mouseup   = noop
    evt_mousedown = noop
    

class nTrisMsg(Enum):
    P1_MOVE_LEFT  = 0,
    P1_MOVE_RIGHT = 1,
    P1_MOVE_DOWN  = 2,
    P1_ROT_CW     = 3,
    P1_ROT_CCW    = 4,
    P2_MOVE_LEFT  = 5,
    P2_MOVE_RIGHT = 6,
    P2_MOVE_DOWN  = 7,
    P2_ROT_CW     = 8,
    P2_ROT_CCW    = 9,
    PAUSE         = 10,
    QUIT          = 11,
    ACCEPT        = 12,
    DOWN          = 13,
    UP            = 14,
    RIGHT         = 15,
    LEFT          = 16

class nTrisPlayer:

    def __init__(self):
        self.points = 0
        self.lastmoves = []
        self.nmc = None
        self.movetimer = 0.0
        self.gameover = False
        self.repeat_timer = 0.0
        self.repeat_thold = 1000.0
    
    def lastmove(self):
        return self.lastmoves[-1] if self.lastmoves else None
    
    def move(self, dn, dir):
        if self.nmc:
            if dn:
                try:
                    self.lastmoves.remove(dir)
                except ValueError:
                    pass
                self.lastmoves.append(dir)
                return self.nmc.move(dir)
            else:
                try:
                    self.lastmoves.remove(dir)
                except ValueError:
                    pass
                return True
        else:
            return False
        
    def rot(self, spin):
        if self.nmc:
            return self.nmc.rotate(spin)
        return False
    
class nTris(Game):
                         
    def __init__(self, screen):
        super().__init__(screen)
        self.bg = pygame.Surface(screen.get_size())
        self.bg.fill((0,0,0))
        self.init_msgs()
        self.init_game_keymap()
        self.init_game()
    
    def init_msgs(self):
        self.msgmap[nTrisMsg.P1_MOVE_LEFT]  = lambda dn : self.move(0, dn, nminoctl.Dir.LEFT)
        self.msgmap[nTrisMsg.P1_MOVE_RIGHT] = lambda dn : self.move(0, dn, nminoctl.Dir.RIGHT)
        self.msgmap[nTrisMsg.P1_MOVE_DOWN]  = lambda dn : self.move(0, dn, nminoctl.Dir.DOWN)
        self.msgmap[nTrisMsg.P1_ROT_CW]     = lambda dn : self.rot(0, dn, nminoctl.Spin.CLOCKWISE)
        self.msgmap[nTrisMsg.P1_ROT_CCW]    = lambda dn : self.rot(0, dn, nminoctl.Spin.COUNTERCLOCKWISE)
        self.msgmap[nTrisMsg.P2_MOVE_LEFT]  = lambda dn : self.move(1, dn, nminoctl.Dir.LEFT)
        self.msgmap[nTrisMsg.P2_MOVE_RIGHT] = lambda dn : self.move(1, dn, nminoctl.Dir.RIGHT)
        self.msgmap[nTrisMsg.P2_MOVE_DOWN]  = lambda dn : self.move(1, dn, nminoctl.Dir.DOWN)
        self.msgmap[nTrisMsg.P2_ROT_CW]     = lambda dn : self.rot(1, dn, nminoctl.Spin.CLOCKWISE)
        self.msgmap[nTrisMsg.P2_ROT_CCW]    = lambda dn : self.rot(1, dn, nminoctl.Spin.COUNTERCLOCKWISE)
        self.msgmap[nTrisMsg.PAUSE]  = lambda dn : None
        self.msgmap[nTrisMsg.QUIT]   = lambda dn : None
        self.msgmap[nTrisMsg.ACCEPT] = lambda dn : None
        self.msgmap[nTrisMsg.DOWN]   = lambda dn : None
        self.msgmap[nTrisMsg.UP]     = lambda dn : None
        self.msgmap[nTrisMsg.RIGHT]  = lambda dn : None
        self.msgmap[nTrisMsg.LEFT]   = lambda dn : None
    
    def init_game_keymap(self):
        self.keymap[K_a]      = nTrisMsg.P1_MOVE_LEFT
        self.keymap[K_d]      = nTrisMsg.P1_MOVE_RIGHT
        self.keymap[K_s]      = nTrisMsg.P1_MOVE_DOWN
        self.keymap[K_v]      = nTrisMsg.P1_ROT_CCW
        self.keymap[K_b]      = nTrisMsg.P1_ROT_CW
        self.keymap[K_LEFT]   = nTrisMsg.P2_MOVE_LEFT
        self.keymap[K_RIGHT]  = nTrisMsg.P2_MOVE_RIGHT
        self.keymap[K_DOWN]   = nTrisMsg.P2_MOVE_DOWN
        self.keymap[K_PERIOD] = nTrisMsg.P2_ROT_CCW
        self.keymap[K_SLASH]  = nTrisMsg.P2_ROT_CW
        self.keymap[K_p]      = nTrisMsg.PAUSE
        self.keymap[K_ESCAPE] = nTrisMsg.QUIT
        self.keymap[K_RETURN] = nTrisMsg.ACCEPT
    
    def init_game(self):
        self.stage = stage.Stage((30,30), 300, 10)
        self.player = nTrisPlayer()
        self.players = [self.player]
        self.nmg = nmino.nMinoGen(4)
        self.freq = 300.0
    
    def move(self, player, keydown, dir):
        if player < len(self.players):
            p = self.players[player]
            if p.nmc:
                able = p.move(keydown, dir)
                if dir == nminoctl.Dir.DOWN:
                    p.movetimer = 0.0
                    if not able:
                        p.nmc.rest()
                    
    def rot(self, player, keydown, spin):
        if keydown:
            if player < len(self.players):
                self.players[player].rot(spin)
    
    def update(self, dt):
        for p in self.players:
            p.movetimer+= dt
            if p.gameover:
                continue
            if not p.nmc:
                try:
                    p.nmc = nminoctl.nMinoCtl(self.nmg.generate(), self.stage)
                except nminoctl.GameOver:
                    p.gameover = True
                    continue
                p.movetimer = 0.0
            while p.movetimer > self.freq:
                p.movetimer-= self.freq
                if not p.nmc.move(nminoctl.Dir.DOWN):
                    p.nmc.rest()
        
    def draw(self, screen):
        screen.blit(self.bg, (0,0))
        self.stage.draw(screen)
        for p in self.players:
            if p.nmc:
                p.nmc.draw(screen)
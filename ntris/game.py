from collections import deque
import pygame
from pygame.locals import *

import stage
import nmino
import nminoctl
import utils
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

class nTrisMenuDir(Enum):
    DOWN  = 1,
    LEFT  = 2,
    UP    = 3,
    RIGHT = 4
    
class nTrisBase(Game):
    def __init__(self, screen):
        super().__init__(screen)
        self.bg = pygame.Surface(screen.get_size())
        self.bg.fill((0,0,0))
        self.init_msgs()
        self.init_game_keymap()
        self.init_menu_keymap()
        self.keymap = self.menu_keymap
    
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
        self.msgmap[nTrisMsg.PAUSE]  = lambda dn : self.pause()
        self.msgmap[nTrisMsg.QUIT]   = lambda dn : self.quit()
        self.msgmap[nTrisMsg.ACCEPT] = lambda dn : self.ok()
        self.msgmap[nTrisMsg.DOWN]   = lambda dn : self.select(nTrisMenuDir.DOWN)
        self.msgmap[nTrisMsg.UP]     = lambda dn : self.select(nTrisMenuDir.UP)
        self.msgmap[nTrisMsg.RIGHT]  = lambda dn : self.select(nTrisMenuDir.RIGHT)
        self.msgmap[nTrisMsg.LEFT]   = lambda dn : self.select(nTrisMenuDir.LEFT)
    
    def init_game_keymap(self):
        self.game_keymap = dict()
        self.game_keymap[K_a]      = nTrisMsg.P1_MOVE_LEFT
        self.game_keymap[K_d]      = nTrisMsg.P1_MOVE_RIGHT
        self.game_keymap[K_s]      = nTrisMsg.P1_MOVE_DOWN
        self.game_keymap[K_v]      = nTrisMsg.P1_ROT_CCW
        self.game_keymap[K_b]      = nTrisMsg.P1_ROT_CW
        self.game_keymap[K_LEFT]   = nTrisMsg.P2_MOVE_LEFT
        self.game_keymap[K_RIGHT]  = nTrisMsg.P2_MOVE_RIGHT
        self.game_keymap[K_DOWN]   = nTrisMsg.P2_MOVE_DOWN
        self.game_keymap[K_PERIOD] = nTrisMsg.P2_ROT_CCW
        self.game_keymap[K_SLASH]  = nTrisMsg.P2_ROT_CW
        self.game_keymap[K_p]      = nTrisMsg.PAUSE
        self.game_keymap[K_ESCAPE] = nTrisMsg.QUIT
    
    def init_menu_keymap(self):
        self.menu_keymap = dict()
        self.menu_keymap[K_LEFT]   = nTrisMsg.LEFT
        self.menu_keymap[K_RIGHT]  = nTrisMsg.RIGHT
        self.menu_keymap[K_DOWN]   = nTrisMsg.DOWN
        self.menu_keymap[K_UP]     = nTrisMsg.UP
        self.menu_keymap[K_ESCAPE] = nTrisMsg.QUIT
        self.menu_keymap[K_RETURN] = nTrisMsg.ACCEPT
    
    def switch_keymap_game(self):
        self.keymap = self.game_keymap
    def switch_keymap_menu(self):
        self.keymap = self.menu_keymap
    
    def quit(self):
        pygame.event.post(pygame.event.Event(QUIT))
    
    pause  = noop
    ok     = noop
    select = noop
    move   = noop
    rot    = noop
    
    def draw(self, screen):
        screen.blit(self.bg, (0,0))
        


    
class nTrisPlayerCtl:

    def __init__(self, freq, placed_cb):
        self.score = 0
        self.lastmoves = (None, None)
        self.nmc = None
        self.movetimer = utils.NormalTimer(self._move_dn, freq)
        self.lrtimer   = utils.NiceTimer(self._move_lr, freq*0.3, 0.7, 400.0)
        self.downtimer = utils.NiceTimer(self._move_dn, freq*0.2, 0.7, 400.0)
        self.timers = (self.lrtimer, self.downtimer, self.movetimer)
        self.gameover = False
        self.placed = placed_cb
        self.movetimer.activate()
    
    def _get_lastmove(self):
        return self.lastmoves[0]
    def _set_lastmove(self, dir):
        if self.lastmoves[0] != dir:
            self.lastmoves = (dir, self.lastmoves[0])
    def _del_lastmove(self, dir):
        if self.lastmoves[0] == dir:
            self.lastmoves = (self.lastmoves[1], None)
        else:
            self.lastmoves = (self.lastmoves[0], None)
        
    def _move_lr(self):
        if self.nmc:
            self.nmc.move(self._get_lastmove())
    
    def _move_dn(self):
        self.movetimer.reset()
        if self.nmc and not self.nmc.move(nminoctl.Dir.DOWN):
            self.placed(self, self.nmc.rest())
    
    def move(self, dn, dir):
        if dn:
            if dir != nminoctl.Dir.DOWN:
                if self.nmc and not any(self.lastmoves):
                    self.nmc.move(dir)
                self._set_lastmove(dir)
                self.lrtimer.activate()
            else:
                self.downtimer.activate()
                self._move_dn()
        else:
            if dir != nminoctl.Dir.DOWN:
                self._del_lastmove(dir)
                if not any(self.lastmoves):
                    self.lrtimer.deactivate()
            else:
                self.downtimer.deactivate()
        
    def rot(self, spin):
        if self.nmc:
            return self.nmc.rotate(spin)
        return False
    
    def take_nmino(self, nmc):
        self.nmc = nmc
        self.downtimer.reset()
        self.movetimer.reset()
    
    def grant_points(self, pts):
        self.score += pts
    
    def game_over(self):
        self.gameover = True
        self.downtimer.deactivate()
        self.lrtimer.deactivate()
        self.movetimer.deactivate()
        self.nmc = None
        
    def change_speed(self, freq):
        for t in self.timers:
            t.change_freq(freq)
    
    def update(self, dt):
        for t in self.timers:
            t.tick(dt)

class nTris(nTrisBase):
    
    DEF_FREQ  = 500.0
    PTS_PLACE = 10
    PTS_ROW   = 100
    
    def __init__(self, screen):
        super().__init__(screen)
        self.switch_keymap_game()
        self.freq = nTris.DEF_FREQ
        self.stage = stage.Stage((30,30), 300, 10)
        self.player = nTrisPlayerCtl(self.freq, self.placed)
        self.players = [self.player]
        self.nmg = nmino.nMinoGen(4)
        self.feed_nmino(self.player)
    
    def move(self, player, keydown, dir):
        if player < len(self.players):
            p = self.players[player].move(keydown, dir)
                    
    def rot(self, player, keydown, spin):
        if keydown:
            if player < len(self.players):
                self.players[player].rot(spin)
    
    def placed(self, player, loc):
        rows = {y for x,y in loc}
        full = self.stage.get_full_rows(rows)
        if full:
            def after():
                self.feed_nmino(player)
                player.grant_points(nTris.PTS_ROW)
            self.stage.anim_delete(full, done = after)
        else:
            player.grant_points(nTris.PTS_PLACE)
        self.feed_nmino(player)
    
    def feed_nmino(self, player):
        nm = self.nmg.generate()
        try:
            nmc = nminoctl.nMinoCtl(nm, self.stage)
            player.take_nmino(nmc)
        except nminoctl.GameOver:
            player.game_over()

    def update(self, dt):
        for p in self.players:
            p.update(dt)
    
    def draw(self, screen):
        screen.blit(self.bg, (0,0))
        self.stage.draw(screen)
        for p in self.players:
            if p.nmc:
                p.nmc.draw(screen)
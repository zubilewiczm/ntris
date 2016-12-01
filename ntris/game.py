# MIT License
# 
# Copyright (c) 2016 Marcin Zubilewicz
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import pygame
from pygame.locals import *

import stage
import nmino
import nminoctl
import utils
import position
import ui
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
        self.msgmap[nTrisMsg.P1_MOVE_LEFT]  = lambda dn : self.move(0, dn, position.Dir.LEFT)
        self.msgmap[nTrisMsg.P1_MOVE_RIGHT] = lambda dn : self.move(0, dn, position.Dir.RIGHT)
        self.msgmap[nTrisMsg.P1_MOVE_DOWN]  = lambda dn : self.move(0, dn, position.Dir.DOWN)
        self.msgmap[nTrisMsg.P1_ROT_CW]     = lambda dn : self.rot(0, dn, position.Spin.CLOCKWISE)
        self.msgmap[nTrisMsg.P1_ROT_CCW]    = lambda dn : self.rot(0, dn, position.Spin.COUNTERCLOCKWISE)
        self.msgmap[nTrisMsg.P2_MOVE_LEFT]  = lambda dn : self.move(1, dn, position.Dir.LEFT)
        self.msgmap[nTrisMsg.P2_MOVE_RIGHT] = lambda dn : self.move(1, dn, position.Dir.RIGHT)
        self.msgmap[nTrisMsg.P2_MOVE_DOWN]  = lambda dn : self.move(1, dn, position.Dir.DOWN)
        self.msgmap[nTrisMsg.P2_ROT_CW]     = lambda dn : self.rot(1, dn, position.Spin.CLOCKWISE)
        self.msgmap[nTrisMsg.P2_ROT_CCW]    = lambda dn : self.rot(1, dn, position.Spin.COUNTERCLOCKWISE)
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
        self.lrtimer   = utils.NiceTimer(self._move_lr, freq*0.3, 0.6, 300.0)
        self.downtimer = utils.NiceTimer(self._move_dn, freq*0.2, 0.7, 300.0)
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
        if self.nmc and not self.nmc.move(position.Dir.DOWN):
            col = self.nmc.nmino.color
            self.placed(self, self.nmc.rest(), col)
    
    def move(self, dn, dir):
        if dn:
            if dir != position.Dir.DOWN:
                if self.nmc and not any(self.lastmoves):
                    self.nmc.move(dir)
                self._set_lastmove(dir)
                self.lrtimer.activate()
            else:
                self.downtimer.activate()
                self._move_dn()
        else:
            if dir != position.Dir.DOWN:
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
    
    STAGE_TOP     = 30
    STAGE_XOFFSET = 30
    STAGE_WIDTH   = 300
    
    UI_MAIN_TOP = 15
    UI_MAIN_OFFSET = 20
    UI_LVL_SIZE = (60,40)
    UI_SCORE_XOFFSET = 30
    UI_SCORE_YOFFSET = 15
    UI_PTS_OFFSET = 10
    UI_OFFSTAGE_OFFSET = 15
    
    def __init__(self, screen):
        super().__init__(screen)
        self.switch_keymap_game()
        self.freq = self.DEF_FREQ
        self.stage_axis = self.screen.get_size()[0]
        self.stage = stage.Stage((self.STAGE_TOP,self.STAGE_XOFFSET),
                                 self.STAGE_WIDTH, 10)
        self.player = nTrisPlayerCtl(self.freq, self.placed)
        self.players = [self.player]
        self.nmg = nmino.nMinoGen(4)
        self.feed_nmino(self.player)
        self.lvl = 1
        
        self.init_texts_1p()
        
    
    def init_texts_1p(self):
        rect = self.stage.rect
        rect.topleft = (self.UI_MAIN_OFFSET, rect.bottom + self.UI_MAIN_TOP)
        rect.size = self.UI_LVL_SIZE
        
        self.text_ilvl = ui.Text("LVL",
                                 rect.topleft,
                                 color = [200,200,200])
        
        self.text_vlvl = ui.Text(str(self.lvl),
                                 rect.bottomright,
                                 ref   = position.Ref.BOTTOMRIGHT,
                                 scale = (3,4),
                                 shade = True)
        
        self.text_vpts = ui.ScoreText((self.stage_axis - self.UI_SCORE_XOFFSET,
                                       rect.top + self.UI_SCORE_YOFFSET),
                                      ref = position.Ref.TOPRIGHT,
                                      scale = (2,2),
                                      shade = True)
        
        rect_score = self.text_vpts.rect
        self.text_ipts = ui.Text("PTS",
                                 (rect_score.left - self.UI_PTS_OFFSET, rect.top),
                                 color = [200,200,200])
        
        self.textcollection_small = utils.TimedSet()
    
    def move(self, player, keydown, dir):
        if player < len(self.players):
            p = self.players[player].move(keydown, dir)
                    
    def rot(self, player, keydown, spin):
        if keydown:
            if player < len(self.players):
                self.players[player].rot(spin)
    
    def placed(self, player, loc, color):
        rows = {y for x,y in loc}
        
        rows_min = max(rows) + 0.5
        t        = rows_min/self.stage.gridsize[1] #[0,1)
        rect     = self.stage.rect
        y        = int(t*rect.bottom + (1-t)*rect.top)
        textpos = (self.stage.rect.right + self.UI_OFFSTAGE_OFFSET, y)
        
        full = self.stage.get_full_rows(rows)
        if full:
            pts = self.PTS_ROW*len(full)
            col = color
            time = 1000
            def after():
                self.feed_nmino(player)
                player.grant_points(pts)
                text    = ui.Text(str(pts), textpos,
                              color = col,
                              ref = position.Ref.MIDLEFT)
                self.textcollection_small.add(text, time)
            self.stage.anim_delete(full, done = after)
        else:
            pts = self.PTS_PLACE
            col = [255,255,255]
            time = 500
            player.grant_points(self.PTS_PLACE)
            self.feed_nmino(player)
            text    = ui.Text(str(pts), textpos,
                              color = col,
                              ref = position.Ref.MIDLEFT)
            self.textcollection_small.add(text, time)
    
    def feed_nmino(self, player):
        nm = self.nmg.generate()
        try:
            nmc = nminoctl.nMinoCtl(nm, self.stage)
            player.take_nmino(nmc)
        except nminoctl.GameOver:
            player.game_over()

    def update(self, dt):
        self.stage.update(dt)
        for p in self.players:
            p.update(dt)
        self.text_vpts.score = self.player.score
        self.textcollection_small.tick(dt)
    
    def draw(self, screen):
        screen.blit(self.bg, (0,0))
        self.stage.draw(screen)
        for p in self.players:
            if p.nmc:
                p.nmc.draw(screen)
        
        self.text_ilvl.draw(screen)
        self.text_vlvl.draw(screen)
        self.text_vpts.draw(screen)
        self.text_ipts.draw(screen)
        for txt in self.textcollection_small:
            txt.draw(screen)

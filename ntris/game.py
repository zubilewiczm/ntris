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

import ntris.stage
import ntris.nmino
import ntris.nminoctl
import ntris.nminoprev
import ntris.utils
import ntris.position
import ntris.ui
from ntris.utils import noop, not_implemented

from enum import Enum
from os.path import expanduser, isfile
import re

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
    
    def finalize(self):
        pass

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
    LEFT          = 16,
    DEBUG         = 17,
    
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
        self.msgmap[nTrisMsg.P1_MOVE_LEFT]  = lambda dn : self.move(0, dn, ntris.position.Dir.LEFT)
        self.msgmap[nTrisMsg.P1_MOVE_RIGHT] = lambda dn : self.move(0, dn, ntris.position.Dir.RIGHT)
        self.msgmap[nTrisMsg.P1_MOVE_DOWN]  = lambda dn : self.move(0, dn, ntris.position.Dir.DOWN)
        self.msgmap[nTrisMsg.P1_ROT_CW]     = lambda dn : self.rot(0, dn, ntris.position.Spin.CLOCKWISE)
        self.msgmap[nTrisMsg.P1_ROT_CCW]    = lambda dn : self.rot(0, dn, ntris.position.Spin.COUNTERCLOCKWISE)
        self.msgmap[nTrisMsg.P2_MOVE_LEFT]  = lambda dn : self.move(1, dn, ntris.position.Dir.LEFT)
        self.msgmap[nTrisMsg.P2_MOVE_RIGHT] = lambda dn : self.move(1, dn, ntris.position.Dir.RIGHT)
        self.msgmap[nTrisMsg.P2_MOVE_DOWN]  = lambda dn : self.move(1, dn, ntris.position.Dir.DOWN)
        self.msgmap[nTrisMsg.P2_ROT_CW]     = lambda dn : self.rot(1, dn, ntris.position.Spin.CLOCKWISE)
        self.msgmap[nTrisMsg.P2_ROT_CCW]    = lambda dn : self.rot(1, dn, ntris.position.Spin.COUNTERCLOCKWISE)
        self.msgmap[nTrisMsg.PAUSE]  = lambda dn : self.pause(dn)
        self.msgmap[nTrisMsg.QUIT]   = lambda dn : self.quit(dn)
        self.msgmap[nTrisMsg.ACCEPT] = lambda dn : self.ok(dn)
        self.msgmap[nTrisMsg.DOWN]   = lambda dn : self.select(dn,ntris.position.Dir.DOWN)
        self.msgmap[nTrisMsg.UP]     = lambda dn : self.select(dn,ntris.position.Dir.UP)
        self.msgmap[nTrisMsg.RIGHT]  = lambda dn : self.select(dn,ntris.position.Dir.RIGHT)
        self.msgmap[nTrisMsg.LEFT]   = lambda dn : self.select(dn,ntris.position.Dir.LEFT)
        self.msgmap[nTrisMsg.DEBUG]  = lambda dn : self.debug(dn)
    
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
        self.game_keymap[K_MINUS]  = nTrisMsg.DEBUG
    
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
    
    def quit(self, dn):
        pygame.event.post(pygame.event.Event(QUIT))
    
    pause  = noop
    ok     = noop
    select = noop
    move   = noop
    rot    = noop
    debug  = noop
    
    def draw(self, screen):
        screen.blit(self.bg, (0,0))
        


class nTris(nTrisBase):

    class nTrisPlayerCtl:

        DN_FACTOR = 0.2
        LR_FACTOR = 0.3
    
        def __init__(self, freq, placed_cb):
            self.score = 0
            self.lastmoves = (None, None)
            self.nmc = None
            self.movetimer = ntris.utils.NormalTimer(self._move_dn, freq)
            self.lrtimer   = ntris.utils.NiceTimer(self._move_lr, freq*self.DN_FACTOR, 0.6, 300.0)
            self.downtimer = ntris.utils.NiceTimer(self._move_dn, freq*self.LR_FACTOR, 0.7, 300.0)
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
            
        def _move_lr(self, t=None):
            if self.nmc:
                self.nmc.move(self._get_lastmove())
        
        def _move_dn(self, t=None):
            self.movetimer.reset()
            if self.nmc and not self.nmc.move(ntris.position.Dir.DOWN):
                col = self.nmc.nmino.color
                self.placed(self, self.nmc.rest(), col)
        
        def move(self, dn, dir):
            if dn:
                if dir != ntris.position.Dir.DOWN:
                    if self.nmc and not any(self.lastmoves):
                        self.nmc.move(dir)
                    self._set_lastmove(dir)
                    self.lrtimer.activate()
                else:
                    self.downtimer.activate()
                    self._move_dn()
            else:
                if dir != ntris.position.Dir.DOWN:
                    self._del_lastmove(dir)
                    if not any(self.lastmoves):
                        self.lrtimer.deactivate()
                else:
                    self.downtimer.deactivate()
            
        def rot(self, spin):
            if self.nmc:
                return self.nmc.rotate(spin)
            return None
        
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
        
        def is_game_over(self):
            return self.gameover
            
        def change_speed(self, freq):
            self.movetimer.change_freq(freq)
            self.lrtimer.change_freq(freq*self.LR_FACTOR)
            self.downtimer.change_freq(freq*self.DN_FACTOR)
        
        def update(self, dt):
            for t in self.timers:
                t.tick(dt)
                


    class GameState:
    
        DEF_FREQ  = 500.0
        PTS_PLACE = 10
        PTS_ROW   = 100
        
        STAGE_TOP     = 30
        STAGE_XOFFSET = 30
        STAGE_WIDTH   = 300
        
        UI_MAIN_TOP = 15
        UI_MAIN_OFFSET = 20
        UI_LVL_SIZE = (25,40)
        UI_SCORE_XOFFSET = 30
        UI_SCORE_YOFFSET = 15
        UI_PTS_OFFSET = 10
        UI_OFFSTAGE_OFFSET = 15
        
        def __init__(self, game):
            self.game = game
            self.game.switch_keymap_game()
            
            self.stage = ntris.stage.Stage((self.STAGE_TOP,self.STAGE_XOFFSET),
                                 self.STAGE_WIDTH, 10)
            self.player = nTris.nTrisPlayerCtl(self.DEF_FREQ, self.placed)
            self.players = [self.player]
            
            self.nmg = ntris.nmino.nMinoGen(4)
            self.nmp = ntris.nminoprev.nMinoPrev(
                ((self.STAGE_XOFFSET + self.STAGE_WIDTH + 40,
                    self.STAGE_TOP + 30),
                (100,100)),
                self.nmg)
            self.feed_nmino(self.player)
            
            self.lvl = 1
            self.freq = self.DEF_FREQ
            self.threshold = 300
            
            self.init_texts()
        
        def init_texts(self):
            rect = self.stage.rect
            rect.topleft = (self.UI_MAIN_OFFSET, rect.bottom + self.UI_MAIN_TOP)
            rect.size = self.UI_LVL_SIZE
            
            self.main_top = rect.top
            self.stage_axis = self.game.screen.get_size()[0]
            self.text_ilvl = ntris.ui.Text(
                "LVL",
                rect.topleft,
                color = [200,200,200]
            )
            
            self.text_vlvl = ntris.ui.Text(
                str(self.lvl),
                rect.bottomright,
                ref   = ntris.position.Ref.BOTTOMLEFT,
                scale = (3,4),
                shade = True
            )
            
            self.text_vpts = ntris.ui.ScoreText(
                (self.stage_axis - self.UI_SCORE_XOFFSET,
                rect.top + self.UI_SCORE_YOFFSET),
                ref = ntris.position.Ref.TOPRIGHT,
                scale = (2,2),
                shade = True
            )
            self.text_vpts.score = self.player.score
    
            rect_score = self.text_vpts.rect
            self.text_ipts = ntris.ui.Text(
                "PTS",
                (rect_score.left - self.UI_PTS_OFFSET, rect.top),
                color = [200,200,200]
            )
            self.set_name()
            self.text_timerset = ntris.utils.TimedSet()
            
        def move(self, player, keydown, dir):
            if player < len(self.players):
                p = self.players[player].move(keydown, dir)
                    
        def rot(self, player, keydown, spin):
            if keydown:
                if player < len(self.players):
                    res = self.players[player].rot(spin)
                    if res is not None:
                        if res:
                            self.game.sounds["rot"].play()
                        else:
                            self.game.sounds["blocked"].play()
        
        def pause(self, dn):
            if dn:
                self.game.state = self.game.PausedState(self.game, self)
        
        def update(self, dt):
            self.stage.update(dt)
            for p in self.players:
                p.update(dt)
            self.text_timerset.tick(dt)
            self.text_ntris.tick(dt)
        
        def draw(self, screen):
            self.stage.draw(screen)
            self.nmp.draw(screen)
            for p in self.players:
                if p.nmc:
                    p.nmc.draw(screen)
            
            self.text_ilvl.draw(screen)
            self.text_vlvl.draw(screen)
            self.text_vpts.draw(screen)
            self.text_ipts.draw(screen)
            self.text_ntris.draw(screen)
            for txt in self.text_timerset:
                txt.draw(screen)
            
        def set_name(self, flash=False):
            full_width = self.text_vpts.rect.left+self.text_vlvl.rect.right
            self.text_ntris = ntris.ui.FlashingText(self.nmg.name(),
                                              (full_width//2, self.main_top + self.UI_SCORE_YOFFSET),
                                              ref = ntris.position.Ref.MIDCENTER,
                                              scale = (2,2),
                                              shade = True)
            if self.text_ntris.rect.width > full_width:
                self.text_ntris.scale = (1,1)
            if flash:
                self.text_ntris.flash()
        
        def placed(self, player, loc, color):
            rows = {y for x,y in loc}
            
            rows_min = max(rows) + 0.5
            t        = rows_min/self.stage.gridsize[1] #[0,1)
            rect     = self.stage.rect
            y        = int(t*rect.bottom + (1-t)*rect.top)
            textpos  = (self.stage.rect.right + self.UI_OFFSTAGE_OFFSET, y)
            
            def proc(pts, col, time):
                player.grant_points(pts)
                self.text_vpts.score = self.player.score
                if player.score >= self.threshold:
                    self.lvlup()
                self.feed_nmino(player)
                text    = ntris.ui.Text(str(pts), textpos,
                              color = col,
                              ref = ntris.position.Ref.MIDLEFT)
                self.text_timerset.add(text, time)
            
            full = self.stage.get_full_rows(rows)
            if full:
                pts = self.PTS_ROW*len(full)
                self.game.sounds["line"].play()
                self.stage.anim_delete(full, done = lambda: proc(pts, color, 1000))
            else:
                pts = self.PTS_PLACE
                col = [255,255,255]
                proc(pts, col, 500)
                self.game.sounds["crash"].play()
        
        def feed_nmino(self, player):
            nm = self.nmp.get()
            try:
                nmc = ntris.nminoctl.nMinoCtl(nm, self.stage)
                player.take_nmino(nmc)
            except ntris.nminoctl.GameOver:
                player.game_over()
                if all(p.is_game_over() for p in self.players):
                    self.nmp.put(nm)
                    self.game.state = self.game.GameOverState(self.game, self)
        
        def lvlup(self):
            self.threshold += [300, 500, 700][self.lvl % 3]
            self.lvl += 1
            self.text_vlvl.text = str(self.lvl)
            
            q,r = divmod(self.lvl-1, 3)
            f   = 1.2**(0.25*q + r)
            self.freq = self.DEF_FREQ / f
            for p in self.players:
                p.change_speed(self.freq)
            
            if not r:
                self.stage.expand(1)
                self.nmg.lvlup()
                self.set_name(True)
            self.game.sounds["shake"].play()
                
        def debug(self, dn):
            self.player.score = self.threshold - 10

    
    class PausedState:
        
        def __init__(self, game, gamestate):
            self.game = game
            self.gamestate = gamestate
            self.prevscreen = pygame.Surface(self.game.screen.get_size())
            self.gamestate.draw(self.prevscreen)
            self.prevscreen.fill([128,128,128], None, BLEND_RGB_MULT)
            self.pressed = pygame.key.get_pressed()
            
            timer = ntris.utils.NormalTimer(lambda t:None, 800)
            self.text = ntris.ui.FlashingText(
                "PAUSED",
                self.prevscreen.get_rect().center,
                ref   = ntris.position.Ref.MIDCENTER,
                shade = True,
                scale = (4,4),
                timer = timer
            )
            self.text.flash()
            self.game.sounds["pause"].play()
            
        def update(self, dt):
            self.text.tick(dt)
        
        def draw(self, screen):
            screen.blit(self.prevscreen, (0,0))
            self.text.draw(screen)
        
        def pause(self, dn):
            if dn:
                self.game.state = self.gamestate
                
                pressed = pygame.key.get_pressed()
                movemsgs = [nTrisMsg.P1_MOVE_LEFT,
                    nTrisMsg.P1_MOVE_RIGHT,
                    nTrisMsg.P2_MOVE_LEFT,
                    nTrisMsg.P2_MOVE_RIGHT,
                    nTrisMsg.P1_MOVE_DOWN,
                    nTrisMsg.P2_MOVE_DOWN]
                summary = []
                    
                for k,v in self.game.keymap.items():
                    if v in movemsgs and self.pressed[k] != pressed[k]:
                        summary.append((v, pressed[k]))
                        
                if (movemsgs[0], True) in summary and (movemsgs[1], False) in summary:
                    summary.remove((movemsgs[1], False))
                if (movemsgs[0], False) in summary and (movemsgs[1], True) in summary:
                    summary.remove((movemsgs[0], False))
                if (movemsgs[2], True) in summary and (movemsgs[3], False) in summary:
                    summary.remove((movemsgs[3], False))
                if (movemsgs[2], False) in summary and (movemsgs[3], True) in summary:
                    summary.remove((movemsgs[2], False))
                    
                for v, p in summary:
                    self.game.msgmap[v](p)
    
    class GameOverState:
    
        def __init__(self, game, gamestate):
            self.game = game
            self.game.switch_keymap_menu()
            self.gamestate = gamestate
            self.prevscreen = pygame.Surface(self.game.screen.get_size())
            self.gamestate.draw(self.prevscreen)
            self.screen = self.prevscreen.copy()
            self.players = len(self.gamestate.players)
            
            self.anim_phase = 0
            self.anim_t = 0
            self.anim_darken = 2000
            self.anim_gameover = 300
            self.anim_scores = 1000
            self.anim_interscore = 1000
            self.anim_quit = 2000
            self.anim_p = 0
            
            self.upd_list = []
            
            rect = self.prevscreen.get_rect()
            self.text_gameover = ntris.ui.Text(
                "Game Over",
                ntris.position.rect_lerp(rect, 0.5, 0.25),
                scale = (4,4),
                shade = True,
                ref   = ntris.position.Ref.BOTTOMCENTER
            )
            
            scores = [self.gamestate.players[p].score for p in range(self.players)]
            max_score = max(scores)
            players_best = [i for i,v in enumerate(scores) if v == max_score]
            
            self.text_scores = []
            pos = ntris.position.rect_lerp(rect, 0.50, 0.4)
            for p in range(self.players):
                text1 = ntris.ui.Text(
                    str(scores[p]).rjust(ntris.ui.ScoreText.PADDING, " "),
                    pos,
                    scale = (3,3),
                    shade = True,
                    ref   = ntris.position.Ref.TOPCENTER
                )
                text2 = None
                pos = text1.rect.topleft
                pos = (pos[0]-10, pos[1]-10)
                if scores[p] > self.game.hiscore and p in players_best:
                    text2 = ntris.ui.FlashingText(
                        "HISCORE!",
                        pos,
                        scale = (1,1),
                        shade = True,
                        ref   = ntris.position.Ref.BOTTOMRIGHT,
                        timer = ntris.utils.NormalTimer(lambda t:None, 60),
                        color = [255,255,255],
                        color2 = [255,0,0]
                    )
                    text2.flash()
                    self.upd_list.append(text2)
                else:
                    text2 = ntris.ui.Text(
                        "SCORE:",
                        pos,
                        scale = (1,1),
                        shade = True,
                        ref   = ntris.position.Ref.BOTTOMRIGHT,
                        color = [255,255,255]
                    )
                pos = text1.rect.topright
                pos = (pos[0]+30, pos[1]-10)
                text3 = ntris.ui.Text(
                    "P"+str(p+1),
                    pos,
                    scale = (2,2),
                    shade = True,
                    ref   = ntris.position.Ref.BOTTOMLEFT,
                    color = [200, 200, 200]
                )
                pos = text1.rect.midbottom
                pos = (pos[0], pos[1]+60)
                if self.players == 1:
                    self.text_scores.append([text1, text2])
                else:
                    self.text_scores.append([text1, text2, text3])
            pos = ntris.position.rect_lerp(rect, 0.50, 0.8)
            self.text_esc = ntris.ui.Text(
                "Press ESC to quit",
                pos,
                scale = (2,2),
                shade = True,
                ref   = ntris.position.Ref.MIDCENTER
            )
            self.text_enter = ntris.ui.Text(
                "or Enter to play again!",
                self.text_esc.rect.move(0,5).midbottom,
                scale = (2,2),
                shade = True,
                ref   = ntris.position.Ref.TOPCENTER
            )
            if max_score > self.game.hiscore:
                self.game.hiscore = max_score

        
        def update(self, dt):
            for u in self.upd_list:
                u.tick(dt)
            if self.anim_phase == 5:
                return
            self.anim_t+= dt
            if self.anim_phase == 0 and self.anim_t > self.anim_darken:
                self.anim_phase = 1
                self.anim_t -= self.anim_darken
            elif self.anim_phase == 1 and self.anim_t > self.anim_gameover:
                self.anim_phase = 2
                self.anim_t -= self.anim_gameover
            elif self.anim_phase == 2 and self.anim_t > self.anim_scores:
                self.anim_phase = 3
                self.anim_t -= self.anim_scores
            elif self.anim_phase == 3 and self.anim_t > self.anim_interscore:
                self.anim_p+= 1
                self.anim_t -= self.anim_interscore
                if self.anim_p >= self.players:
                    self.anim_phase = 4
            elif self.anim_phase == 4 and self.anim_t > self.anim_quit:
                self.anim_phase = 5
        
        def draw(self, surface):
            if self.anim_phase == 0:
                self.screen.blit(self.prevscreen, (0,0))
                q = self.anim_t/self.anim_darken
                col = [int(255*(1-q) + 64*q) for i in range(3)]
                self.screen.fill(col, None, BLEND_RGB_MULT)
                surface.blit(self.screen, (0,0))
            elif self.anim_phase == 1:
                surface.blit(self.screen, (0,0))
            elif self.anim_phase >= 2:
                surface.blit(self.screen, (0,0))
                self.text_gameover.draw(surface)
            if self.anim_phase >= 3:
                for p in range(self.anim_p):
                    for text in self.text_scores[p]:
                        text.draw(surface)
            if self.anim_phase == 5:
                self.text_esc.draw(surface)
                self.text_enter.draw(surface)
        
        def ok(self, dn):
            self.game.state = self.game.GameState(self.game)
                
                
    class MenuState:
        
        def __init__(self, game):
            self.game = game
            self.game.switch_keymap_menu()
            self.text = ntris.ui.Text("nTris",
                ntris.position.rect_lerp(self.game.screen.get_rect(), 0.5, 0.2),
                scale = (6,6),
                shade = True,
                ref   = ntris.position.Ref.MIDCENTER
            )
            self.text2 = ntris.ui.Text("Press Enter to start!",
                ntris.position.rect_lerp(self.game.screen.get_rect(), 0.5, 0.8),
                scale = (2,2),
                shade = True,
                ref   = ntris.position.Ref.MIDCENTER
            )
        
        def draw(self, surface):
            self.text.draw(surface)
            self.text2.draw(surface)
        
        def update(self, dt):
            pass
        
        def ok(self, dn):
            self.game.state = self.game.GameState(self.game)
    
    
    # nTris
    def __init__(self, screen):
        super().__init__(screen)
        self.init_sounds()
        self.state = self.MenuState(self)
        self.hiscore = 5000
        self.parse_settings()
    
    def init_sounds(self):
        try:
            self.sounds
        except:
            self.sounds = {
                "blocked" : pygame.mixer.Sound("assets/sounds/blocked.wav"),
                "rot"     : pygame.mixer.Sound("assets/sounds/rot.wav"),
                "crash"   : pygame.mixer.Sound("assets/sounds/crash.wav"),
                "pause"   : pygame.mixer.Sound("assets/sounds/pause.wav"),
                "line"    : pygame.mixer.Sound("assets/sounds/line2.wav"),
                "shake"   : pygame.mixer.Sound("assets/sounds/shake.wav")
            }
            self.sound_rel_volumes = {
                "rot"     : 0.6,
                "crash"   : 0.7
            }
            self.sounds_volume(1.0)
            
    def sounds_volume(self, vol):
        for name, s in self.sounds.items():
            s.set_volume(vol*self.sound_rel_volumes.get(name, 1.0))
    
    def parse_settings(self):
        parser = re.compile(r"^([a-zA-Z][a-zA-Z0-9_]*)\s*=\s*([0-9]+)\s*$")
        whspce = re.compile(r"^\s*(?:#.*)?$")
        file = expanduser("~/.ntris-settings")
        if isfile(file):
            with open(file, "r") as f:
                for line in f:
                    m = parser.match(line)
                    if m:
                        if m.group(1) == "hiscore":
                            self.hiscore = int(m.group(2))
                        else:
                            raise Exception("read unknown setting "+m.group(1))
                    else:
                        if not whspce.match(line):
                            raise Exception("garbage in settings file")
    
    def save_settings(self):
        file = expanduser("~/.ntris-settings")
        with open(file, "w") as f:
            f.write("# Generated automagically, do not modify!\n")
            f.write("hiscore = "+str(self.hiscore)+"\n")
    
    def draw(self, screen):
        screen.blit(self.bg, (0,0))
        self.state.draw(screen)
        
    def finalize(self):
        self.save_settings()
    
    delegate2state = {
        "update",
        "move",
        "rot",
        "pause",
        "quit",
        "select",
        "debug",
        "ok"
    }
    
    def __getattribute__(self, name):
        if name in nTris.delegate2state:
            try:
                return self.state.__getattribute__(name)
            except AttributeError:
                return super().__getattribute__(name)
        else:
            return super().__getattribute__(name)

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
import ntris.position
import ntris.utils

pygame.font.init()

class Area:
    
    BD_COL  = [255,255,255]
    BD_COL2 = [x//2 for x in BD_COL]
    BG_COL  = [0, 0, 0]

    def __init__(self, rect, bg=None):
        self._rect = pygame.Rect(rect)
        self.bg = bg if bg else self.BG_COL
        self.bg = pygame.Color(*self.bg)
    
    def draw(self, screen):
        temprect = ntris.position.rect_inflate(self._rect, 2, 2)
        pygame.draw.rect(screen, Area.BD_COL2, temprect, 1)
        temprect = ntris.position.rect_inflate(temprect, -1, -1)
        pygame.draw.rect(screen, Area.BD_COL, temprect, 1)
        screen.subsurface(self._rect).fill(self.bg)
    
    @property
    def rect(self):
        return self._rect.copy()

class Text:
    
    FONT_FILE = "assets/fonts/PressStart2P.ttf"
    FONT      = pygame.font.Font(FONT_FILE, 8)
    
    def __init__(self, txt, pos, **kwargs):
        self.color  = kwargs.get("color", [255,255,255])
        self.scale  = kwargs.get("scale", None)
        self.ref    = kwargs.get("ref",   ntris.position.Ref.TOPLEFT)
        self.shade  = kwargs.get("shade", False)
        if not isinstance(self.ref, ntris.position.Ref):
            raise ValueError("instance of ntris.position.Ref expected")
        self.text = txt
        self.pos = pos
        
    def draw(self, surface):
        textsurf = Text.FONT.render(self.text, False, self._color)
        if self.scale:
            w,h = textsurf.get_size()
            w,h = int(self.scale[0]*w), int(self.scale[1]*h)
            textsurf = pygame.transform.scale(textsurf, (w,h))
        rect = ntris.position.rect_align(textsurf.get_rect(), self.pos, self.ref)
        if self.shade:
            textsurf2 = textsurf.copy()
            textsurf2.set_palette_at(1, [100,100,100])
            shift = max(self.scale)//2
            surface.blit(textsurf2, rect.move(shift,shift).topleft)
        surface.blit(textsurf, rect.topleft)
    
    def get_color(self):
        return self._color
    def set_color(self, col):
        self._color = pygame.Color(*col)
    color = property(get_color, set_color)
    
    def get_rect(self):
        rect = pygame.Rect((0,0), Text.FONT.size(self.text))
        rect.size = (rect.w*self.scale[0], rect.h*self.scale[1])
        rect = ntris.position.rect_align(rect, self.pos, self.ref)
        return rect
    rect = property(get_rect)

class ScoreText(Text):
    
    PADDING = 8
    
    def __init__(self, pos, **kwargs):
        super().__init__("", pos, **kwargs)
        self.score = 0
        
        widths  = []
        heights = []
        for i in range(10):
            self.text = str(i)
            rect = super().get_rect()
            widths.append(rect.width)
            heights.append(rect.height)
        self._digit_rect = pygame.Rect(0,0, max(widths), max(heights))
        self._shaded_text = Text("0", (0,0),
                                 color = tuple(x//2 for x in self.color),
                                 ref   = ntris.position.Ref.BOTTOMRIGHT,
                                 scale = self.scale)
        self._light_text  = Text("1", (0,0),
                                 color = self.color,
                                 ref   = ntris.position.Ref.BOTTOMRIGHT,
                                 scale = self.scale,
                                 shade = self.shade)
        
    def draw(self, surface):
        rect = self.get_rect()
        drect = self._digit_rect.copy()
        drect.topleft = rect.topleft
        fontfaces = [self._shaded_text, self._light_text]
        l = self.PADDING - len(str(self.score))
        
        for i,c in enumerate(str(self.score).rjust(self.PADDING, "0")):
            face = fontfaces[i>=l]
            face.text = c
            face.pos = drect.bottomright
            face.draw(surface)
            drect.topleft = drect.topright
        
    def get_rect(self):
        rect = self._digit_rect.copy()
        rect.w = rect.w * ScoreText.PADDING
        rect = ntris.position.rect_align(rect, self.pos, self.ref)
        return rect
    rect = property(get_rect)

    
class FlashingText(Text):
    
    def __init__(self, txt, pos, **kwargs):
        super().__init__(txt, pos, **kwargs)
        self.timer = kwargs.get("timer", ntris.utils.MultiShot(lambda t:None, 200, 7))
        self.color2 = kwargs.get("color2", None)
        if self.color2 is not None:
            self.color2 = pygame.Color(*self.color2)
        self.timer.hook(lambda t: self.action(t))
        self.flashing = False
    
    def action(self, timer):
        self.flashing ^= True
        
    def draw(self, surface):
        if not self.flashing:
            super().draw(surface)
        elif self.color2 is not None:
            col_old = self.color
            self.color = self.color2
            super().draw(surface)
            self.color = col_old
    
    def flash(self):
        self.timer.reset().activate()
    
    def tick(self, dt):
        self.timer.tick(dt)
    
    def stop(self):
        self.timer.deactivate()
        self.render = True
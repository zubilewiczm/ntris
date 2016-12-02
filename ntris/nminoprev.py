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
import ui
import position
import nmino as nm

class nMinoPrev(ui.Area):
    
    def __init__(self, rect, gen, margin=10):
        super().__init__(rect)
        if not isinstance(gen, nm.nMinoGen):
            TypeError("nMinoGen expected as second argument")
        self.nminogen = gen
        self.nmino = None
        self.margin = margin
        self._draw_rect = None
        self.get()
    
    def draw(self, surface):
        super().draw(surface)
        self.nmino.draw(surface.subsurface(self._draw_rect))
        
    def get(self):
        ret = self.nmino
        self.nmino = self.nminogen.generate()
        
        max = self.nminogen.max_size()
        temprect = position.rect_inflate(self._rect, -self.margin, -self.margin)
        size = min(temprect.size)//max
        
        bounds = self.nmino.bounds()
        n,m = bounds.size
        bounds.size = n*size, m*size
        bounds.center = self._rect.center
        
        self._draw_rect = bounds
        return ret
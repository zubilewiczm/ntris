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

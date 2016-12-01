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

from enum import Enum
import pygame

class Dir(Enum):
    DOWN  = 1
    LEFT  = 2
    RIGHT = 3
    UP = 4

class Ref(Enum):
    BOTTOMLEFT   = 1
    BOTTOMCENTER = 2
    BOTTOMRIGHT  = 3
    MIDLEFT      = 4
    MIDCENTER    = 5
    MIDRIGHT     = 6
    TOPLEFT      = 7
    TOPCENTER    = 8
    TOPRIGHT     = 9

class Spin(Enum):
    CLOCKWISE = 1
    COUNTERCLOCKWISE = 2

def rect_align(rect, pos, ref):
    if not isinstance(ref, Ref):
        raise ValueError("Instance of enum Ref expected")
    rect = pygame.Rect(rect)
    if ref.value % 3 == 1: #left
        rect.left    = pos[0]
    elif ref.value % 3 == 2: #center
        rect.centerx = pos[0]
    elif ref.value % 3 == 0: #right
        rect.right   = pos[0]
    if (ref.value-1) // 3 == 0: #bottom
        rect.bottom  = pos[1]
    elif (ref.value-1) // 3 == 1: #mid
        rect.center  = pos[1]
    elif (ref.value-1) // 3 == 2: #top
        rect.top     = pos[1]
    return rect

def rect_inflate(rect, x,y):
    return pygame.Rect(rect.left-x,rect.top-y,rect.width+2*x,rect.height+2*y)

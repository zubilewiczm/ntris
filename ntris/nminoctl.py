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

import stage as stg
import nmino as nm
import blocks as blk
from enum import Enum

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

class GameOver(Exception):
    pass
    
class nMinoCtl:
    def __init__(self, nmino, stage):
        if not (isinstance(nmino, nm.nMino) and isinstance(stage, stg.Stage)):
            raise ValueError("invalid arguments: first has to be an nMino, " +
              "while second a Stage")
        self.nmino = nmino
        self.stage = stage
        if not self.set_pos(Ref.TOPCENTER, (stage.gridsize[0]//2, stage.gridsize[1]-1)):
            raise GameOver
        
    def move(self, dir):
        if not isinstance(dir, Dir):
            raise ValueError("instance of Dir expected")
        px,py = self.pos
        translations = {
            1 : (lambda x,y : (x,y-1)),
            2 : (lambda x,y : (x-1,y)),
            3 : (lambda x,y : (x+1,y)),
            4 : (lambda x,y : (x,y+1))
        }
        return self.set_pos(Ref.MIDCENTER, translations[dir.value](px,py))
        
    def set_pos(self, ref, pos):
        if not isinstance(ref, Ref):
            raise ValueError("instance of Ref expected")
        bounds = self.nmino.bounds()
        if ref.value % 3 == 1: #left
            x = pos[0] - bounds.left
        elif ref.value % 3 == 2: #center
            x = pos[0]
        elif ref.value % 3 == 0: #right
            x = pos[0] - bounds.right + 1
        if (ref.value-1) // 3 == 0: #bottom
            y = pos[1] + bounds.bottom - 1
        elif (ref.value-1) // 3 == 1: #mid
            y = pos[1]
        elif (ref.value-1) // 3 == 2: #top
            y = pos[1] + bounds.top
        X,Y = x, self.stage.gridsize[1]-y-1
        if self.pos_allowed(X,Y):
            self.pos = (x,y)
            return True
        else:
            return False
    
    def rotate(self, spin):
        if not isinstance(spin, Spin):
            raise ValueError("instance of Spin expected")
        rot = self.nmino.rotate(spin == Spin.CLOCKWISE)
        tmp, self.nmino = self.nmino, rot
        if self.pos_allowed(*self.pos_stage):
            return True
        else:
            self.nmino = tmp
            return False
        
    def pos_allowed(self, x, y):
        for px,py in self.nmino:
            if self.stage.obstructs((px+x, py+y)):
                return False
        return True
    
    def rest(self):
        x,y = self.pos_stage
        ret = []
        for px,py in self.nmino:
            self.stage.add_obstacle((px+x,py+y), blk.Block(self.nmino.color))
            ret.append((px+x,py+y))
        self.nmino = None
        return ret
    
    def draw(self, surface):
        bounds = self.nmino.bounds()
        x,y = self.pos_stage
        x += bounds.x
        y += bounds.y
        size = bounds.size
        rect = self.stage.stage2screen((x,y), size)
        self.nmino.draw(surface.subsurface(rect))
        
    def __bool__(self):
        return bool(self.nmino)
    
    @property
    def pos_stage(self):
        return self.pos[0], self.stage.gridsize[1]-self.pos[1]-1
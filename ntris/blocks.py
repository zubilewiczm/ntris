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

import numpy as np
import random
import pygame
from pygame.locals import *

# scale
# color
# move_to

def block_sprite_init(looks, mask):
    mask.fill((255,255,255))
    a = pygame.surfarray.pixels_alpha(mask)
    b = pygame.surfarray.array3d(looks)
    r = np.min(b, axis=2).astype(np.int32)
    m, M = np.min(r), np.max(r)
    r = (r-m)*255/(M-m)
    r = r**2 / 255
    a[:,:] = r
    del a
    mask.unlock()

class Block:
    """
    Block - a basic rectangular object that gets drawn on screen. It's fully
      specified by its color. Its position and size are determined by surface
      passed to the 'draw' function. The texture it uses is tied directly
      to the class and is not changed during the game.
      
    Methods:
      __init__(col)
      __init__(Block)
      draw(surface)
    
    Properties:
        color: rw
    """
    LOOKS = pygame.image.load("assets/sprites/block.png")
    MASK  = pygame.Surface(LOOKS.get_size(), 0, LOOKS)
    block_sprite_init(LOOKS, MASK)

    def __init__(self, *args):
        """
        __init__(self, col)
        __init__(self, block)
            Constructs a block.
        
        Arguments:
            col  : pygame.Color
              Color of a block.
            
            block : ntris.Block
              Block to copy parameters from.
        """
        if isinstance(args[0], Block):
            block, *_ = args
            self.col = block.col
            self.shaded   = block.shaded
            self.flashing = block.flashing
            self.scale    = block.scale
        else:
            col, *_ = args
            self.set_color(col)
        self.shaded = False
        self.flashing = False
        self.scale = 1.0
    
    def draw(self, surface):
        wh = surface.get_size()
        img  = pygame.transform.smoothscale(Block.LOOKS, wh)
        if not self.flashing:
            tint = pygame.Surface(wh, 0, Block.LOOKS)
            tint.fill(self.col)
            if self.shaded:
                tint.fill((200,200,200), None, BLEND_RGB_MULT)
            else:
                mask = pygame.transform.smoothscale(Block.MASK, wh)
                tint.blit(mask, (0,0))
                tint.set_alpha()
            img.blit(tint, (0,0), None, BLEND_RGB_MULT)
        else:
            img.fill([255,255,255,200])
        surface.blit(img, (0,0))
        
    def disable(self):
        self.shaded = True
    def flash(self):
        self.flashing^= True
            
    def get_color(self):
        return self.col
    def set_color(self, col):
        self.col = pygame.Color(*col)
    color = property(get_color, set_color)

class BlockArray:
    """
    BlockArray - stores essential data about blocks lying on stage, i.e.
      color and positions on evenly-spaced grid of possible block positions.
    """
    def __init__(self, size, rect):
        self.size = tuple(size)[0:2]
        self.array = [[None]*size[0] for x in range(size[1])]
    
    def __getitem__(self, key):
        if isinstance(key, tuple) and len(key) == 2 and \
           all(isinstance(x,int) for x in key):
            return self.array[key[1]][key[0]]
        elif isinstance(key, int):
            return self.array[key]
        raise KeyError("invalid index ({})".format(key))
    
    def __setitem__(self, key, val):
        if not isinstance(val, Block):
            val = Block(val)
        if isinstance(key, tuple) and len(key) == 2 and \
           all(isinstance(x,int) for x in key):
            self.array[key[1]][key[0]] = val
        else:
            raise KeyError("invalid index ({})".format(key))
    
    def coords2rect(self, ref, coords, size=(1,1)):
        cx,cy = coords
        mcx,mcy = self.size
        w,h = ref.size
        t,l = ref.topleft
        px,py = cx*w//mcx, cy*h//mcy
        sx,sy = (cx+size[0])*w//mcx, (cy+size[1])*h//mcy
        return pygame.Rect(px+l,py+t,sx-px,sy-py)
    
    def expand(self, by):
        try:
            byx, byy = by
            assert(isinstance(byx, int) and isinstance(byy, int))
            assert(by[0]>0 and by[1]>0)
        except:
            raise ValueError("cannot expand BlockArray by " +
                             "{} (use a pair of positive integers)".format(by))
        sx, sy = self.size
        for i,a in enumerate(self.array):
            a = a.copy()
            copies, rest = divmod(byx, sx)
            first = -byx + copies * sx
            last  =  byx + copies * (sx+1)
            self.array[i].extend(a*copies)
            self.array[i][:0] = a*copies
            self.array[i].extend(a[:rest])
            self.array[i][:0] = a[-rest:]
        self.array[:0] = [[None]*(sx+2*byx) for x in range(byy)]
        self.size = (sx+2*byx, sy+byy)
    
    def delete_row(self, i):
        del self.array[i]
        self.array[:0] = [[None]*self.size[0]]
    
    def obstruction_at(self, coord):
        cx, cy = coord
        if not (isinstance(cx, int) and isinstance(cy, int)):
            raise KeyError("invalid index ({})".format(coord))
        return self.array[cy][cx] is not None
    
    def __iter__(self):
        for a in range(self.size[1]):
            for b in range(self.size[0]):
                if self.array[a][b]:
                    yield self[b,a]
    
    def with_rects(self, ref):
        for a in range(self.size[1]):
            for b in range(self.size[0]):
                if self.array[a][b]:
                    yield self[b,a], self.coords2rect(ref, (b,a))
    
    @property
    def dims(self):
        return self.size
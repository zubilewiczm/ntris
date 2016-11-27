import blocks as blk
import utils

import pygame
import random

class nMino:
    def __init__(self, *args):
        if isinstance(args[0], nMino):
            self.components = args[0].components.copy()
            self.color = args[0].color
        else:
            if len(args) == 2:
                if not self.is_valid_set(args[1]):
                    raise ValueError("second argument is not a set of ints")
                self.components = args[1]
            elif len(args) == 1:
                self.components = set()
            else:
                raise ValueError("expected 1 or 2 arguments, got {}".format(len(args)))
            self.normalize()
            self.color = pygame.Color(*args[0])
    
    def is_valid_set(self,s):
        for v in s:
            if not isinstance(v,tuple) or len(v) != 2:
                return False
            if not all(isinstance(x, int) for x in v):
                return False
        return True
    
    def rotate(self, clockwise=True):
        bx,by = self.fbarycenter()
        eps = 1e-10
        if clockwise:
            new = {(int(round(-y+by+eps)), int(round(x-bx+eps))) for x,y in self.components}
        else:
            new = {(int(round(y-by+eps)), int(round(-x+bx+eps))) for x,y in self.components}
        return nMino(self.color, new)
    
    def add(self, coord):
        coord2 = tuple(coord)[0:2]
        if not all(isinstance(x, int) for x in coord2):
            raise ValueError("expected pair of ints, got {}".format(coord))
        self.components.add(coord2)
    
    def __iter__(self):
        return iter(self.components)
        
    def fbarycenter(self):
        cx = sum(v[0] for v in self.components)
        cy = sum(v[1] for v in self.components)
        n = len(self.components)
        return cx/n, cy/n
    
    def barycenter(self):
        bx, by = self.fbarycenter()
        return int(round(bx)), int(round(by))

    def normalize(self):
        bx, by = self.barycenter()
        self.components = {(x-bx, y-by) for x,y in self.components}
    
    def bounds(self):
        if not self.components:
            return pygame.Rect(0,0,0,0)
        mx = min(x for x,y in self.components)
        Mx = max(x for x,y in self.components)
        my = min(y for x,y in self.components)
        My = max(y for x,y in self.components)
        return pygame.Rect(mx,my,Mx-mx+1,My-my+1)
    
    def blocks(self, *args):
        bounds = self.bounds()
        if isinstance(args[0], int):
            size, pos = args
            pos = (pos[0]-(size//2), pos[1]-(size//2))
            rect = bounds.move(pos)
            rect.size = (bounds.width*size, bounds.height*size)
        else:
            rect = pygame.Rect(args[0])
        for x,y in self.components:
            blkrect = (rect.left + (x-bounds.left)*rect.width  // bounds.width,
                       rect.top  + (y-bounds.top) *rect.height // bounds.height,
                       rect.left + (x-bounds.left+1)*rect.width  // bounds.width,
                       rect.top  + (y-bounds.top+1) *rect.height // bounds.height)
            blkrect = (blkrect[0], blkrect[1],
                       blkrect[2]-blkrect[0], blkrect[3]-blkrect[1])
            yield blk.Block(self.color), blkrect
    
    def draw(self, surface):
        for block, rect in self.blocks(((0,0), surface.get_size())):
            block.draw(surface.subsurface(rect))


class nMinoGen:
    TOOCOMPLEX = 8
    S,V = 100, 80
    
    def __init__(self, n):
        if isinstance(n, nMinoGen):
            self.ncomps = n.ncomps
            self.patterns = n.patterns.copy()
            self.colors = n.colors.copy()
        else:
            self.ncomps = n
            if n < nMinoGen.TOOCOMPLEX:
                self.pregenerate()
        
    def generate(self):
        if self.ncomps < nMinoGen.TOOCOMPLEX:
            p = random.choice(tuple(self.patterns))
            nm = nMino(self.colors[p], p)
            n = random.randint(0,3)
            for i in range(n):
                nm = nm.rotate()
            return nm
        else:
            return self.generate_inaccurate()
    
    def pregenerate(self):
        begin = frozenset([(0,0)])
        self.patterns = set([begin])
        i, self.ncomps = self.ncomps, 1
        while self.ncomps != i:
            self.ncomps+= 1
            self.postgenerate()
        self.update_colors()
    
    def postgenerate(self):
        translates = [lambda x,y: (x+1,y),
                      lambda x,y: (x-1,y),
                      lambda x,y: (x,y+1),
                      lambda x,y: (x,y-1)]
        new = set()
        for p in self.patterns:
            nmino = nMino([0,0,0], set(p))
            for x,y in nmino:
                for t in translates:
                    nmino2 = nMino(nmino)
                    tx,ty = t(x,y)
                    if not (tx,ty) in nmino.components:
                        nmino2.add((tx,ty))
                        nmino2.normalize()
                        allout = True
                        for i in range(4):
                            allout = allout and frozenset(nmino2.components) not in new
                            nmino2 = nmino2.rotate()
                        if allout:
                            new.add(frozenset(nmino2.components))
        self.patterns = new
    
    def generate_inaccurate(self):
        h = random.random()*360
        c = pygame.Color(255)
        c.hsva = h, nMinoGen.S, nMinoGen.V
        m = nMino(c)
        m.add((0,0))
        d = []
        s = set([(0,0)])
        translates = [lambda x,y: (x,y+1),
                      lambda x,y: (x-+1,y),
                      lambda x,y: (x,y-1),
                      lambda x,y: (x-1,y)]
        cur = (0,0)
        while len(m.components) < self.ncomps:
            for t in translates:
                tx,ty = t(cur[0],cur[1])
                if (ty, tx) > (0,0) and (tx,ty) not in s:
                    d.append((tx,ty))
                    s.add((tx,ty))
            i = random.choice(range(len(d)))
            i = random.choice(range(i,len(d)))
            cur = d[i]
            m.add(cur)
            del d[i]
        m.normalize()
        return m
    
    def lvlup(self):
        self.ncomps+= 1
        if self.ncomps < nMinoGen.TOOCOMPLEX:
            self.postgenerate()
            self.update_colors()
    
    def update_colors(self):
        self.colors = {p : utils.hsv(i, len(self.patterns), 100,100)
            for i,p in enumerate(self.patterns)}
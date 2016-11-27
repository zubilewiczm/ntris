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
        if not self.set_pos(Ref.TOPCENTER, (stage.gridsize[0]//2, 0)):
            raise GameOver
        
    def move(self, dir):
        if not isinstance(dir, Dir):
            raise ValueError("instance of Dir expected")
        px,py = self.pos
        translations = {
            1 : (lambda x,y : (x,y+1)),
            2 : (lambda x,y : (x-1,y)),
            3 : (lambda x,y : (x+1,y)),
            4 : (lambda x,y : (x,y-1))
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
            y = pos[1] - bounds.bottom + 1
        elif (ref.value-1) // 3 == 1: #mid
            y = pos[1]
        elif (ref.value-1) // 3 == 2: #top
            y = pos[1] - bounds.top
        if self.pos_allowed(x,y):
            self.pos = (x,y)
            return True
        else:
            return False
    
    def rotate(self, spin):
        if not isinstance(spin, Spin):
            raise ValueError("instance of Spin expected")
        rot = self.nmino.rotate(spin == Spin.CLOCKWISE)
        tmp, self.nmino = self.nmino, rot
        if self.pos_allowed(*self.pos):
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
        x,y = self.pos
        for px,py in self.nmino:
            self.stage.add_obstacle((px+x,py+y), blk.Block(self.nmino.color))
        self.nmino = None
    
    def draw(self, surface):
        bounds = self.nmino.bounds()
        x,y = self.pos
        x += bounds.x
        y += bounds.y
        size = bounds.size
        rect = self.stage.stage2screen((x,y), size)
        self.nmino.draw(surface.subsurface(rect))
        
    def __bool__(self):
        return bool(self.nmino)
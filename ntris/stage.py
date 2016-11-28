import pygame
import utils
from blocks import Block, BlockArray

class Stage:
    
    DEF_BC = [255,255,255]
    
    def __init__(self, pos, width, grid_width, **kwargs):
        if grid_width % 2 == 1:
            raise ValueError("grid_width isn't even! (grid_width={})"
                .format(width, grid_width))
        self.rect   = pygame.Rect(pos[0], pos[1], width, width*3//2)
        self.width  = self.rect.w
        self.height = self.rect.h
        self.border_color  = kwargs.get("bc", Stage.DEF_BC)
        self.border_color2 = [x//2 for x in self.border_color]
        gridsize  = (grid_width, grid_width*3//2)
        self.block_array = BlockArray(gridsize, self.rect)
   
    @property
    def gridsize(self):
        return self.block_array.dims
        
        
    def update(self):
        pass
    
    def draw(self, screen):
        temprect = utils.rect_inflate(self.rect, 2, 2)
        pygame.draw.rect(screen, self.border_color2, temprect, 1)
        temprect = utils.rect_inflate(temprect, -1, -1)
        pygame.draw.rect(screen, self.border_color, temprect, 1)
        temprect = utils.rect_inflate(temprect, -1, -1)
        
        for block, rect in self.block_array.with_rects(temprect):
            block.draw(screen.subsurface(rect))
            
    def stage2screen(self, *args):
        """
        stage2screen(self, coords, size=(1,1))
            Returns rect of screen coordinates containing cells between
            'coords' and 'coords'+'size' (right exclusive).
        
        Args:
            coords : pair of indices
            size   : pair of positive ints
        """
        return self.block_array.coords2rect(self.rect, *args)
    
    def add_obstacle(self, pos, blk):
        blk.disable()
        self.block_array[pos] = blk
    
    def obstructs(self, pos):
        return not 0 <= pos[0] < self.block_array.dims[0] or \
               not 0 <= pos[1] < self.block_array.dims[1] or \
               self.block_array.obstruction_at(pos)
               
    def get_full_rows(self, rows=None):
        rows = sorted(rows) if rows else range(self.gridsize[1])
        return [r for r in rows if all(self.block_array[r])]
    
    def delete(self, rows):
        for r in rows:
            self.block_array.delete_row(r)
    
    def anim_delete(self, rows, done):
        self.delete(rows)
        done()
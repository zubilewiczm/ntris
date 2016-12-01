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
import utils
from blocks import Block, BlockArray

class Stage(ui.Area):
    
    class StageRowPending:
        def __init__(self, rows, done, stage):
            self.rows = rows
            self.step = 0
            def callback():
                for r in rows:
                    for b in stage.block_array[r]:
                        if b:
                            b.flash()
                if self.step == 4:
                    done()
                    self.timer.deactivate()
                    stage.pending.remove(self)
                    stage.delete_rows(self.rows)
                self.step+= 1
            self.timer = utils.NormalTimer(callback, 70.0)
            self.timer.activate()
            
        def update(self, dt):
            self.timer.tick(dt)
    
    
    
    def __init__(self, pos, width, grid_width):
        if grid_width % 2 == 1:
            raise ValueError("grid_width isn't even! (grid_width={})"
                .format(width, grid_width))
                
        self.rect = pygame.Rect(pos[0], pos[1], width, width*3//2)
        super().__init__(self.rect)
        
        gridsize  = (grid_width, grid_width*3//2)
        self.block_array = BlockArray(gridsize, self.rect)
        self.pending = []

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
    
    def delete_rows(self, rows):
        for r in rows:
            self.block_array.delete_row(r)
            for p in self.pending:
                for i in range(len(p.rows)):
                    if p.rows[i] < i:
                        p.rows[i]-= 1
    
    def anim_delete(self, rows, done):
        self.pending.append(Stage.StageRowPending(rows, done, self))

        
    def update(self, dt):
        for p in self.pending:
            p.update(dt)
    
    def draw(self, screen):
        super().draw(screen)
        for block, rect in self.block_array.with_rects(self.rect):
            block.draw(screen.subsurface(rect))          

    @property
    def gridsize(self):
        return self.block_array.dims

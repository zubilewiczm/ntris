import unittest
import pygame
import ntris.blocks as blk

class TestBlock(unittest.TestCase):
    
    def test_ctors(self):
        block = blk.Block((0,0), (20,20), [255,255,0])
        self.assertEqual(block.dims.topleft, (0,0))
        self.assertEqual(block.size, (20,20))
        self.assertEqual(block.color, pygame.Color(255,255,0,255))
        
        block = blk.Block(pygame.Rect(block.dims.topleft, block.size), block.color)
        self.assertEqual(block.dims.topleft, (0,0))
        self.assertEqual(block.size, (20,20))
        self.assertEqual(block.color, pygame.Color(255,255,0,255))
        
        block = blk.Block(block)
        self.assertEqual(block.dims.topleft, (0,0))
        self.assertEqual(block.size, (20,20))
        self.assertEqual(block.color, pygame.Color(255,255,0,255))
        
        block = blk.Block((0.5,1.2), (23.1,-0.9), [0,0,0,255])
        self.assertEqual(block.dims, (0,1,23,0))
    
    def test_move(self):
        block = blk.Block((0,0,10,10), [14,52,63,23])
        block.move((10,10))
        self.assertEqual(block.dims, (10,10,10,10))
        block.move((0,0,20,20))
        self.assertEqual(block.dims, (0,0,20,20))
        block.dims = pygame.Rect(20,30,40,50)
        self.assertEqual(block.dims, (20,30,40,50))

class TestBlockArray(unittest.TestCase):

    def test_ctor(self):
        arr = blk.BlockArray((3,4), (10,10,100,100))
        self.assertEqual(arr.dims, (3,4))
        with self.assertRaises(Exception):
            arr.dims = (4,5)
            
    def test_getset(self):
        arr = blk.BlockArray((3,4),(10,10,75,100))
        with self.assertRaises(Exception):
            arr[3,2] = [255,255,255,255]
        arr[2,3] = [255,255,0]
        arr[1,1] = [255,0,255]
        self.assertEqual(arr[2,3].color, (255,255,0))
        self.assertEqual(arr[1,1].color, (255,0,255))
        self.assertEqual(arr[1,0], None)
        self.assertEqual(arr[2,3].rect, (60,85,25,25))
    
    def test_coords(self):
        arr = blk.BlockArray((3,4),(10,10,75,100))
        self.assertEqual(arr.coords2rect((1,2),(2,2)), (35,60, 50,50))
    
    def test_expand(self):
        arr = blk.BlockArray((3,4),(10,10,75,100))
        arr[0,3] = (24,25,26)
        arr[2,2] = (45,46,47)
        arr.expand((1,1))
        self.assertEqual(arr.size, (5,5))
        self.assertEqual(arr.size[1], len(arr.array))
        for i in range(arr.size[0]):
            self.assertEqual(arr.size[0], len(arr.array[i]))
        self.assertEqual(arr[0,3].color, (45,46,47))
        self.assertEqual(arr[4,4].color, (24,25,26))
        self.assertEqual(arr[4,3], None)
    
    def test_obtr(self):
        arr = blk.BlockArray((3,4),(10,10,75,100))
        arr[0,3] = (24,25,26)
        arr[2,2] = (45,46,47)
        self.assertTrue(arr.obstruction_at((0,3)))
        self.assertTrue(arr.obstruction_at((2,2)))
        self.assertFalse(arr.obstruction_at((0,0)))
    
    def test_iter(self):
        arr = blk.BlockArray((3,4),(10,10,75,100))
        arr[0,3] = (24,25,26)
        arr[2,2] = (45,46,47)
        max = 0
        for b in arr:
            max+= 1
            self.assertIsInstance(b, blk.Block)
        self.assertEqual(max, 2)
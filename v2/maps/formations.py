from random import randint


cave10x10 = [[0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
             [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
             [1, 1, 1, 1, 0, 0, 0, 1, 1, 1],
             [1, 1, 1, 1, 0, 0, 0, 1, 1, 0],
             [0, 1, 1, 0, 0, 0, 0, 1, 1, 0],
             [0, 0, 1, 0, 0, 0, 0, 1, 1, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
             [0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
             [0, 0, 1, 0, 0, 0, 1, 1, 1, 0],
             [0, 0, 0, 1, 1, 0, 0, 1, 0, 0]]
             

class WallShape(object):

    w, h = 1, 1
    
    def get_tile_data(self):
        for y in range(self.h):
            for x in range(self.w):
                yield self.shape[x][y], x, y

class MediumHollow(WallShape):
    
    w, h = 10, 10
    
    def __init__(self, cave_shape):
        self.shape = cave10x10
    
                
class RandomBoulder(WallShape):

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.shape = [([0] * w)] * h
        init_w = w/2
        for y in range(h):
            space = abs(w - init_w)
            space /= 2
            
            for x in range(w):
                if x < space:
                    blocked = False
                elif x < init_w:
                    blocked = True
                else:
                    blocked = False
                self.shape[x][y] = (1 if blocked else 0)
                
            init_w += randint(0, w - init_w)

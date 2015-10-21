import libtcodpy as libtcod

from settings import *
from unit import Unit
import markovgen

from random import randint

class TextGenerator(object):
    def __init__(self):
        self.sentences = []
        self.i = 0
        with open('waves.txt') as f:
            text = markovgen.Markov(f)
            for _ in range(10):
                self.add_sentence(text.generate_markov_text(size=100))
        
    def add_sentence(self, s):
        self.sentences.append(s)
        
    def advance_index(self):
        self.i += 1
        if self.i >= len(self.sentences):
            self.i = 0
            
    def get_sentence(self):
        s = self.sentences[self.i]
        self.advance_index()
        return s


class Tile(Unit):
    def __init__(self, blocked, con, block_sight=None):
        super(Tile, self).__init__(con)
        self.blocked = blocked
        
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight
        
        if self.blocked:
            self.set_color(COLOR_DARK_WALL)
        else:
            self.set_color(COLOR_DARK_GROUND)

#    def draw(self):
##        libtcod.console_set_char_background(self.con, 
 #                                self.x,
#                                 self.y,
#                                 self.color,
#                                 libtcod.BKGND_SET)
#                                               
#    def clear(self):
#        pass
        
class Map(object):

    width = SCREEN_WIDTH
    height = SCREEN_HEIGHT
    
    text = TextGenerator()

    def __init__(self, game, con):
        self.game = game
        self.con = con
        self.map_grid = [[Tile((False if randint(-7, 1) < 0 else True), self.con)
                            for y in range(self.height)] 
                                for x in range(self.width)]
                                
        for y in range(self.height):
            for x in range(self.width):
                u = self.map_grid[x][y]
                u.x, u.y = x, y
                                
        self.map_grid[7][7].blocked = True
        self.map_grid[7][7].block_sight = True
        
#        self.make_walls()
        
    def get_all_tiles(self):
        tiles = []
        for r in self.map_grid:
            for c in r:
                tiles.append(c)
        return tiles
        
    def make_walls(self):
        for y in range(self.height):
            for x in range(self.width):
                if randint(1, 10) == 5:
                    self.map_grid[x][y] = Tile(True, self.con)
        
    def oscillate(self):
        otext = self.text.get_sentence()
    
        rand_tiles = set()
        for _ in range(int(self.width*self.height*.1)):
            rand_tiles.add((randint(0, self.width - 1), randint(0, self.height - 1)))
        for i, t in enumerate(rand_tiles):
            x, y = t
            self.map_grid[x][y].char = otext[i]
            
    def get_cross(self, cellX, cellY):
        tiles = []
        try:
            tiles.append(self.map_grid[cellX + 1][cellY])
        except IndexError:
            pass
        try:
            tiles.append(self.map_grid[cellX - 1][cellY])
        except IndexError:
            pass
        try:
            tiles.append(self.map_grid[cellX][cellY + 1])
        except IndexError:
            pass
        try:
            tiles.append(self.map_grid[cellX][cellY - 1])
        except IndexError:
            pass       
        return tiles
        
    def get_all_tiles(self):
        tiles = []
        for y in range(self.height):
            for x in range(self.width):
                tiles.append(self.map_grid[x][y])
        return tiles
import libtcodpy as libtcod
from PIL import Image


from tile import EnvironmentTile, BottomlessPit
from primeRGB import sieve
import settings

def make_tile(map_drawing, x, y, con, game):
    primes = sieve(255*3)
    tile = map_drawing.get_tile(x, y)
    tile_rgb = tile[0], tile[1], tile[2]
    if tile_rgb == (221, 32, 117):
        return BottomlessPit(
            True,
            x, y, ' ', libtcod.black, con, game
                                     )
    blocked = (False if sum(tile_rgb) in primes or sum(tile_rgb) == 0 else True)
    color = (libtcod.darkest_grey if sum(tile_rgb) == 0 else libtcod.Color(*tile_rgb))
    return EnvironmentTile(
            blocked,
            x, y, '@', color, con, game
                                     )

class MapDrawing(object):

    def __init__(self, img):
        self.image_name = img
        self.tiles = [x for x in self.read_image()]
        self.tile_index = 0
        
    def read_image(self):
        self.open_image = Image.open(self.image_name)
        self.w, self.h = self.open_image.size
        for p in list(self.open_image.getdata()):
            yield p
        self.open_image.close()
        
    def get_next_tile(self):
        self.tile_index += 1
        if self.tile_index >= len(self.tiles):
            self.tile_index = 0
        return self.tiles[self.tile_index]
        
    def get_tile(self, x, y):
        return self.tiles[x + y*self.w]
        
lvl0 = MapDrawing("maps\lvl0.png")
lvl1 = MapDrawing("maps\lvl1.png")
lvl2 = MapDrawing("maps\lvl2.png")
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

class GifReader(object):

    def __init__(self, img):
        self.image_file = img
        self.frames = []
        self.frame_index = 0
        self.current_frame = None
        self.read_image()

    def get_frame_data(self):
        xys = [(i % self.w, i / self.h) for i in range(len(self.frames[0]))]
        frame_data = dict(zip(xys, [[] for xy in xys]))
        for f in self.frames:
            for i, n in enumerate(f):
                frame_data[(i % self.w, i / self.h)].append((n, None))
        return frame_data

    def advance_frame(self):
        self.frame_index += 1
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.current_frame = self.frames[self.frame_index]
    
    def read_image(self):
        im = Image.open(self.image_file)
        self.w, self.h = im.size
        self.add_frame(self.create_data(im))
        while True:
            try:
                im.seek(im.tell() + 1)
                img_data = self.create_data(im)
                self.add_frame(img_data)
            except EOFError:
                break
        im.close()
        self.current_frame = self.frames[self.frame_index]

    def add_frame(self, img_data):
        self.frames.append([x for x in img_data])

    def create_data(self, img):
        for p in list(img.getdata()):
            yield libtcod.Color(p, 0, 0)
    
        
lvl0 = MapDrawing("maps\lvl0.png")
lvl1 = MapDrawing("maps\lvl1.png")
lvl2 = MapDrawing("maps\lvl2.png")
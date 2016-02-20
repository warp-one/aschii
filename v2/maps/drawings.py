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
        self.read_image()

    def get_frame_data(self):
        def get_xy(i):
            return i % self.w, i / self.w
        xys = [get_xy(i) for i in xrange(len(self.frames[0]))]
        frame_data = dict(zip(xys, [[] for xy in xys]))
        for f in self.frames:
            for i, color_char in enumerate(f):
                frame_data[get_xy(i)].append(color_char)
        return frame_data

    def read_image(self):
        im = Image.open(self.image_file)
        self.w, self.h = im.size
        while True:
            try:
                current_frame = im.convert('RGB')
                img_data = self.create_data(current_frame)
                self.add_frame(img_data)
                im.seek(im.tell() + 1)
            except EOFError:
                break
        im.close()

    def create_data(self, img):
        for p in list(img.getdata()):
            yield (libtcod.Color(*p), libtcod.CHAR_BLOCK2)
    
    def add_frame(self, img_data):
        self.frames.append([x for x in img_data])

class SpecialEffect(object):

   
    def __init__(self, frames, position):
        self.current_frame = 0
        self.frames = frames # a dict of coordinates with lists of color, char data
        self.position = position
        self.num_frames = self.frames[(0, 0)]
        
    def get_char(self, x, y):
        x1, y1 = x - self.position[0], y - self.position[1]
        return self.frames[(x1, y1)][self.current_frame]

    def update(self):
        self.current_frame += 1
        if self.current_frame >= len(self.num_frames):
            self.current_frame = 0

    def begin(self, tilemap):
        for xy in self.frames.keys():
            x = xy[0] + self.position[0]
            y = xy[1] + self.position[1]
            tilemap.get_tile(x, y).effects.append(self)

    def complete(self, tilemap):
        for xy in self.frames.keys():
            tilemap.get_tile(*xy).effects.remove(self)
        
lvl0 = MapDrawing("maps/lvl0.png")
lvl1 = MapDrawing("maps/lvl1.png")
lvl2 = MapDrawing("maps/lvl2.png")
cave = MapDrawing("maps/cave.png")

tv = SpecialEffect(GifReader("maps/trees-loop.gif").get_frame_data(), (88, 14))

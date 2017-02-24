import libtcodpy as libtcod
from PIL import Image
from random import choice


from tile import EnvironmentTile, BottomlessPit
from primeRGB import sieve
import settings

# MAKING A MAP:
# One image has black pixels for floor, (221, 32, 117) for pits, and
# everything else for walls.
# A second image is referenced for floor color only.
#
# TODO: Add in a class to define other kinds of tiles and objects'
# placement on a level-by-level basis

def make_tile(map_drawing, x, y, con, game, blocked=None):
    tile = map_drawing.get_tile(x, y)
    tile_rgb = tile[0], tile[1], tile[2]
    floor = map_drawing.get_tile(x, y, layer="floor")
    floor_rgb = floor[0], floor[1], floor[2]
    if tile_rgb == (221, 32, 117):
        return BottomlessPit(
            True,
            x, y, ' ', libtcod.black, con, game)
    if blocked is None:                                 
        blocked = (False if tile_rgb == (0, 0, 0) else True)
    color = (libtcod.Color(*floor_rgb)
                            if not blocked 
                            else libtcod.Color(*tile_rgb))
    return EnvironmentTile(
            blocked,
            x, y, choice(['@', '%', '#']), color, con, game
                                     )

class MapDrawing(object):

    def __init__(self, img, floor_img=None):
        self.map_size_set = False   # the first image you read will set the size of the level
        
        self.image_name = img
        if not floor_img is None:
            self.floor_name = floor_img
        else:
            self.floor_name = None
            
        self.tiles = [x for x in self.read_image(self.image_name)]
        if self.floor_name:
            self.floor = [x for x in self.read_image(self.floor_name)]
        
    def read_image(self, img):
        self.open_image = Image.open(img)
        self.w, self.h = self.open_image.size
        if self.map_size_set is False:
            settings.LVL0_MAP_WIDTH, settings.LVL0_MAP_HEIGHT = self.w, self.h
            self.map_size_set = True
        for p in list(self.open_image.getdata()):
            yield p
        self.open_image.close()
        
    def get_tile(self, x, y, layer="walls"):
        if layer == "walls":
            return self.tiles[x + y*self.w]
        elif layer == "floor" and self.floor_name:
            return self.floor[x + y*self.w]
        else:
            return (31, 31, 31)

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
            yield (libtcod.Color(*p), '<')#libtcod.CHAR_BLOCK2) #
    
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
cave = MapDrawing("maps/longcave.png", floor_img="maps/longcavefloor.png")

tv = SpecialEffect(GifReader("maps/stream-loop.gif").get_frame_data(), (40, 75))

from PIL import Image

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
        
lvl0 = MapDrawing("maps\likethis.png")
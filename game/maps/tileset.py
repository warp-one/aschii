from tile import EnvironmentTile

default_tile = EnvironmentTile

class TileDictionary(dict):
    def __missing__(self, key):
        return default_tile

class Tileset(object):
    def __init__(self, tile_definitions=None):
        self.tile_dictionary = TileDictionary()
        if tile_definitions:
            for rgb, tile in tile_definitions.iteritems():
                self.tile_dictionary[rgb] = tile
        
    def get_tile_from_RGB(self, rgb):
        return self.tile_dictionary[rgb]
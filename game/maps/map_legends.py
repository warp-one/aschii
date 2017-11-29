all_tiles = {
    ""
    }

class MapLegend(object):

    tile_keys = {(0, 0, 0):         "unblocked enviro-tile",
                 (221, 32, 117):    "bottomless pit",
                 }

    def __init__(self, additional_tile_keys=None):
        if additional_tile_keys:
            for tk in additional_tile_keys:
                tile_keys[tk] = additional_tile_keys[tk]
        
        
    def get_tile_data(self, map_drawing, x, y, con, game):
        RGB_key = map_drawing.get_tile(x, y)
        if RGB_key in self.tile_keys:
            tile_type = self.tile_keys[RGB_key]
        else:
            tile_type = "blocked enviro-tile"
        
        if tile_type == "unblocked enviro-tile":
            return EnvironmentTile(False, x, y, choice(['@', '%', '#']), color, con, game)
        elif tile_type == "blocked enviro-tile":
            return EnvironmentTile(True, x, y, choice(['@', '%', '#']), color, con, game)
        elif tile_type == "bottomless pit":
            return BottomlessPit(True, x, y, ' ', libtcod.black, con, game)

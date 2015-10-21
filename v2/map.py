from random import randint

import libtcodpy as libtcod

from tile import EnvironmentTile

class TileMap(object):
    def __init__(self, w, h, con, game):
        self.con = con
        self.game = game
        self.width, self.height = w, h
        self.tilemap = [[EnvironmentTile(
                (False if randint(-6, 1) < 1 else True), 
                x, y, '@', libtcod.darkest_grey, self.con, self.game
                                         )
                            for y in range(h)]
                            for x in range(w)]

    def get_tiles(self):
        for y in range(self.height):
            for x in range(self.width):
                yield self.tilemap[x][y]

    def get_NSEW(self, x, y):
        targets = [(x, y-1), (x, y+1), (x+1, y), (x-1, y)]
        failures = 0
        for t in targets:
            try:
                yield self.tilemap[t[0]][t[1]]
            except IndexError:
                failures += 1

import libtcodpy as libtcod

from map import TileMap
from player import Player
import tools

class Level(object):

    start_location = 5, 15
    hud = []

    def __init__(self, game):
        self.game = game
        self.create_consoles()
        self.add_map()
        self.player = Player(15, 15, ' ', libtcod.white, self.foreground, self)
        
    def create_consoles(self):
        self.background = libtcod.console_new(self.game.width, self.game.height)
        self.foreground = libtcod.console_new(self.game.width, self.game.height)
        self.consoles = [self.background, self.foreground]

    def add_map(self):
        self.the_map = TileMap(self.game.width, self.game.height, self.foreground, self)
        self.tilemap = self.the_map.tilemap

    def get_all_tiles(self):
        tiles = [self.player]
        for t in self.the_map.get_tiles_by_layer():
            tiles.append(t)
        return tiles

    def render_all(self):
        lights = self.the_map.light_sources
        for t in self.the_map.get_tiles_by_layer():
            seen = libtcod.map_is_in_fov(self.the_map.libtcod_map, t.x, t.y)
            lit = False
            for l in lights:
                if tools.get_distance(l.get_location(), t.get_location()) < l.Lradius:
                    lit = True
            if lit or seen:
                t.visible = True
            else:
                t.visible = False
            t.draw()
        for i in self.hud:
            i.draw()

    def clear_all(self):
        return

    def update_all(self):
        for t in self.get_all_tiles():
            t.update()
        for i in self.hud:
            i.update()
        
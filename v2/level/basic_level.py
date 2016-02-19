
import libtcodpy as libtcod

from maps import TileMap
from player import Player



class Level(object):

    start_location = 5, 15
    hud = []

    def __init__(self, game):
        self.game = game
        self.create_consoles()
        self.add_map()
        self.player = Player(10, 6, ' ', libtcod.white, self.foreground, self)
        self.last_render = []
        self.next_render = []
        self.special_effects = []
        
    def create_consoles(self):
        self.background = libtcod.console_new(self.game.width, self.game.height)
        self.foreground = libtcod.console_new(self.game.width, self.game.height)
        self.consoles = [self.background, self.foreground]

    def add_map(self):
        self.the_map = TileMap(self.game.width, self.game.height, self.foreground, self)
        self.tilemap = self.the_map.tilemap

    def get_all_tiles(self):
        map_tiles = self.the_map.get_tiles()
        return self.the_map.get_tiles_by_layer(map_tiles)
        
    def update_all(self):
        self.next_render = [x for x in self.the_map.get_tiles_by_layer(self.the_map.get_tiles_in_render_area())]
        self.player.update()
        for t in self.next_render:
            if not isinstance(t, Player):
                t.update()
            seen = libtcod.map_is_in_fov(self.the_map.libtcod_map, t.x, t.y)
            if seen:
                t.visible = True
            else:
                t.visible = False

        for i in self.hud:
            i.update()
        for e in self.special_effects:
            e.update()

        if self.player.schimb:
            self.the_map.schimb()
            self.player.schimb = False

    def render_all(self):
        for t in self.next_render:
            t.draw()
        for i in self.hud:
            i.draw()
        self.last_render = self.next_render
        self.next_render = []

    def clear_all(self):
        for t in self.last_render:
            t.clear()
        self.last_render = []
        
        for a in self.player.action_manager.actions:
            a.clear()
        for d in self.player.children:
            d.clear()


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
        self.last_render = []
        
    def create_consoles(self):
        self.background = libtcod.console_new(self.game.width, self.game.height)
        self.foreground = libtcod.console_new(self.game.width, self.game.height)
        self.consoles = [self.background, self.foreground]

    def add_map(self):
        self.the_map = TileMap(self.game.width, self.game.height, self.foreground, self)
        self.tilemap = self.the_map.tilemap

    def get_all_tiles(self):
        all_tiles = [self.player]
        map_tiles = self.the_map.get_tiles()
        for t in self.the_map.get_tiles_by_layer(map_tiles):
            all_tiles.append(t)
        return all_tiles

    def render_all(self):
        lights = self.the_map.light_sources
        def x(light):
            return light.get_location()[0]
        def y(light):
            return light.get_location()[1]
        Xmins = [x(l) - l.Lradius for l in self.the_map.light_sources]
        Xmaxs = [x(l) + l.Lradius for l in self.the_map.light_sources]
        Ymins = [y(l) - l.Lradius for l in self.the_map.light_sources]
        Ymaxs = [y(l) + l.Lradius for l in self.the_map.light_sources]
        PXmin = self.player.x - self.player.sight_radius - 1
        PXmax = self.player.x + self.player.sight_radius + 1
        PYmin = self.player.y - self.player.sight_radius - 1
        PYmax = self.player.y + self.player.sight_radius + 1
        minX, minY = min([PXmin] + (Xmins if Xmins else [])), min([PYmin] + (Ymins if Ymins else []))
        maxX, maxY = max([PXmax] + (Xmaxs if Xmaxs else [])), max([PYmax] + (Ymaxs if Ymaxs else []))
        w = maxX - minX
        h = maxY - minY
        squares_to_render = self.the_map.get_area(minX, minY, w, h, anchor="default")
        all_render_objects = self.the_map.get_tiles_by_layer(squares_to_render)
        for t in all_render_objects:
            self.last_render.append(t)
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
        for t in self.last_render:
            t.clear()
        self.last_render = []
        
        for a in self.player.action_manager.actions:
            a.clear()

    def update_all(self):
        for t in self.get_all_tiles():
            t.update()
        for i in self.hud:
            i.update()
        
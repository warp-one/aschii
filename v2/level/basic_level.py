import libtcodpy as libtcod
import pyaudio
import wave
import sys

from maps import TileMap
from player import Player
import tools

'''# pyaudio
CHUNK = 1024
if len(sys.argv) < 2:
    print("Plays a wave file. \n\nUsage: %s sys.argv[0])
    sys.exit(-1)
wf = wave.open(sys.argv[1]
p = pyaudio.PyAudio()
stream = p.open(format=p.get_format_from_'''

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
        all_render_objects = self.the_map.get_all_in_render_area()
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
        to_clear = self.the_map.get_all_in_clear_area()
        for t in to_clear:#self.last_render:
            t.clear()
        self.last_render = []
        
        for a in self.player.action_manager.actions:
            a.clear()

    def update_all(self):
        for t in self.get_all_tiles():
            t.update()
        for i in self.hud:
            i.update()
        
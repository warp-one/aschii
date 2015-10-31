from random import randint

import libtcodpy as libtcod

from player import Player
from tile import EnvironmentTile
import tile
from directive import *
from map import TileMap
 
#actual size of the window
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
 
LIMIT_FPS = 20  #20 frames-per-second maximum

class Game(object):
    def __init__(self, w, h):
        self.width, self.height = w, h

        libtcod.console_set_custom_font('terminal8x8_gs_ro.png', 
                libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
        libtcod.console_init_root(self.width, self.height, 
                'rooms', False, renderer=libtcod.RENDERER_GLSL)
        libtcod.sys_set_fps(LIMIT_FPS)

        self.create_consoles()
        self.player = Player(15, 15, ' ', libtcod.white, self.foreground, self)
        self.add_map()
        self.player.move(5, 5)
        self.player.add_power(Power(self.player, self, static=True, offset=(0, 30+len(self.player.children))))
        self.player.add_power(Sprint(self.player, self, text="sprint", static=True, offset=(0, 30+len(self.player.children))))
        self.player.add_observer(self.the_map)
        
        self.statues = []
        for _ in range(1):
            s = tile.Statue(['He dreamt that it was alive, tremulous', 'it was not the atrocious bastard', 'of a tiger and a colt, but', 'at the same time both of these', 'fiery creatures, and also', 'a bull, a rose, and a storm'], 10 + _*3, 10 + _, 'S', libtcod.green, self.foreground, self)
            self.statues.append(s)
            self.the_map.add(s.x, s.y, s)
            self.player.add_child(Next(s, self, text="bow", static=True, offset = (2, 2)))
            self.player.add_child(Waypoint(s, self, text="approach", static=True, offset=(-1,-1)))
        s = self.the_map.schimb()
            
    def create_consoles(self):
        self.background = libtcod.console_new(self.width, self.height)
        self.foreground = libtcod.console_new(self.width, self.height)
        self.consoles = [self.background, self.foreground]

    def add_map(self):
        self.the_map = TileMap(self.width, self.height, self.foreground, self, self.player)
        self.tilemap = self.the_map.tilemap
        
    def switch_map(self):
        pass

    def get_all_tiles(self):
        tiles = [self.player]
        for t in self.the_map.get_tiles():
            tiles.append(t)
        return tiles

    def render_all(self):
        for t in self.the_map.get_tiles():
            t.draw()
#        for t in self.the_map.get_tiles_by_layer():
#            t.draw()
        for s in self.statues:
            s.draw()
        self.player.draw()

    def clear_all(self):
        self.player.clear()

    def update(self):
        for t in self.get_all_tiles():
            t.update()

    def execute(self):
        while not libtcod.console_is_window_closed():
            libtcod.console_set_default_foreground(0, libtcod.white)
            self.update()
            self.render_all()
            for c in self.consoles:
                libtcod.console_blit(c, 0, 0, self.width, self.height, 0, 0, 0)
            libtcod.console_flush()
            self.clear_all()
            exit = self.player.handle_keys()
            if exit:
                break

if __name__ == '__main__':
    game = Game(SCREEN_WIDTH, SCREEN_HEIGHT)
    game.execute()
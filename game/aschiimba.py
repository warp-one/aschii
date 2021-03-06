import cProfile as profile

from random import randint

import libtcodpy as libtcod

from maps import cave_drawing, bridge_drawing
from level import LevelZero
from player import Player
from tile import EnvironmentTile
import tile, settings

## this is a game made by William Schuller. w r schuller at gmail dot com
# Copyright me, 2015-2017.
#
# "the position of each individual letter on the page is subject to rules"
# bowing puzzles
# "it's all a maze."
# "all of it"
# in caves the way forward is sometimes through the hard-to-find tight squeeze
# something occurs to you about the walls...
#
# titles:
# like a s hell (the waves)
# through the caves
# 

# dodge, run from a goblin
# maze
# re-up the light, keep it active
# standing still increases light radius
# walking reduces it
# piecing narrative together
# tracking sensical story vs. generated nonsense
# typing light words in the background
# stopping to look for what you need in the floor
# collectibles in background, generally

# objects gleam in the darkness

class Game(object):

    the_map = None

    def __init__(self, w, h):
        self.width, self.height = w, h

        libtcod.console_set_custom_font(settings.FONT_IMG,
                libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW,
                )
        libtcod.console_init_root(self.width, self.height, 
                'the caves', False, renderer=libtcod.RENDERER_GLSL)
        libtcod.sys_set_fps(settings.LIMIT_FPS)

        self.current_level = LevelZero(self, bridge_drawing)
            
    def execute(self):
        while not libtcod.console_is_window_closed():
#            libtcod.console_set_default_foreground(0, libtcod.white)
            self.current_level.update_all()
            self.current_level.render_all()
            libtcod.console_blit(self.current_level.foreground, 0, 0, 
                                 self.width, self.height, 0, 0, 0)
            libtcod.console_flush()
            self.current_level.clear_all()
            exit = self.current_level.player.handle_keys()
            if exit:
                break

if __name__ == '__main__':
    game = Game(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
    if not settings.PROFILE:
        game.execute()
    else:
        profile.run('game.execute()')
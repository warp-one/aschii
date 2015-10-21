from random import randint

import libtcodpy as libtcod

from unit import Player
from settings import *
import map

class Game(object):
    def __init__(self):
        libtcod.console_set_custom_font('font2.png', 
           libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
        libtcod.console_init_root(SCREEN_WIDTH, 
                                  SCREEN_HEIGHT, 
                                  'python/libtcod tutorial', 
                                  False)
        libtcod.sys_set_fps(LIMIT_FPS)
        self.consoles = {}
        self.console_id = 0
        self.add_console()
        self.map = map.Map(self, self.consoles[0])
        self.add_console()
        self.player = Player(self.consoles[0], grid=self.map)
        self.objects = []
        self.objects.extend(self.map.get_all_tiles())
        self.units = [self.player]
        
    def add_console(self):
        self.consoles[self.console_id] = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.console_id += 1
        
    def get_default_console(self):
        return self.consoles.get(0, libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT))
        
    def render_all(self):
        for t in self.map.get_cross(self.player.x, self.player.y):
            if not t.blocked:
                t.current_color = libtcod.white
                t.char = "#"
        for o in self.objects:
            o.draw()
        for u in self.units:
            u.draw()
            
    def clear_all(self):
        for o in self.objects:
            o.clear()
        for u in self.units:
            u.clear()
        
    def update(self):
            
#        if randint(1, 5) == 1:
#            self.map.oscillate()
    
        libtcod.console_set_default_foreground(0, libtcod.white)
        con = self.consoles[0]
        self.render_all()
        libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
        libtcod.console_flush()
        self.clear_all()
        self.player.handle_keys()
                                
if __name__ == '__main__':
    game = Game()
    while not libtcod.console_is_window_closed():
        game.update()
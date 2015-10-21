import libtcodpy as libtcod

from settings import *

class Unit(object):
    def __init__(self, con, grid=None, char='@', color=libtcod.white):
        self.x = 5
        self.y = 5
        self.char = char
        self.color = color
        self.current_color = self.color
        self.con = con
        self.grid = grid
        
    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        
    def set_color(self, color):
        self.color = color
        self.current_color = self.color
        
    def draw(self):
#        libtcod.console_set_char_foreground(self.con, self.x, self.y, self.color)
        libtcod.console_set_default_foreground(self.con, self.current_color)
        libtcod.console_put_char(self.con,
                                 self.x,
                                 self.y,
                                 self.char,
                                 libtcod.BKGND_NONE)
                                               
    def clear(self):
        libtcod.console_put_char(self.con,
                                 self.x,
                                 self.y,
                                 ' ',
                                 libtcod.BKGND_NONE)
                                 
class SolidUnit(Unit):
    def move(self, dx, dy):
        newX = self.x + dx
        newY = self.y + dy
        if self.grid:
            if self.grid.map_grid[newX][newY].blocked:
                return
        self.x, self.y = newX, newY
        return True
        
        
class Player(SolidUnit):

    def move(self, dx, dy):
        if super(Player, self).move(dx, dy):
            for t in self.grid.get_all_tiles():
                t.current_color = t.color
        

    def handle_keys(self):
        key = libtcod.console_check_for_keypress()
        if key.vk == libtcod.KEY_ENTER and key.lalt:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
        elif key.vk == libtcod.KEY_ESCAPE:
            return True
        if libtcod.console_is_key_pressed(libtcod.KEY_UP):
            self.move(0, -1)
        if libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
            self.move(0, 1)
        if libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
            self.move(-1, 0)
        if libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
            self.move(1, 0)
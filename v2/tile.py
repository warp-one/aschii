import libtcodpy as libtcod

import tools

class Tile(object):

    name = ""

    def __init__(self, x, y, char, color, con, game):
        self.x, self.y = x, y
        self.char = char
        self.current_char = char
        self.color = color
        self.current_color = color
        self.con = con
        self.game = game
        self.next = None
        self.prev = None
        
        self.visible = True

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        
    def get_location(self):
        return self.x, self.y

    def place(self, x, y):
        self.move(-self.x + x, -self.y + y)

    def revert_color(self):
        self.current_color = self.color

    def toggle_visible(self):
        if self.visible:
            self.visible = False
        else:
            self.visible = True
        return self.visible
        
    def is_visible(self):
        lights = self.game.the_map.light_sources
        seen = libtcod.map_is_in_fov(self.game.the_map.libtcod_map, self.x, self.y)
        seen = True
        lit = False
        for l in lights:
            if tools.get_distance(l.get_location(), self.get_location()) < l.Lradius:
                lit = True
        return seen or lit and self.visible

    def draw(self):
        if self.is_visible():
            self._draw()
        else:
            self.clear()
    
    
    def _draw(self):
        self.current_char = self.char
        self.current_color = self.color
        x, y = self.get_location()
        libtcod.console_set_default_foreground(self.con, self.current_color)
        libtcod.console_put_char(self.con, x, y, 
                    self.current_char, libtcod.BKGND_NONE)

    def clear(self):
        libtcod.console_put_char(self.con, self.x, self.y, 
                                       ' ', libtcod.BKGND_NONE)

    def update(self):
        pass


class EnvironmentTile(Tile):
    def __init__(self, blocked, *args):
        super(EnvironmentTile, self).__init__(*args)
        self.blocked = blocked
        if self.blocked:
            self.color = libtcod.white
            self.revert_color()
            self.char = '#'
            
class Unit(Tile):   # has collision
    def move(self, dx, dy):
        newX = self.x + dx
        newY = self.y + dy
        if not self.game.the_map.run_collision(newX, newY):
            self.x += dx
            self.y += dy
            return True
        return False
        
class Word(Tile):
    def __init__(self, word, *args):
        super(Word, self).__init__(*args)
        self.word = word
        
    def draw(self):
        for i, letter in enumerate(self.word):
            x, y = self.x + i, self.y
            if libtcod.map_is_in_fov(self.game.the_map.libtcod_map, x, y):
                libtcod.console_set_default_foreground(self.con, self.current_color)
                libtcod.console_put_char(self.con, x, y, 
                                                letter, libtcod.BKGND_NONE)

        

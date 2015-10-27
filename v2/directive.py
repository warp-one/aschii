import libtcodpy as libtcod

from tile import Tile
import tools

class Attachment(object):
    def update(self):
        if not self.static:
            newX = self.anchor.x + self.offsetX 
            newY = self.anchor.y - self.offsetY
            self.place(newX, newY)
    

class Directive(Attachment, Tile):

    char = 'X'

    def __init__(self, anchor, game, static=False, text="destroy", offset=(0, 0)):
        self.anchor = anchor
        self.offsetX = offset[0]
        self.offsetY = offset[1]
        self.static = static
        self.color = libtcod.green
        self.current_color = self.color
        self.game = game
        self.con = game.foreground
        self.x, self.y = self.anchor.x + self.offsetX, self.anchor.y + self.offsetY
        self.active = False

        self.create_phrase(text)
        self.pressed = False
        
    def toggle_active(self):
        if self.active:
            self.active = False
        else:
            self.active = True

    def create_phrase(self, text):
        self.phrase = text
        self.phrase_clear = [False] * len(self.phrase) 
        self.phrase_index = 0
        self.completed = False
        
    def get_visible(self):
        dv = super(Directive, self).get_visible()
        av = self.anchor.get_visible()
        return dv and av

    def _draw(self):
        to_draw = self.phrase
        for i, char in enumerate(to_draw):
            x, y = self.x + i, self.y
            if not self.game.the_map.run_collision(x, y):
                color = (self.current_color if self.phrase_clear[i] else libtcod.red)
                libtcod.console_set_default_foreground(self.con, color)
                libtcod.console_put_char(self.con, x, y, 
                                                char, libtcod.BKGND_NONE)
                                            
            
    def complete(self):
        self.completed = True
        self.game.player.remove_child(self)
        
    def clear(self):
        pass
        
            
    def tick_phrase(self, letter):
        if self.anchor.get_visible() and self.get_visible():
            if not self.completed:
                if self.phrase[self.phrase_index] == letter:
                    self.phrase_clear[self.phrase_index] = True
                    self.phrase_index += 1
                    if self.phrase_index >= len(self.phrase):
                        self.complete()
                    return True
                else:
                    return False
                
    def reset(self):
        self.phrase_clear = [False] * len(self.phrase)
        self.phrase_index = 0
        
class Power(Directive):
    def get_visible(self):
        return True
        
        
## The Point of Interest Directives

class Waypoint(Directive):
    def complete(self):
#        self.completed = True
        p = self.game.player
        path = p.get_path(p.get_location(), self.anchor.get_location())
        self.game.player.add_order(len(path) * .1, p.move_along_path)
        self.reset()
        
    def get_visible(self):
        player_proximity = tools.get_distance(self.get_location(), 
                                            self.game.player.get_location())
        return super(Waypoint, self).get_visible() and player_proximity > 7
        
class Next(Directive):
    def complete(self):
        self.anchor.say_line()
        if self.anchor.script:
            self.reset()
        else:
            super(Next, self).complete()
            
class Legs(Directive):
    def create_phrase(self, text):
        self.phrase1 = "l"
        self.phrase2 = "r"
        self.current_phrase = self.phrase1
        self.phrase_clear = [False] * len(self.current_phrase) 
        self.phrase_index = 0
        self.completed = False
        
    def complete(self):
        if self.current_phrase == self.phrase1:
            self.current_phrase = self.phrase2
        else:
            self.current_phrase = self.phrase1
        self.phrase_clear = [False] * len(self.current_phrase)
        self.phrase_index = 0
        self.anchor.move(*self.anchor.facing)
        
    def reset(self):
        self.phrase_clear = [False] * len(self.current_phrase)
        self.phrase_index = 0
        
    def tick_phrase(self, letter):
        if self.current_phrase[self.phrase_index] == letter:
            self.phrase_clear[self.phrase_index] = True
            self.phrase_index += 1
            if self.phrase_index >= len(self.current_phrase):
                self.complete()
            return True
        else:
            return False
            
    def _draw(self):
        to_draw = self.current_phrase
        x_dir = self.anchor.facing[0]
        y_dir = self.anchor.facing[1]
        while self.game.the_map.get_tile(self.x + x_dir, self.y + y_dir).get_visible():
            if x_dir: x_dir += 1 * (x_dir/abs(x_dir))
            if y_dir: y_dir += 1 * (y_dir/abs(y_dir))
        for i, char in enumerate(to_draw):
            x, y = self.x + i + x_dir, self.y + y_dir
            if not self.game.the_map.run_collision(x, y):
                color = (self.current_color if self.phrase_clear[i] else libtcod.red)
                libtcod.console_set_default_foreground(self.con, color)
                libtcod.console_put_char(self.con, x, y, 
                                                char, libtcod.BKGND_NONE)
        
        
           
class SCHIMB(Directive):
    def __init__(self, indices, *args, **kwargs):
        super(SCHIMB, self).__init__(*args, **kwargs)
        self.coordinates = []
        for i in indices:
            self.coordinates.append(tools.get_xy_from_index(i, len(self.game.tilemap[0])))
        self.color2 = libtcod.blue - libtcod.grey
        self.color = libtcod.blue - libtcod.red
        self.revert_color()
            
    def draw(self):
        to_draw = zip(self.phrase, self.coordinates)
        for i, letter in enumerate(to_draw):
            x, y = letter[1][0], letter[1][1]
            color = (self.current_color if self.phrase_clear[i] else self.color2)
            if libtcod.map_is_in_fov(self.game.the_map.libtcod_map, x, y):
                libtcod.console_set_default_foreground(self.con, color)
                libtcod.console_put_char(self.con, x, y, 
                                                letter[0], libtcod.BKGND_NONE)
                                            
    def complete(self):
        super(SCHIMB, self).complete()
        self.game.the_map.schimb()
            
        
class PlayerArrow(Directive):
    def create_phrase(self, text):
        self.phrase = text
        self.phrase_clear = [False]
        self.phrase_index = 0
        self.completed = False

    def _draw(self):
        if self.game.the_map.run_collision(self.x, self.y):
            return
        char = chr(self.phrase)
        color = (self.current_color if self.pressed else libtcod.red)
        libtcod.console_set_default_foreground(self.con, color)
        libtcod.console_put_char(self.con, self.x, self.y, 
                                        char, libtcod.BKGND_NONE)
                                        
    def tick_phrase(self, letter):
        return
           
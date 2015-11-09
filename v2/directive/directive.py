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
    range = 5

    def __init__(self, anchor, game, static=False, text="Destroy", offset=(0, 0)):
        self.anchor = anchor
        self.offsetX = offset[0]
        self.offsetY = offset[1]
        self.static = static
        self.color = libtcod.green
        self.current_color = self.color
        self.dormant_color = libtcod.red
        self.game = game
        self.con = game.foreground
        self.x, self.y = self.anchor.x + self.offsetX, self.anchor.y + self.offsetY
        self.active = False

        self.create_phrase(text)
        self.pressed = False

        self.visible = True
        
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
        
    def is_visible(self):
        dv = super(Directive, self).is_visible()
        av = self.anchor.is_visible()
        return dv and av

    def _draw(self):
        in_range = tools.get_distance(self.game.player.get_location(), self.get_location()) < self.range
        if in_range:
            self.dormant_color = libtcod.red
        else:
            self.dormant_color = libtcod.grey
        
    
    
    
        to_draw = self.phrase
        for i, char in enumerate(to_draw):
            x, y = self.x + i, self.y
            if not self.game.the_map.run_collision(x, y):
                color = (self.current_color if self.phrase_clear[i] else self.dormant_color)
                libtcod.console_set_default_foreground(self.con, color)
                libtcod.console_put_char(self.con, x, y, 
                                                char, libtcod.BKGND_NONE)
                                            
            
    def complete(self):
        self.completed = True
        self.game.player.remove_child(self)
        
    def clear(self):
        pass
            
    def tick_phrase(self, letter):
        if self.anchor.is_visible() and self.is_visible():
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
        

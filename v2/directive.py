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

        self.create_phrase(text)
        self.pressed = False

    def create_phrase(self, text):
        self.phrase = text
        self.phrase_clear = [False] * len(self.phrase) 
        self.phrase_index = 0
        self.completed = False

    def draw(self):
        to_draw = self.phrase
        for i, char in enumerate(to_draw):
            color = (self.current_color if self.phrase_clear[i] else libtcod.red)
            libtcod.console_set_default_foreground(self.con, color)
            libtcod.console_put_char(self.con, self.x + i, self.y, 
                                            char, libtcod.BKGND_NONE)
            
    def complete(self):
        self.completed = True
        self.game.player.remove_child(self)
        
            
    def tick_phrase(self, letter):
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
        
class Aschimba(Directive):

    def __init__(self, indices, *args, **kwargs):
        super(Aschimba, self).__init__(*args, **kwargs)
        self.coordinates = []
        for i in indices:
            self.coordinates.append(tools.get_xy_from_index(i, len(self.game.tilemap[0])))
        self.color2 = libtcod.blue + libtcod.grey
        self.color = libtcod.blue + libtcod.red
        self.revert_color()
            
    def draw(self):
        to_draw = zip(self.phrase, self.coordinates)
        for i, letter in enumerate(to_draw):
            color = (self.current_color if self.phrase_clear[i] else self.color2)
            libtcod.console_set_default_foreground(self.con, color)
            libtcod.console_put_char(self.con, letter[1][0], letter[1][1], 
                                            letter[0], libtcod.BKGND_NONE)
                                            
    def complete(self):
        super(Aschimba, self).complete()
        self.game.the_map.schimb()
            
        
class PlayerArrow(Directive):
    def create_phrase(self, text):
        self.phrase = text
        self.phrase_clear = [False]
        self.phrase_index = 0
        self.completed = False

    def draw(self):
        if self.game.tilemap[self.x][self.y].blocked:
            return
        char = chr(self.phrase)
        color = (self.current_color if self.pressed else libtcod.red)
        libtcod.console_set_default_foreground(self.con, color)
        libtcod.console_put_char(self.con, self.x, self.y, 
                                        char, libtcod.BKGND_NONE)
                                        
    def tick_phrase(self, letter):
        return
           
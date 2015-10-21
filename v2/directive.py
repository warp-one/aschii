import libtcodpy as libtcod

from tile import Tile

#class Attache(Tile):
    

class Directive(Tile):
    def __init__(self, anchor, game, static=False, text="destroy"):
        self.anchor = anchor
        self.offsetX = 0
        self.offsetY = 0
        self.static = static
        self.char = '@'
        self.color = libtcod.green
        self.current_color = self.color
        self.game = game
        self.con = game.foreground
        self.x, self.y = self.anchor.x + self.offsetX, self.anchor.y + self.offsetY

        self.create_phrase(text)
        self.pressed = False

    def update(self):
        if not self.static:
            newX = self.anchor.x + self.offsetX 
            newY = self.anchor.y - self.offsetY
            self.place(newX, newY)

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
            

    def tick_phrase(self, letter):
        if not self.completed:
            if self.phrase[self.phrase_index] == letter:
                self.phrase_clear[self.phrase_index] = True
                self.phrase_index += 1
                if self.phrase_index >= len(self.phrase):
                    print "yeah!"
                    self.completed = True
                    self.anchor.remove_directive(self)
                return True
            else:
                return False
                
    def reset(self):
        self.phrase_clear = [False] * len(self.phrase)
        self.phrase_index = 0

        
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
        if isinstance(letter, str):
            return False
        if not self.completed:
            print self.phrase, letter, "AG"
            if self.phrase == letter + 10:
                self.phrase_clear[self.phrase_index] = True
                self.completed = True
                return True
            else:
                return False
                                        
    def reset(self):
        self.phrase_clear = [False]
        self.phrase_index = 0
        self.completed = False
        self.anchor.current_directive = None

    def update(self):
        super(PlayerArrow, self).update()
#        if self.completed:
#            self.period += .1
#            if self.period > .3:
#                self.period = 0.
#                self.reset()
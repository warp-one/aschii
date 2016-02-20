import libtcodpy as libtcod

from tile import Tile
import tools, faders

class Attachment(object):
    def update(self):
        if not self.static:
            newX = self.anchor.x + self.offsetX 
            newY = self.anchor.y - self.offsetY
            self.place(newX, newY)
    
        
class Directive(Attachment, Tile):

    char = 'X'
    range = 9

    def __init__(self, anchor, game, static=False, text="Destroy", offset=(0, 0), new_fader=None):
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

        self.change_text(text)
        self.pressed = False

        self.visible = False
        if new_fader:
            self.fader = new_fader(self.game.camera)
        else:
            self.fader = faders.DirectiveFade(self.game.camera)
        
    def toggle_active(self):
        if self.active:
            self.active = False
        else:
            self.active = True
            
    def change_text(self, text):
        self.phrase = text
        self.phrase_clear = [False] * len(self.phrase) 
        self.phrase_index = 0
        self.completed = False
        
    def is_visible(self):
        dv = super(Directive, self).is_visible()
        av = self.anchor.is_visible()
        return av
       
    def draw(self):
        if self.completed: # should only pass if there's a fader
            if self.fader:
                if self.fader.apply_draw_step_for_erase(self):
                    return
                else:
                    self.game.player.remove_child(self)
        elif self.is_visible():
            self._draw()


    def _draw(self):
        Ploc = self.game.player.get_location()
        Sloc = self.anchor.get_location()
        in_range = tools.get_distance(Ploc, Sloc) < self.range
        self.dormant_color = libtcod.red if in_range else libtcod.grey
        to_draw = self.phrase
        for i, char in enumerate(to_draw):
            x, y = self.x + i, self.y
            if (x, y) == self.anchor.get_location():
                continue
            x, y = self.game.camera.to_camera_coordinates(x, y)
            color = (self.current_color if self.phrase_clear[i] else self.dormant_color)
            libtcod.console_set_default_foreground(self.con, color)
            libtcod.console_put_char(self.con, x, y, 
                                            char, libtcod.BKGND_NONE)
                                                    
    def complete(self):
        self.completed = True
        if self.fader:
            self.clear()
            return
        else:
            self.game.player.remove_child(self)
        
    def clear(self):
        try:
            for i in xrange(len(self.phrase)):
                x, y = self.game.camera.to_camera_coordinates(self.x + i, self.y)
                libtcod.console_put_char(self.con, x, y, 
                                                ' ', libtcod.BKGND_NONE)
        except TypeError:
            x, y = self.game.camera.to_camera_coordinates(self.x, self.y)
            libtcod.console_put_char(self.con, self.x, self.y, 
                                            ' ', libtcod.BKGND_NONE)
            
    def tick_phrase(self, letter):
        if not self.completed:
            if self.anchor.is_visible() and self.is_visible():
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
        
class DirectiveLink(object):
    def __init__(self):
        self.links = []
        
    def add_link(self, directive):
        self.links.append(directive)
        
    def remove_link(self, directive):
        self.links.remove(directive)
        
    def notify_links(self, command):
        for l in self.links:
            getattr(l, command)()

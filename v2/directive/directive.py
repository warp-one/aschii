from random import randint, choice

import libtcodpy as libtcod

from tile import Tile
import tools, faders

class Flair(object):
    def __init__(self, period, width, height, split, direction):
        self.period = period
        self.width = width
        self.height = height
        self.split = split
        self.direction = direction
        
    def modulate(self, x, y, i, in_range):
        line = i/self.width
        return x + i%self.width, y + line
            
    def tick(self, width):
        pass
                    
class RollingFlair(Flair):
    def modulate(self, x, y, i, in_range):
        x, y = super(RollingFlair, self).modulate(x, y, i, in_range)
        if in_range:
            y = (y if i > self.split else y - self.direction) - self.height
        return x, y
            
    def tick(self, width):
        self.width = width
        if True:#not randint(0, 4):
            self.split += 1
            if self.split >= self.width:
                self.split = 0
                self.height += self.direction
                if self.height >= self.period:
                    self.direction = -1
                elif self.height <= 0:
                    self.direction = 1

                    
class RectangleFlair(Flair):
    def __init__(self, *args):
        super(RectangleFlair, self).__init__(*args)
        self.set_rectangle()
        
        
    def set_rectangle(self):
        self.rectangle_top = [(w, -self.height) for w in range(self.width)]
        self.rectangle_right = [(self.width - 1, -h) for h in range(self.height - 1, 1, -1)]
        self.rectangle_bottom = [(w, -1) for w in range(self.width)]
        self.rectangle_left = [(0, -h) for h in range(self.height - 1, 1, -1)]
        self.rectangle = self.rectangle_top + self.rectangle_left + self.rectangle_right + self.rectangle_bottom 
        
    def modulate(self, x, y, i, in_range):
        try:
            space = self.rectangle[i]# if self.direction == 1 else self.rectangle[-i]
        except IndexError:
            return x, y
        return x + space[0] - 1, y + space[1] + self.height - 1

        
    def tick(self, width):
        pass
   
    
class Directive(Tile):

    char = 'X'

    def __init__(self, anchor, game, 
                 static=False, 
                 text="Destroy", sentence=None, 
                 offset=(0, 0), 
                 new_fader=None,
                 flair=None,
                 on_completion_callable=None,
                 range = 5,
                 width = 10):
        self.anchor = anchor
        self.game = game
        self.static = static
        self.offset = offset
        self.sentence = sentence  # currently only used by FloorDirective
        self.width = width
        self.spaces_transparent = False
        
        if new_fader: self.fader = new_fader(self.game.camera)
        else: self.fader = faders.DirectiveFade(self.game.camera)
        if flair is None: self.flair = Flair(0, self.width, 0, 0, 0)
        else: self.flair = flair
        
        self.on_completion_callable = on_completion_callable
        self.range = range

        self.con = game.foreground
        self.change_text(text, sentence=self.sentence)

        self.color = libtcod.green
        self.dormant_color = libtcod.red
        self.current_color = self.color
        self.active = False
        self.visible = False
        
    @property
    def location(self):
        return self.anchor.x + self.offset[0], self.anchor.y + self.offset[1]
        
    @property
    def x(self):
        return self.anchor.x + self.offset[0]
        
    @property    
    def y(self):
        return self.anchor.y + self.offset[1]

    def toggle_active(self):
        if self.active:
            self.active = False
        else:
            self.active = True
            
    def change_text(self, text, sentence=None):
        self.phrase = text
        if not sentence:
            self.sentence = text
            self.phrase_position = 0
        else:
            self.sentence = sentence
            self.phrase_position = self.sentence.find(self.phrase)
        self.reset()
        
    def is_visible(self):
        dv = super(Directive, self).is_visible()
        av = self.anchor.is_visible()
        return av
       
    def draw(self):
        if self.completed: # should only be around to pass if there's a fader
            if self.fader:
                if self.fader.apply_draw_step_for_erase(self):
                    return
                else:
                    if self.on_completion_callable:
                        self.on_completion_callable()
                    self.game.player.remove_child(self)
        elif self.is_visible():
            self._draw()

    def p_draw(self):
        Ploc = self.game.player.location
        Sloc = self.anchor.location
        in_range = tools.get_distance(Ploc, Sloc) < self.range
        self.dormant_color = libtcod.red if in_range else libtcod.grey
        to_draw = self.phrase
        for i, char in enumerate(to_draw):
            x, y = self.x + i, self.y
#            if (x, y) == self.anchor.location:
#                continue
            x, y = self.game.camera.to_camera_coordinates(x, y)
            color = (self.current_color if self.phrase_clear[i] 
                                        else self.dormant_color)
            libtcod.console_set_default_foreground(self.con, color)
            libtcod.console_put_char(self.con, x, y, 
                                            char, libtcod.BKGND_NONE)
                                            
    def _draw(self):
        ir = self.in_range()
        
        for i, char in enumerate(self.sentence):
            if char == ' ':
                if self.spaces_transparent:
                    continue
            x, y = self.x, self.y
            x, y = self.game.camera.to_camera_coordinates(x, y)
            if self.flair:
                x, y = self.flair.modulate(x, y, i, ir)
            if tools.get_distance((x, y), self.game.player.location) > self.game.player.base_sight:
                color = libtcod.darker_grey
            else:
                color = libtcod.grey
                
            keyword_color_index = i - self.phrase_position

            if keyword_color_index < 0 or keyword_color_index > len(self.phrase) - 1:
                pass
            else:
                if ir:
                    color *= (self.current_color
                                if self.phrase_clear[keyword_color_index]
                                else self.anchor.current_color)
#            tile = self.game.the_map.tilemap[x][y]
#            tile.current_char = char
#            tile_current_color = color

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
                if self.flair:
                    x, y = self.flair.modulate(x, y, i)
                libtcod.console_put_char(self.con, x, y, 
                                                ' ', libtcod.BKGND_NONE)
        except TypeError:
            x, y = self.game.camera.to_camera_coordinates(self.x, self.y)
            libtcod.console_put_char(self.con, self.x, self.y, 
                                            ' ', libtcod.BKGND_NONE)
            
    def tick_phrase(self, letter):
        if len(self.phrase) is 0:
            return
        if not self.completed:
            if self.anchor.is_visible() and self.is_visible() and self.in_range():
                if self.phrase[self.phrase_index] == letter:
                    self.phrase_clear[self.phrase_index] = True
                    self.phrase_index += 1
                    if self.phrase_index >= len(self.phrase):
                        self.complete()
                    return True
        return False
                
    def reset(self):
        self.phrase_clear = [False] * len(self.phrase)
        self.phrase_index = 0
        self.clear()
        self.completed = False
        
    def update(self):
        if self.flair:
            self.flair.tick(len(self.sentence))
            
    def in_range(self):
        if tools.get_distance(self.anchor.location, self.game.player.location) < self.range:
            return True
        else:
            return False
        
class RotatingDirective(Directive):
    def __init__(self, script, *args, **kwargs):
        self.script = script
        self.num_rotations = 0
        self.max_rotations = len(self.script)
        super(RotatingDirective, self).__init__(*args, **kwargs)
        self.rotate_text()
    
    def complete(self):
        if self.num_rotations >= self.max_rotations and self.max_rotations > 0:
            self.flair = None
        self.rotate_text()
        self.reset()
        if self.on_completion_callable:
            self.on_completion_callable()

    def rotate_text(self):
        new_keyword, new_sentence = self.script[0]
        self.script.rotate(-1)
        self.num_rotations += 1
        self.change_text(new_keyword, sentence = new_sentence)
        
        

        
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

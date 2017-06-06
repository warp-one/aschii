from random import randint, choice

import libtcodpy as libtcod

from tile import Tile
import tools, faders, layout
   
    
class Directive(Tile):

    char = 'X'

    def __init__(self, anchor, game, 
                 static=False, 
                 text="Destroy", sentence=None, 
                 offset=(0, 0), 
                 new_fader=None,
                 text_layout=None,
                 on_completion_callable=None,
                 range = 5,
                 width = 10):
        self.anchor = anchor
        self.game = game
        self.static = static
        self.offset = offset
        self.sentence = sentence
        self.width = width
        self.spaces_transparent = False
        
        if new_fader: self.fader = new_fader(self.game.camera)
        else: self.fader = faders.DirectiveFade(self.game.camera)
        if text_layout is None: self.text_layout = layout.DirectiveLayout(0, self.width, 0, 0, 0)
        else: self.text_layout = text_layout
        
        self.on_completion_callable = on_completion_callable
        self.range = range

        self.con = game.foreground
        self.change_text(text, sentence=self.sentence)

        self.color = libtcod.green
        self.dormant_color = libtcod.red # not used by the _draw method
        self.current_color = self.color
        self.active = False
        self.visible = True
        
        self.phrase_coordinate = (0, 0)
        
    @property
    def location(self):
        return self.x, self.y
        
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
        dv = self.visible
        av = self.anchor.is_visible()
        return av and dv
       
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
        if self.text_layout:
            self.text_layout.words = self.sentence.split()
            coords = self.text_layout.get_coords(self.x, self.y, len(self.sentence))
        
        for i, char in enumerate(self.sentence):
            if char == ' ':
                if self.spaces_transparent:
                    continue
            x, y = coords[i]
            if i == self.phrase_position:
                self.phrase_coordinate = x, y
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
                                
            x, y = self.game.camera.to_camera_coordinates(x, y)
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
        return
        try:
            for i in xrange(len(self.phrase)): ##?????
                x, y = self.game.camera.to_camera_coordinates(self.x + i, self.y)
                if self.text_layout: ## !! not modulate any more
                    x, y = self.text_layout.modulate(x, y, i)
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
        if self.text_layout:
            self.text_layout.tick(len(self.sentence))
            
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
        self.persistent = True
    
    def complete(self):
        if self.num_rotations >= self.max_rotations and self.max_rotations > 0:
            if self.on_completion_callable:
                self.on_completion_callable()
            if self.persistent:
                self.num_rotations = 0
            else:
                super(RotatingDirective, self).complete()

        self.rotate_text()
        self.reset()

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

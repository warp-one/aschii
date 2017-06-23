from random import randint, choice

import libtcodpy as libtcod

from tile import Tile
import tools, faders, layout, directive_colors
   
    
class Directive(Tile):

    char = 'X'

    def __init__(self, anchor, game, 
                 static=False, 
                 text="Destroy", sentence=None, 
                 offset=(0, 0), 
                 new_fader=None,
                 text_layout=None,
                 color_scheme=None,
                 on_completion_callable=None,
                 range = 10,
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
        if color_scheme is None: self.color_scheme = directive_colors.ColorScheme(directive_colors.basic_red)
        else: self.color_scheme = color_scheme
        
        self.on_completion_callable = on_completion_callable
        self.range = range
        self.guessed = ""

        self.con = game.foreground
        self.change_text(text, sentence=self.sentence)

        self.dormant_color = libtcod.red # not used by the _draw method
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
        
    @property
    def to_draw(self):
        return self.sentence
        
    @property
    def not_guessed(self):
        guessed_letters = list(self.guessed)
        unguessed_letters = []
        for l in self.phrase:
            if l in guessed_letters:
                guessed_letters.remove(l)
                continue
            else:
                unguessed_letters.append(l)
        return "".join(unguessed_letters)
        
    @property
    def phrase_location(self):
        return self.sentence.find(self.phrase)

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
        self.text_layout.words = self.to_draw.split()
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
                    self.do_completion_actions()
                    self.game.player.remove_child(self)
        elif self.is_visible():
            self._draw()
            
    def do_completion_actions(self):
        if self.on_completion_callable:
            self.on_completion_callable()
        
                                            
    def _draw(self):
        ir = self.in_range()
        if self.static:
            ox, oy = self.offset
            coords = self.text_layout.get_coords(ox, oy, len(self.sentence))
        else:
            coords = self.text_layout.get_coords(self.x, self.y, len(self.sentence))
        colors = self.color_scheme.get_colors(self.phrase, self.to_draw, ir, self.phrase_index)

        for i, char in enumerate(self.to_draw):
            if char == ' ' and self.spaces_transparent:
                continue
                
            x, y = coords[i]
            if i == self.phrase_position:
                self.phrase_coordinate = x, y
                            
            color = colors[i]
            
            if not self.static:                    
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
        self.guessed = ""
        
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
            self.do_completion_actions()
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
            
            
class TestingDirective(Directive):
    def tick_phrase(self, letter):
        if len(self.phrase) is 0:
            return
        if not self.completed:
            if self.anchor.is_visible() and self.is_visible() and self.in_range():
                if letter in self.not_guessed:
                    self.guessed += letter
                    self.phrase_clear[self.phrase_index] = True
                    self.phrase_index += 1
                    if len(self.guessed) >= len(self.phrase):
                        if self.guessed == self.phrase:
                            self.complete()
                        else:
                            self.reset()
                else:
                    self.reset()
                return True
        return False
        
    @property
    def to_draw(self):
        phrase_replacement = self.guessed + self.not_guessed 
        return self.sentence.replace(self.phrase, phrase_replacement)

        
class NarrativeDirective(RotatingDirective):
    def do_completion_actions(self):
        if self.on_completion_callable:
            self.on_completion_callable(self)
    
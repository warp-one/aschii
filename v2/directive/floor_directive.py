from random import choice, randint
from collections import deque

import libtcodpy as libtcod

import tools, colors
from directive import Directive

class FloorDirective(Directive):

    next = False # !!!
    script = deque([("left", "Let's go left."),
                    ("right", "No, I like right.")
                    ]
                   )
    nodes = [(5, 5)]
    appear_flicker_duration = 15

    
    def __init__(self, *args, **kwargs):
        self.coords = []
        super(FloorDirective, self).__init__(*args, **kwargs)
        
        self._draw_on_floor = True
        self.priority = 0
        self.mandatory = True
        self.id = None
        self.num_rotations = 0

    def rotate_text(self):
        new_keyword, new_sentence = self.script[0]
        self.script.rotate(-1)
        self.num_rotations += 1
        self.change_text(new_keyword, sentence = new_sentence)
        
    def player_in_range(self): 
        # called, confusingly, by the scribe so that it gets
        # puts it in play only when it will actually be drawn.
        # or, rather, it's always drawn whenever it's put into
        # play
        for n in self.nodes:
            if tools.get_distance(self.anchor.location, n
                             ) < self.anchor.sight_radius:
                self.nearest_node = n
                break
        else:
            self.nearest_node = None
        return self.nearest_node

    def draw(self):
        if self.nearest_node:
            if self.visible:
                if self.active_node is None:
                    self.appear_timer = self.appear_flicker_duration
                self.active_node = self.nearest_node
        else:
            self.visible = False
            self.active_node = None
        super(FloorDirective, self).draw()

    def _draw(self):
        colorful_choice = libtcod.Color(*self.flicker_color)
        if self.appear_timer > 0:
            if self.appear_timer % 2:
                self.phrase_color = colorful_choice * (self.appear_timer/10.)
            self.appear_timer -= 1

        keyword_position = self.sentence.find(self.phrase)
        sentence_flash = not randint(0, 20)
        phrase_flash = not randint(0, 15)
        for i, char in enumerate(self.sentence):
            x, y = self.coords[i][0]
            if not self.game.the_map.get_tile(x, y).visible:
                continue
            
            floor_color = self.coords[i][1]
            self.dormant_color = (floor_color * .5
                                    if sentence_flash
                                    else floor_color)
            self.phrase_color = (colorful_choice
                                    if phrase_flash
                                    else self.dormant_color)
            if tools.get_distance((x, y), self.game.player.location) > self.game.player.min_sight:
                color = self.dormant_color * .5
            else:
                color = self.dormant_color
                
            if self.draw_on_floor:
                x, y = self.game.camera.to_camera_coordinates(x, y)
            else:
                print x, y, "AGAWERGERG"

            keyword_color_index = i - keyword_position

            if keyword_color_index < 0 or keyword_color_index > len(self.phrase) - 1:
                pass
            else:
                color = (self.current_color
                            if self.phrase_clear[keyword_color_index]
                            else self.phrase_color)

            libtcod.console_set_default_foreground(self.con, color)
            libtcod.console_put_char(self.con, x, y,
                                            char, libtcod.BKGND_NONE)
                                            
    def clear(self): # only needed if not draw_on_floor?
        for c in self.coords:
            x, y = c[0]
            libtcod.console_put_char(self.con, x, y, 
                                        ' ', libtcod.BKGND_NONE)
        
    def tick_phrase(self, letter): # IT'S GOTTA RETURN THE RESUUUUUULT
        # add conditional about visibility of self.phrase to make
        # this only useable when you can actually see the word
        return super(FloorDirective, self).tick_phrase(letter)
        
    def is_visible(self):
        return self.visible
        
    @property
    def draw_on_floor(self):
        return self._draw_on_floor
        
    @draw_on_floor.setter
    def draw_on_floor(self, boolean):
        if not boolean:
            self.clear()
        self._draw_on_floor = boolean
        
    def complete(self):
        self.anchor.notify(self.game.player, "directive requests schimb")
        self.num_rotations = 0
        self.rotate_text()
        self.reset()
        self.visible = False

        self.nodes.remove(self.active_node)
        self.active_node = None
        
        
class Lightener(FloorDirective):
    #should only appear in fixed places, and each disappear after you use it once

    script = deque([("light", "I quiver and hang in a loop of light."),
                    ("lantern", "Like a lantern down a dark lane."),
                    ("glow", "A mysterious glow against a stand of yew trees."),
                    ("candle", "To lXXXt a candle is to cast a shadow..."),
                    ("luminous", "You are not yourself luminous!")
                    ]
                   )
    nodes = [(x, x) for x in range(10, 60, 10)]

    def __init__(self, *args, **kwargs):
        super(Lightener, self).__init__(*args, **kwargs)
        self.color = libtcod.black
        self.dormant_color = libtcod.light_grey
        self.current_color = self.color
        self.active_node = None
        self.rotate_text()
        self.appear_timer = 0
        
    @property
    def flicker_color(self):
        return choice(colors.fire_colorset)

    def complete(self):
        super(Lightener, self).complete()
        self.game.player.change_min_sight(2)
        self.game.player.darken_timer = 0

        
class Schimber(FloorDirective):

    script = deque([("ants", "This line is being eaten by ants."),
                    ("point", "Could you point your headlamp over there?"),
                    ("your", "Watch your foot!"),
                    ("way", "Is this the right way?"),
                    ("forward", "I think forward is the only possibility.")
                    ]
                   )
    nodes = [(x/2, x) for x in range(10, 110, 20)]
    
    def __init__(self, *args, **kwargs):
        super(Schimber, self).__init__(*args, **kwargs)
        
        self.color = libtcod.black
        self.dormant_color = libtcod.light_grey
        self.current_color = self.color
        self.active_node = None
        self.rotate_text()
        self.appear_timer = 0
        
    @property
    def flicker_color(self):
        return choice(colors.random_colorset)
        
     
class Storyteller(FloorDirective):
       
    script = deque([("moths", "Do you ever think about moths?"),
                    ("wings", "The quiet flap of their wings?"),
                    ("eyes",  "An enormous pair of dark eyes."),
                    ]
                   )
    nodes = [(x, x) for x in range(10, 110, 30)]
    
    def __init__(self, *args, **kwargs):
        super(Storyteller, self).__init__(*args, **kwargs)
        
        self.color = libtcod.black
        self.dormant_color = libtcod.light_grey
        self.current_color = self.color
        self.active_node = None
        self.rotate_text()
        self.appear_timer = 0
        self.max_rotations = len(self.script)
        
    @property
    def flicker_color(self):
        return choice(colors.random_colorset)

    def complete(self):
        if self.num_rotations >= self.max_rotations:
            super(Storyteller, self).complete()
        else:
            self.rotate_text()
            self.reset()
        
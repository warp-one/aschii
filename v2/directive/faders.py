from random import randint

import libtcodpy as libtcod

import tools

class Fader(object):
    def __init__(self, camera):
        self.fade_time = 60 # in ticks
        self.fade_step = self.fade_time
        self.color_add = libtcod.darkest_grey
        self.camera = camera

class DirectiveFade(Fader):
        
    def apply_draw_step_for_erase(self, directive):
        self.fade_step -= 1
        iteration = self.fade_time - self.fade_step
        if self.fade_step < 0:
            return False
        Ploc = directive.game.player.get_location()
        Sloc = directive.anchor.get_location()
        in_range = tools.get_distance(Ploc, Sloc) < directive.range
        directive.dormant_color = libtcod.red if in_range else libtcod.grey
        to_draw = directive.phrase
        color = directive.current_color - self.color_add * iteration
        if color == libtcod.black:
            return False

        for i, char in enumerate(to_draw):
            rx, ry = randint(-1, 1), randint(-1, 1)
            x, y = self.camera.to_camera_coordinates(directive.x + i + rx, directive.y + ry)
            if True:#not self.game.the_map.run_collision(x, y): 
                    # dunno about the above, visuals-wise
                libtcod.console_set_default_foreground(directive.con, color)
                libtcod.console_put_char(directive.con, x, y, 
                                                char, libtcod.BKGND_NONE)

        return True

class DirectiveLineFade(Fader):
        
    def apply_draw_step_for_erase(self, directive):
        self.fade_step -= 1
        iteration = self.fade_time - self.fade_step
        if self.fade_step < 0:
            return False
        Ploc = directive.game.player.get_location()
        Sloc = directive.anchor.get_location()
        in_range = tools.get_distance(Ploc, Sloc) < directive.range
        directive.dormant_color = libtcod.red if in_range else libtcod.grey
        to_draw = directive.phrase

        for i, char in enumerate(to_draw):
            shade_amount = iteration - i
            color = directive.current_color - self.color_add * (shade_amount)
            if color == libtcod.black and i == len(to_draw) - 1:
                return False
            x, y = self.camera.to_camera_coordinates(directive.x + i, directive.y)
            if True:#not self.game.the_map.run_collision(x, y): 
                    # dunno about the above, visuals-wise
                libtcod.console_set_default_foreground(directive.con, color)
                libtcod.console_put_char(directive.con, x, y, 
                                                char, libtcod.BKGND_NONE)

        return True

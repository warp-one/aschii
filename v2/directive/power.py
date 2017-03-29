import libtcodpy as libtcod

import settings
from directive import Directive


class Power(Directive):

    range = 1000
    visible = True
    
    def __init__(self, *args, **kwargs):
        super(Power, self).__init__(*args, **kwargs)
        self._x, self._y = self.anchor.x, self.anchor.y
        
    @property
    def x(self):
        return self._x
        
    @x.setter
    def x(self, value):
        self._x = value

    @property
    def y(self):
        return self._y
        
    @y.setter
    def y(self, value):
        self._y = value
        
    def is_visible(self):
        return True
        
    def complete(self):
        self.reset()

    def _draw(self):
        self.dormant_color = libtcod.red 
        to_draw = self.phrase
        for i, char in enumerate(to_draw):
            x, y = self.x + i, self.y
            color = (self.current_color if self.phrase_clear[i] else self.dormant_color)
            libtcod.console_set_default_foreground(self.con, color)
            libtcod.console_put_char(self.con, x, y, 
                                            char, libtcod.BKGND_NONE)

    def clear(self):
        try:
            for i in xrange(len(self.phrase)):
                x, y = self.x + i, self.y
                libtcod.console_put_char(self.con, x, y,
                                                ' ', libtcod.BKGND_NONE)
        except TypeError:
            x, y = self.game.camera.to_camera_coordinates(self.x, self.y)
            libtcod.console_put_char(self.con, self.x, self.y,
                                            ' ', libtcod.BKGND_NONE)

 
class ItemToggle(Power):

    def __init__(self, item, *args, **kwargs):
        super(ItemToggle, self).__init__(*args, **kwargs)
        self.item = item

    @property
    def y(self):
        return settings.SCREEN_HEIGHT - 1
                
    def complete(self):
        super(ItemToggle, self).complete()
        self.item.toggle()
        self.change_text(self.item.get_toggle_text())

            
class Sprint(Power):

    sprint_distance = 20

    def complete(self):
        p = self.game.player
        player_location = p.location
        path = []
        for s in range(self.sprint_distance):
            next_tile = (p.x + p.facing[0] * (s + 1), p.y + p.facing[1] * (s + 1))
            path.append(next_tile)
        path = p.set_path(path)
        self.game.player.add_order(len(path), p.move_along_path, None)
        self.reset()
        
        
class LeaveTheCaves(Power):
    def complete(self):
        pass

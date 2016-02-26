import libtcodpy as libtcod

from directive import Directive

class Power(Directive):

    range = 1000
    visible = True

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
 
class ItemToggle(Power):

    def __init__(self, item, *args, **kwargs):
        super(ItemToggle, self).__init__(*args, **kwargs)
        self.item = item

    def complete(self):
        super(ItemToggle, self).complete()
        self.item.toggle()
        if self.item.on:
            self.change_text(self.item.offtext)
        else:
            self.change_text(self.item.ontext)
            
        
            


class Sprint(Power):

    sprint_distance = 20

    def complete(self):
        p = self.game.player
        player_location = p.get_location()
        path = []
        for s in range(self.sprint_distance):
            next_tile = (p.x + p.facing[0] * (s + 1), p.y + p.facing[1] * (s + 1))
            path.append(next_tile)
        path = p.set_path(path)
        self.game.player.add_order(len(path), p.move_along_path)
        self.reset()
        
        
class LeaveTheCaves(Power):
    def complete(self):
        self.game

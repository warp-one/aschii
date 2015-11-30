from directive import Directive

class Power(Directive):

    range = 1000

    def is_visible(self):
        return True
        
    def complete(self):
        self.reset()

 
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
    def complete(self):
        p = self.game.player
        player_location = p.get_location()
        path = []
        for s in range(p.sprint_distance):
            next_tile = (p.x + p.facing[0] * (s + 1), p.y + p.facing[1] * (s + 1))
            path.append(next_tile)
        path = p.set_path(path)
        self.game.player.add_order(len(path) * .1, p.move_along_path)
        self.reset()
        
        
class LeaveTheCaves(Power):
    def complete(self):
        self.game

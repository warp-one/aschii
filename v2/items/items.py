from inventory import Item
from directive import Directive

class Flashlight(Item):
    
    name = "flashlight"
    on = False
    ontext = "turn on"
    offtext = "turn off"
    distance = 20
    Lradius = 13
    
        
    def get_location(self):
        try:
            if self.owner:
                x, y = self.owner.get_location()
                fx, fy = self.owner.facing
                return x + fx*self.distance, y + fy*self.distance
            else:
                return super(Flashlight, self).get_location()
        except AttributeError:
            return super(Flashlight, self).get_location()
        
    def turn_on(self):
        if super(Flashlight, self).turn_on():
            self.game.the_map.light_sources.append(self)
        self.on = True
        
    def turn_off(self):
        if super(Flashlight, self).turn_off():
            self.game.the_map.light_sources.remove(self)
        self.on = False
        
    def do(self):
        if self.on:
            self.turn_off()
        else:
            self.turn_on()
            
class Gammon(Item):

    name = "gammon"
    description = "the salted hind leg of a pig"
    on = False
    ontext = "eat"
    offtext = " "
    
    def turn_on(self):
        # not hungry any more
        self.on = True
        
        
    def turn_off(self):
        return
        
    def do(self):
        if not self.on:
            self.turn_on()
        else:
            print "wrong!"
    
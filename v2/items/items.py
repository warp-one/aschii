from inventory import Item

class Flashlight(Item):
    
    name = "flashlight"
    distance = 20
    Lradius = 13
    
    def turn_on(self):
        self.on = True
        self.game.the_map.light_sources.append(self)
        
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
        
    def turn_off(self):
        self.on = False
        self.game.the_map.light_sources.remove(self)
        
    def do(self):
        if self.on:
            self.turn_off()
        else:
            self.turn_on()
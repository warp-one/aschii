from inventory import Item

class Flashlight(Item)
    
    name = "flashlight"
    distance = 10
    
    def turn_on(self):
        self.game.the_map.light_sources.append(self)
        
    def get_location(self):
        x, y = self.owner.get_location()
        fx, fy = self.owner.facing
        return x + fx*self.distance, y + fy*self.distance
        
    def turn_off(self):
        self.game.the_map.light_sources.remove(self)
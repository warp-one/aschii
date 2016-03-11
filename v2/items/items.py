import libtcodpy as libtcod

from inventory import Item


class Flashlight(Item):
    
    name = "flashlight"
    on = False
    distance = 20
    Lradius = 5
    
        
    def location(self):
        try:
            if self.owner:
                x, y = self.owner.location
                fx, fy = self.owner.facing
                return x + fx*self.distance, y + fy*self.distance
            else:
                return super(Flashlight, self).location
        except AttributeError:
            return super(Flashlight, self).location

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

            
class Lamp(Item):

    name = "Candelabra"
    on = False
    ontext = "light"
    offtext = "snuff"
    Lradius = 6
    
    def __init__(self, *args):
        super(Lamp, self).__init__(*args)

        self.image = libtcod.image_load('comics/candle.png')

    def pick_up(self, owner):
        super(Lamp, self).pick_up(owner)
        self.owner.trail.add_message("This candelabra can plug in anywhere, but if you move, the cord may come out of the socket...")
        self.owner.trail.begin_message()


    def turn_on(self):
        if super(Lamp, self).turn_on():
            action = self.owner.change_sight_radius
            brightening = (3, action, [self.Lradius/3])
            self.owner.add_order(*brightening)
        self.on = True
        
    def turn_off(self):
        if super(Lamp, self).turn_off():
            self.owner.change_sight_radius(-100)
        self.on = False
        
    def do(self):
        if self.on:
            self.turn_off()
        else:
            self.turn_on()
        self.game.the_map.schimb()
        
    def put_away(self):
        super(Lamp, self).put_away()
        self.turn_off()
    

class Idol(Item):

    name = "Figurine"
    on = False
    ontext = "appeal"
    offtext = "deface"
    
    def __init__(self, *args):
        super(Idol, self).__init__(*args)

        self.image = libtcod.image_load('comics/cycl.png')

    def turn_on(self):
        self.on = True
        
    def turn_off(self):
        self.on = False
        
    def do(self):
        if self.on:
            self.turn_off()
        else:
            self.turn_on()


class Lute(Item):

    name = "gittern"
    on = False
    ontext = "play"
    offtext = "mute"

    def __init__(self, *args):
        super(Lute, self).__init__(*args)

        self.image = libtcod.image_load('comics/lute.png')

    def turn_on(self):
        self.on = True

    def turn_off(self):
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

    def __init__(self, *args):
        super(Gammon, self).__init__(*args)

        self.image = libtcod.image_load('comics/ham.png')

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

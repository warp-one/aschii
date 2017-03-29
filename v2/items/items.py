import libtcodpy as libtcod

from tile import EnvironmentTile


class Item(EnvironmentTile):

    name = "Generic Item"
    description = "an item"
    ontext = "turn on"
    offtext = "turn off"

    def __init__(self, *args):
        super(Item, self).__init__(*args)
        self.on = False
        self.owner = None
        
        self.image = libtcod.image_load('comics/cycl.png')

    def pick_up(self, owner):
        self.toggle_visible()
        self.owner = owner
        self.game.the_map.remove(self)
        
    def put_down(self):
        self.toggle_visible()
        self.x, self.y = self.owner.location
        self.owner = None
        self.game.the_map.add(self.x, self.y, self)
        self.turn_off()

    def turn_on(self):
        if self.on:
            return False
        else:
            self.on = True
            return True
        
    def turn_off(self):
        if not self.on:
            return False
        else:
            self.on = False
            return True
            
    def toggle(self):
        if self.on:
            self.turn_off()
        else:
            self.turn_on()

    def get_toggle_text(self):
        if self.on:
            return self.offtext
        else:
            return self.ontext
        
    def equip(self):
        print "You equip your " + self.name
        
    def put_away(self):
        print "You put away your " + self.name

    def do(self):
        print "Boink!"
        
    def _draw(self):
        try:
            if self.owner:
                return
            else:
                return super(Item, self)._draw()
        except AttributeError:
            return super(Item, self)._draw()
            
                        
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

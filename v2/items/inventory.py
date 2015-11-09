import libtcodpy as libtcod

from tile import EnvironmentTile

class Inventory(object):

    next_item_key = libtcod.KEY_SPACE
    item_keys = []

    def __init__(self, owner):
        self.owner = owner
        self.inventory = []
        self.item_number = 0
        self.current_item = None
        
    def pick_up_item(self, item):
        if item:
            item.pick_up(self.owner)
            self.inventory.append(item)
            print "pickin up"
        else:
            print "No item to pick up!"
        
    def drop_item(self, item):
        item.put_down()
        self.inventory.remove(item)
        
    def switch_item(self):
        previous_item = self.current_item
        if not self.current_item:
            if self.inventory:
                self.current_item = self.inventory[0]
            else:
                self.current_item = None
        else:
            self.item_number += 1
            if self.item_number >= len(self.inventory):
                self.item_number = 0
            self.current_item = self.inventory[self.item_number]
        if self.current_item:
            self.current_item.equip()
            self.current_item.turn_on()
        if previous_item:
            previous_item.put_away()

class Item(EnvironmentTile):

    name = "Generic Item"
    
    def pick_up(self, owner):
        self.toggle_visible()
        self.owner = owner
        print "we got it"
        
    def put_down(self):
        self.x, self.y = self.owner.get_location()
        self.owner = None
        self.toggle_visible()

    def turn_on(self):
        pass
        
    def turn_off(self):
        pass
        
    def equip(self):
        print "You equip your " + self.name
        
    def put_away(self):
        print "You put away your " + self.name
        
    def _draw(self):
        try:
            if self.owner:
                return
            else:
                return super(Item, self)._draw()
        except AttributeError:
            return super(Item, self)._draw()
        
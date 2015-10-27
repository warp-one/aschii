import libtcodpy as libtcod

class Inventory(object):

    next_item_key = libtcod.KEY_SPACE
    item_keys = []

    def __init__(self):
        self.inventory = []
        self.item_number = 0
        self.current_item = None
        
    def pick_up_item(self, item):
        item.toggle_visible()
        self.inventory.append(item)
        
    def drop_item(self, item):
        item.toggle_visible()
        self.inventory.remove(item)
        
    def switch_item(self):
        if not self.current_item:
            if self.inventory:
                self.current_item = self.inventory[0]
        else:
            self.item_number += 1
            if self.item_number >= len(self.inventory):
                self.item_number = 0
            self.current_item = self.inventory[self.item_number]
    

class Item(object):
    def turn_on(self):
        pass
        
    def turn_off(self):
        pass


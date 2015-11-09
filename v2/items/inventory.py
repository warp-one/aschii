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

        self.display = InventoryDisplay(self.owner.game.the_map, self.owner.con)
        self.owner.game.hud.append(self.display)
        
    def pick_up_item(self, item):
        if item:
            item.pick_up(self.owner)
            self.inventory.append(item)
            if len(self.inventory) == 1:
                self.switch_item()
            return True
        else:
            print "No item to pick up!"
            return False
        
    def drop_item(self):
        if self.current_item:
            self.current_item.put_down()
            self.inventory.remove(self.current_item)
            self.current_item = None
            self.switch_item()
        else:
            print "No item in hand!"
        
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
        if previous_item:
            previous_item.put_away()
        if self.current_item:
            self.current_item.equip()
            self.current_item.turn_on()
        self.display.cycle_display(self.current_item)

    def toggle_item(self):
        if self.current_item:
            self.current_item.do()

class InventoryDisplay(object):

    length = 20

    def __init__(self, game_map, con):
        self.x = game_map.width - self.length
        self.y = game_map.height - 1
        self.con = con

        self.current_item = None
        self.text = ""
        self.status = ""

        self.color = libtcod.blue
        self.current_color = self.color

    def cycle_display(self, item):
        self.current_item = item
        if self.current_item:
            self.text = item.name
        else:
            self.text = ""
            self.status = ""

    def draw(self):
        if not self.current_item:
            return
        item = self.current_item
        colon = ":"
        color = (item.current_color if item.on else libtcod.grey)
        for i, char in enumerate(self.text + colon):
            x, y = self.x + i, self.y
            libtcod.console_set_default_foreground(self.con, color)
            libtcod.console_put_char(self.con, x, y, 
                                            char, libtcod.BKGND_NONE)

        for i, char in enumerate(self.status):
            x, y = self.x + len(self.text) + 2 + i, self.y
            libtcod.console_set_default_foreground(self.con, color)
            libtcod.console_put_char(self.con, x, y, 
                                            char, libtcod.BKGND_NONE)

    def update(self):
        if self.current_item:
            if self.current_item.on:
                self.status = "on"
            else:
                self.status = "off"

class Item(EnvironmentTile):

    name = "Generic Item"

    def __init__(self, *args):
        super(Item, self).__init__(*args)
        self.on = False
    
    def pick_up(self, owner):
        self.toggle_visible()
        self.owner = owner
        self.game.the_map.remove(self)
        
    def put_down(self):
        self.toggle_visible()
        self.x, self.y = self.owner.get_location()
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
        
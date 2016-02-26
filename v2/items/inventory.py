import libtcodpy as libtcod

import settings
from tile import EnvironmentTile
from directive import ItemGrab, ItemToggle, Directive, Power

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
            self.owner.add_child(ItemGrab(self.current_item, self.owner.game, text="pick up", offset = (-2, 2)))
            self.inventory.remove(self.current_item)
            self.current_item = None
            self.switch_item()
        else:
            print "No item in hand!"
        
    def switch_item(self):
        #TODO: make a legible sequence of functions rather than this unholiness
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
#            self.current_item.turn_on()
        self.display.cycle_display(self.current_item)
        
        if self.current_item and previous_item is not self.current_item:
            display_location = self.display.get_toggle_location()
            x = display_location[0] - self.owner.x
            y = display_location[1] - self.owner.y
            for d in self.owner.children:
                if isinstance(d, ItemToggle):
                    self.owner.remove_child(d)
                    d.clear()
                    del d
            self.owner.add_child(ItemToggle(self.current_item, 
                    self.owner, 
                    self.owner.game, 
                    text=(self.current_item.offtext if self.current_item.on else self.current_item.ontext), 
                    static=True, 
                    offset=(x, y)))
        elif self.current_item is None:
            for d in self.owner.children:
                if isinstance(d, ItemToggle):
                    self.owner.remove_child(d)
                    d.clear()
                    del d

            
            
    def toggle_item(self):
        if self.current_item:
            self.current_item.do()

class InventoryDisplay(object):

    length = 20

    def __init__(self, game_map, con):
        self.x = settings.SCREEN_WIDTH - self.length
        self.y = settings.SCREEN_HEIGHT - 1
        self.con = con

        self.current_item = None
        self.on_off_switch = None
        self.text = ""
        self.status = ""

        self.color = libtcod.blue
        self.current_color = self.color

    def cycle_display(self, item):
        self.clear()
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
#        if self.current_item.on:
#            self.current_item.item_toggle.change_text(self.current_item.offtext)
#            self.status = self.current_item.offtext
#        else:
#            self.current_item.item_toggle.change_text(self.current_item.ontext)
 #           self.status = self.current_item.ontext
            
#        for i, char in enumerate(self.status):
#            x, y = self.x + len(self.text) + 2 + i, self.y
#            libtcod.console_set_default_foreground(self.con, color)
#            libtcod.console_put_char(self.con, x, y, 
#                                            char, libtcod.BKGND_NONE)
        #libtcod.image_blit_rect(self.current_item.image, self.con, 0, 0, -1, -1, libtcod.BKGND_SET)                                    
        x, y = settings.SCREEN_WIDTH - 10, settings.SCREEN_HEIGHT - 11
        libtcod.image_blit_2x(self.current_item.image, self.con, x, y, 0, 0, -1, -1)
                                            
    def clear(self):
        for i, char in enumerate(self.text + ":"):
            x, y = self.x + i, self.y
            libtcod.console_put_char(self.con, x, y, 
                                            ' ', libtcod.BKGND_NONE)

                                            
    def get_toggle_location(self):
        return self.x + len(self.text) + 2, self.y

    def update(self):
        if False:#self.current_item:
            if self.current_item.on:
                self.status = "on"
            else:
                self.status = "off"

class Item(EnvironmentTile):

    name = "Generic Item"
    description = ""

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
            
    def toggle(self):
        if self.on:
            self.turn_off()
        else:
            self.turn_on()
        
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
        

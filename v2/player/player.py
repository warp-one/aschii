import libtcodpy as libtcod

import tools
from actions import ActionManager
from directive import Directive, PlayerArrow, SCHIMB, Legs, PlayerWASD
from items import Inventory
from observer import Listener
from tile import Unit

class Orders(object):
    def create_orders(self):
        self.orders = [] # (t, callable)
        self.current_action = None
        self.time_left = 0
        self.path = []
        
    def act(self):
        if self.current_action:
            self.current_action()
            self.time_left -= .1
            if self.time_left <= 0:
                self.end_action()
        else:
            if self.orders:
                self.time_left, self.current_action = self.orders.pop(0)
                
    def add_order(self, time, order):
        self.orders.append((time, order))
        
    def move_along_path(self):
        try:
            next_tile = self.path.pop(0)
        except IndexError:
            self.end_action()
            return
        dx = next_tile[0] - self.x
        dy = next_tile[1] - self.y
        if self.game.the_map.run_collision(self.x + dx, self.y + dy):
            self.end_action()
            return
        self.move(dx, dy)
        
    def set_path(self, path):
        self.path = path
        return self.path
        
    def get_path(self, start, finish):
        self.path = []
        x_dif = finish[0] - start[0] 
        y_dif = finish[1] - start[1]
        if x_dif: 
            x_sign = x_dif/abs(x_dif)
        else:
            x_sign = 1
        for x in range(x_sign, x_dif + 1, x_sign):
            self.path.append((start[0] + x, start[1]))
        if y_dif: 
            y_sign = y_dif/abs(y_dif)
        else:
            y_sign = 1
        for y in range(y_sign, y_dif + 1, y_sign):
            self.path.append((start[0] + x_dif, start[1] + y))
        return self.path
        
    def end_action(self):
        self.current_action = None
        self.time_left = 0
            
    def update(self):
        pass
    
    
class Player(Listener, Orders, Unit):

    arrow_keys = [libtcod.KEY_UP, libtcod.KEY_DOWN,
                  libtcod.KEY_RIGHT, libtcod.KEY_LEFT]
    offsets = [(-2, -2), (-2, 2), (2, 3), (2, -3), 
               (-2, -2), (-2, 2), (2, 3), (2, -3)]
    sight_radius = 21 #high in early levels, low in late...
    char = ' '

    def __init__(self, *args):
        self.blocked = False
        super(Player, self).__init__(*args)
        self.action_manager = ActionManager(self)
        self.inventory = Inventory(self)

        self.next_offset = 0
        self.facing = (1, 0)
        self.powers = None
        
        self.create_orders()
        self.obs = []

        self.arrows = {libtcod.CHAR_ARROW_N:None, libtcod.CHAR_ARROW_S:None, 
                       libtcod.CHAR_ARROW_E:None, libtcod.CHAR_ARROW_W:None}
        self.set_arrows()
        self.add_child(PlayerWASD(self, self.game))
        
        
        
    def set_arrows(self):
        NSEW = {(0, 4): libtcod.CHAR_ARROW_N, 
                (0, -4): libtcod.CHAR_ARROW_S, 
                (4, 0): libtcod.CHAR_ARROW_E, 
                (-4, 0): libtcod.CHAR_ARROW_W} 
        for offset, char in NSEW.iteritems():
            newD = PlayerArrow(self, self.game, text=char)
            self.add_child(newD, offset=offset)
            self.add_arrow(newD)
            
        self.legs = Legs(self, self.game)
        self.add_child(self.legs, offset=(0, 0))
        
    def add_arrow(self, arrow):
        self.arrows[arrow.phrase] = arrow

    def handle_keys(self):
        for a in self.arrows.values():
            if a:
                a.pressed = False
        dx, dy = 0, 0
        key = libtcod.console_check_for_keypress()  #real-time
        
        is_char = (key.vk == libtcod.KEY_CHAR)
        is_arrow = (key.vk in self.arrow_keys)
        is_space = (key.vk == libtcod.KEY_SPACE)
        if is_char or is_arrow or is_space:
            self.action_manager.handle_letter(key)
     
        if key.vk == libtcod.KEY_ENTER and key.lalt:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
        elif key.vk == libtcod.KEY_ESCAPE:
            return True  #exit game
        elif key.vk == libtcod.KEY_CONTROL:
            if self.inventory.pick_up_item(self.game.the_map.get_item(*self.get_location())):
                pass
            else:
                self.inventory.toggle_item()
        elif key.vk == libtcod.KEY_TAB:
            self.inventory.switch_item()
        elif key.vk == libtcod.KEY_BACKSPACE:
            self.inventory.drop_item()
 
        if libtcod.console_is_key_pressed(libtcod.KEY_UP):
            self.change_direction((0, -1))
            self.move(0, -1)
            self.arrows[libtcod.CHAR_ARROW_N].pressed = True
        elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
            self.change_direction((0, 1))
            self.move(0, 1)
            self.arrows[libtcod.CHAR_ARROW_S].pressed = True
        elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
            self.change_direction((-1, 0))
            self.move(-1, 0)
            self.arrows[libtcod.CHAR_ARROW_W].pressed = True
        elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
            self.change_direction((1, 0))
            self.move(1, 0)
            self.arrows[libtcod.CHAR_ARROW_E].pressed = True
            
    def add_child(self, child, offset=None):
        super(Player, self).add_child(child, offset)
        if isinstance(child, Directive):
            self.action_manager.add_action(child)
        
    def remove_child(self, child):
        super(Player, self).remove_child(child)
        if isinstance(child, Directive):
            self.action_manager.remove_action(child)
            
    def add_power(self, power):
        if self.powers is None:
            self.powers = []
        self.add_child(power)
        self.powers.append(power)
        power.x = 0
        power.y = self.game.the_map.height - len(self.powers)
        power.update()
        
    def remove_power(self, power):
        self.remove_child(power)
        self.powers.remove(power)
        
    def change_direction(self, direction):
        self.game.the_map.schimb()
        if self.facing == direction:
            return False
        else:
            self.facing = direction
            return self.facing

    def move(self, dx, dy):
        if super(Player, self).move(dx, dy):
            self.game.the_map.move(self.x, self.y, self)
            self.fov = libtcod.map_compute_fov(self.game.the_map.libtcod_map, self.x, self.y, self.sight_radius, algo=libtcod.FOV_DIAMOND)
            if dx:
                self.change_direction((dx/abs(dx), 0))
            elif dy:
                self.change_direction((0, dy/abs(dy)))
            self.notify(None, "player move")
            
    def _draw(self):
        return

    def update(self):
        self.act()
        super(Player, self).update()
        for c in self.children:
            if not c.static:
                c.update()
                
    def on_notify(self, entity, event):
        pass
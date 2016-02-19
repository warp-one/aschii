import libtcodpy as libtcod

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
            

class Player(Listener, Orders, Unit):

    arrow_keys = [libtcod.KEY_UP, libtcod.KEY_DOWN,
                  libtcod.KEY_RIGHT, libtcod.KEY_LEFT]
    offsets = [(-2, -2), (-2, 2), (2, 3), (2, -3), 
               (-2, -2), (-2, 2), (2, 3), (2, -3)]
    sight_radius = 21 # high in early levels, low in late...
    len_step = 6 # in frames
    char = ' '
    left_foot = False
    left_foot_displacement = -1

    def __init__(self, *args):
        self.blocked = False
        super(Player, self).__init__(*args)
        self.action_manager = ActionManager(self)
        self.inventory = Inventory(self)

        self.next_offset = 0
        self.facing = (1, 0)
        self.powers = None
        self.step_timer = 0
        
        self.create_orders()
        self.obs = []

        self.arrows = {libtcod.CHAR_ARROW_N:None, libtcod.CHAR_ARROW_S:None, 
                       libtcod.CHAR_ARROW_E:None, libtcod.CHAR_ARROW_W:None}
        self.set_arrows()
        self.add_child(PlayerWASD(self, self.game))
        
        self.last_position = self.x, self.y
        self.idle_time = -90
        self.moved = False
        self.easy_move = True
        self.schimb = False

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
        self.last_position = self.get_location()
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
        if is_space:
            print self.get_location()
     
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
        x, y = direction
        self.schimb = True
        if self.facing == direction:
            return False
        else:
            self.facing = (x/abs(x) if x else 0), (y/abs(y) if y else 0)
            return self.facing

    def move(self, dx, dy):
        if super(Player, self).move(dx, dy):
            self.game.the_map.move(self.x, self.y, self)
            if dx or dy:
                self.change_direction((dx, dy))
            if self.step_timer >= self.len_step or self.moved is False:
                self.step_timer = 0
                self.take_step()
                self.moved = True
        elif self.easy_move:
            if dx:
                x, y = self.x + dx, self.y
                for tile in ((x, y + 1), (x, y - 1)):
                    if not self.game.the_map.run_collision(*tile):
                        if not self.game.the_map.run_collision(self.x, tile[1]):
                            self.move(0, tile[1] - y)
                        break
            if dy:
                x, y = self.x, self.y + dy
                for tile in ((x + 1, y), (x - 1, y)):
                    if not self.game.the_map.run_collision(*tile):
                        if not self.game.the_map.run_collision(tile[0], self.y):
                            self.move(tile[0] - x, 0)
                        break

    def _draw(self): # THE UNDERSCORE IS IMPORTANT; KEEP IT
                     # OR OTHERWISE ALL THE ACTIONS DISAPPEAR
        return

    def update(self):
        self.act()
        if self.step_timer < self.len_step:
            self.step_timer += 1
        if self.moved and self.get_location() == self.last_position:
            self.moved = False
            if self.step_timer > 5:
                self.take_step()
        super(Player, self).update()
        for c in self.children:
            if not c.static:
                c.update()
                
        dark_time = 40
        if self.last_position == self.get_location():
            self.idle_time += 1
        else:
            if self.sight_radius < 21:
                self.sight_radius += 3
                self.idle_time = 0
            else:
                self.idle_time = -50
        if self.idle_time >= dark_time:
            if self.sight_radius > 3:
                self.sight_radius -= 3
            self.schimb = True
            self.idle_time = 0
        libtcod.map_compute_fov(self.game.the_map.libtcod_map,
                    self.x, self.y, self.sight_radius, algo=libtcod.FOV_DIAMOND)

    def on_notify(self, entity, event):
        pass

    def take_step(self):
        self.notify(self, 'player move')
        if self.left_foot:
            self.left_foot = False
        else:
            self.left_foot = True

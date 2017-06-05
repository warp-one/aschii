from random import shuffle, randint

import libtcodpy as libtcod

import orders, settings, tools
from actions import ActionManager
from directive import Directive, PlayerArrow, PlayerWASD, ItemToggle, Lightener
from items import Lamp
from items import Inventory
from observer import Listener
from tile import Unit

class TextTrail(object):

    def __init__(self, tile):
        self.tile = tile
        self.tilemap = tile.game.the_map
        self.queue = []
        self.current_message = None
        self.current_letter = 0
        self.letter_offset = (0, 0)

    def add_message(self, message):
        self.queue.append(message)

    def clear_queue(self):
        self.queue = []

    def begin_message(self):
        if self.current_message:
            return "A message is already being written."
        else:
            self.current_message = self.queue.pop(0)
            self.current_offset = (randint(0, 2), randint(0, 2))

    def end_message(self):
        self.current_message = None
        self.current_letter = 0

    def write_letter(self):
        if self.current_message:
            ox, oy = self.tile.last_position
            x, y = ox + self.letter_offset[0], oy + self.letter_offset[1]
            while not self.tilemap.can_schimb(x, y):
                if x != ox: x += (ox - x)/abs(ox - x)
                elif y != oy: y += (oy - y)/abs(oy - y)
                else: break
            letter = self.current_message[self.current_letter]
            fade = [libtcod.Color(a, a, a) 
                    for a in xrange(255, libtcod.darkest_grey.r, -10)]

            self.tilemap.apply_tile_effect({(x, y):[(color, letter) for color in fade]}, mode="replace")
            self.current_letter += 1
            if self.current_letter >= len(self.current_message):
                self.end_message()
            

class Darkness(object):
    def __init__(self, darkness_style="constant"):
        self.style = darkness_style
        
    def on_notify(self, entity, event):
        if self.style == "constant":
            if event == "player darken":
                entity.schimb = self.style
            elif event == "player change direction":
                entity.schimb = self.style
        if self.style == "distance-based":
            if event == "darkness leash broken":
                entity.schimb = self.style
            if event == "lightener complete":
                entity.schimb = self.style
        if event == "directive requests schimb":
            entity.schimb = True
                
    def check_leash(self, player):
        if self.style != "distance-based":
            return
        leash_length = tools.get_distance(player.location, player.darkness_location)
        max_leash = settings.RENDER_RADIUS_CIRCLE - player.sight_radius
        if leash_length > max_leash:
            player.darkness_location = player.location
            player.schimb = self.style


class Player(Listener, orders.Orders, Unit):

    offsets = [(-2, -2), (-2, 2), (2, 3), (2, -3), 
               (-2, -2), (-2, 2), (2, 3), (2, -3)]
    sight_radius = 5 
    max_sight = settings.PLAYER_MAX_SIGHT # high in early levels, low in late...
    base_sight = max_sight/2
    sight_floor = 1
    len_step = 3 # in frames
    char = ' '
    left_foot = False
    left_foot_displacement = -1
    idle_start = 0

    def __init__(self, *args):
        self.blocked = False
        super(Player, self).__init__(*args)
        self.action_manager = ActionManager(self)
        self.inventory = Inventory(self)

        self.next_offset = 0
        self.facing = (1, 0)
        self.powers = None
        self.step_timer = 0
        self.darken_timer = 0
        
        self.create_orders()
        self.obs = []
        
        self.last_position = self.x, self.y
        self.idle_time = self.idle_start
        self.moved = False

        self.trail = TextTrail(self)
        self.components = {}
#        self.add_component("trail", TextTrail(self))
        
        darkness_style = "distance-based"
        self.schimb = darkness_style
        self.schimb_hold = False
        self.darkness = Darkness(darkness_style=darkness_style)
        self.add_observer(self.darkness)
        self.darkness_location = self.x, self.y
        
    def is_visible(self):
        return True

    def change_sight_radius(self, delta_s, set=False, noschimb=False):
        if set:
            self.sight_radius = delta_s
        else:
            self.sight_radius += delta_s
        if self.sight_radius > self.max_sight:
            self.sight_radius = self.max_sight
        elif self.sight_radius < self.base_sight:
            self.sight_radius = self.base_sight
        if not noschimb:
            self.notify(self, "player darken")
        if self.sight_radius < self.sight_floor + 3:
            self.darkness.style = "constant"
        else:
            self.darkness.style = "distance-based"
        self.idle_time = 0
        
    def change_base_sight(self, delta_s, set=False):
        if set:
            self.base_sight = delta_s
        else:
            self.base_sight += delta_s
        if self.base_sight < self.sight_floor:
            self.base_sight = self.sight_floor
        if self.base_sight > self.max_sight:
            self.base_sight = self.max_sight
        if self.sight_radius < self.base_sight:
            self.sight_radius = self.base_sight
        self.notify(self, "player darken")

    def handle_keys(self):
        self.last_position = self.location
        key = libtcod.console_check_for_keypress()  #real-time
        
        is_char = (key.vk == libtcod.KEY_CHAR)
        is_space = (key.vk == libtcod.KEY_SPACE)
        if is_char or is_space:
            self.action_manager.handle_letter(key)
     
        if key.vk == libtcod.KEY_ENTER and key.lalt:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
        elif key.vk == libtcod.KEY_ESCAPE:
            return True  #exit game
        elif key.vk == libtcod.KEY_CONTROL:
            if self.inventory.pick_up_item(
                    self.game.the_map.get_item(*self.location)
                                           ):
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
        elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
            self.change_direction((0, 1))
            self.move(0, 1)
        elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
            self.change_direction((-1, 0))
            self.move(-1, 0)
        elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
            self.change_direction((1, 0))
            self.move(1, 0)
            
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
        power.y = settings.SCREEN_HEIGHT - len(self.powers)
        power.update()
        
    def remove_power(self, power):
        self.remove_child(power)
        self.powers.remove(power)
        
    def change_direction(self, direction):
        x, y = direction
        self.notify(self, "player change direction")
        if self.facing == direction:
            return False
        else:
            self.facing = (x/abs(x) if x else 0), (y/abs(y) if y else 0)
            return self.facing

    def move(self, dx, dy, easy_move=True):
        if super(Player, self).move(dx, dy):
            self.game.the_map.move(self.x, self.y, self)
            if dx or dy:
                self.change_direction((dx, dy))
            if self.step_timer >= self.len_step or self.moved is False:
                self.step_timer = 0
                self.take_step()
                self.moved = True
        elif easy_move:
            if dx:
                x, y = self.x + dx, self.y
                destinations = [(x, y + 1), (x, y - 1)]
                shuffle(destinations)
                for tile in destinations:
                    if not self.game.the_map.run_collision(*tile):
                        if not self.game.the_map.run_collision(self.x, tile[1]):
                            self.move(0, tile[1] - y)
                            break
            if dy:
                x, y = self.x, self.y + dy
                destinations = [(x + 1, y), (x - 1, y)]
                shuffle(destinations)
                for tile in destinations:
                    if not self.game.the_map.run_collision(*tile):
                        if not self.game.the_map.run_collision(tile[0], self.y):
                            self.move(tile[0] - x, 0)
                            break

    def draw(self):
        if self.is_visible():
            self._draw()
            for c in self.children:
                if not isinstance(c, Lightener):
                    c.draw()


    def _draw(self): # THE UNDERSCORE IS IMPORTANT; KEEP IT
                     # OR OTHERWISE ALL THE ACTIONS DISAPPEAR
        return
        
    def clear(self):
        super(Player, self).clear()
        for c in self.children:
            c.clear()

    def update(self):
        self.act()
        if self.step_timer < self.len_step:
            self.step_timer += 1
        if self.moved and self.location == self.last_position:
            self.moved = False
            if self.step_timer > 5:
                self.take_step()
        super(Player, self).update()
        for c in self.children:
            c.update()
                
        if self.last_position == self.location:
            self.idle_time += 1
        else:
            equipped_item = self.inventory.current_item
            if isinstance(equipped_item, Lamp):
                if equipped_item.on:
                    for d in self.children: # INEFFICIENT?!
                        if isinstance(d, ItemToggle):
                            d.complete()
            self.change_sight_radius(-3)
            self.trail.write_letter()
            
        self.darkness.check_leash(self)

        self.darken_always()
        libtcod.map_compute_fov(self.game.the_map.libtcod_map,
                self.x, self.y, self.sight_radius, algo=libtcod.FOV_DIAMOND)
                
        self.check_schimb()
                
    def check_schimb(self):
        if self.schimb_hold is True:
            return
            
        if self.schimb:
            self.notify(self.schimb, 'player requests schimb')
        self.schimb = None

    def darken_always(self):
        if self.last_position == self.location:
            self.darken_timer += 1
        else:
            self.darken_timer += 4
        candle = self.inventory.get_item("Candelabra")
        if candle:
            if candle.on:
                return

        if self.darken_timer > 480:
            self.change_base_sight(-1)
            self.change_sight_radius(-1, noschimb=True)
            self.darken_timer = 0
#            self.trail.add_message("darker...")
#            self.trail.begin_message()
            
    def take_step(self):
        self.notify(self, 'player move')
        if self.left_foot:
            self.left_foot = False
        else:
            self.left_foot = True

from random import choice, randint

import libtcodpy as libtcod

import tools, settings, colors
from directive import Directive, DirectiveLink
from tile import Unit, PolishedFloor, BottomlessPit
from orders import Orders
import maps.drawings as dr



class ItemGrab(Directive):

    range = 2

    def complete(self):
        self.game.player.inventory.pick_up_item(self.anchor)
        super(ItemGrab, self).complete()


## The Point of Interest Directives
class Legs(Directive):
    def change_text(self, text):
        self.phrase1 = "l"
        self.phrase2 = "r"
        self.current_phrase = self.phrase1
        self.phrase_clear = [False] * len(self.current_phrase) 
        self.phrase_index = 0
        self.completed = False
        self.step_time = 10 * 3
        
    def complete(self):
        if self.current_phrase == self.phrase1:
            self.current_phrase = self.phrase2
        else:
            self.current_phrase = self.phrase1
        self.phrase_clear = [False] * len(self.current_phrase)
        self.phrase_index = 0
        self.anchor.move(*self.anchor.facing)
        self.step_time += 3
        for _ in range(self.step_time/9):
            self.anchor.move(*self.anchor.facing)
        
    def reset(self):
        self.phrase_clear = [False] * len(self.current_phrase)
        self.phrase_index = 0
        
    def tick_phrase(self, letter):
        if self.current_phrase[self.phrase_index] == letter:
            self.phrase_clear[self.phrase_index] = True
            self.phrase_index += 1
            if self.phrase_index >= len(self.current_phrase):
                self.complete()
            return True
        else:
            return False
            
    def _draw(self):
        self.step_time -= (1 if self.step_time > 0 else 0)
        return
        to_draw = self.current_phrase
        x_dir = self.anchor.facing[0]
        y_dir = self.anchor.facing[1]
        try:
            while self.game.the_map.get_tile(self.x + x_dir, self.y + y_dir).is_visible():
                if x_dir: x_dir += 1 * (x_dir/abs(x_dir))
                if y_dir: y_dir += 1 * (y_dir/abs(y_dir))
            for i, char in enumerate(to_draw):
                x, y = self.x + i + x_dir, self.y + y_dir
                if not self.game.the_map.run_collision(x, y):
                    color = (self.current_color if self.phrase_clear[i] else libtcod.red)
                    libtcod.console_set_default_foreground(self.con, color)
                    libtcod.console_put_char(self.con, x, y, 
                                                    char, libtcod.BKGND_NONE)
        except AttributeError:
            if settings._DEBUG:
                print "No tile!"
            
    def clear(self):
        pass


class Next(Directive):

    def complete(self):
        self.anchor.say_line()
#        if self.anchor.script:
#            self.reset()
#        else:
        super(Next, self).complete()


class Ban(Directive):
    def complete(self):
        super(Ban, self).complete()
        self.anchor.delete()

        
                                                
## TODO: "PLEASE" CONFIRMATION BUTTON FOR MULTIPLE CHOICE PHRASES
        
    
        
class DialogueChoice(Next):
    def complete(self):
        self.anchor.say_line(self.phrase)
        
#    def _draw(self):
#        Ploc = self.game.player.get_location()
#        Sloc = self.anchor.get_location()
#        in_range = tools.get_distance(Ploc, Sloc) < self.range
#        self.dormant_color = libtcod.red if in_range else libtcod.grey
#        to_draw = self.phrase
#        for i, char in enumerate(to_draw):
#            x, y = self.x + i, self.y
#            is_lit = self.game.the_map.tile_is_lit(*self.get_location())
#            in_fov = libtcod.map_is_in_fov(self.game.the_map.libtcod_map, self.x, self.y)
#            if not self.game.the_map.run_collision(x, y) and (is_lit or in_fov):
#                color = (self.current_color if self.phrase_clear[i] else self.dormant_color)
#                libtcod.console_set_default_foreground(self.con, color)
#                libtcod.console_put_char(self.con, x, y, 
#                                                char, libtcod.BKGND_NONE)


        
class Waypoint(Directive):

    range = 25

    def get_dormant(self):
        return False
        
    def complete(self):
#        self.completed = True
        p = self.game.player
        path = p.get_path(p.location, self.anchor.location)
        self.game.player.add_order(len(path) * .1, p.move_along_path)
        self.reset()
        
    def is_visible(self):
        player_proximity = tools.get_distance(self.location,
                                              self.game.player.location)
        return super(Waypoint, self).is_visible() and player_proximity > 7
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

            
class Statue(Unit):
    def __init__(self, *args, **kwargs):
        super(Statue, self).__init__(*args, **kwargs)
        self.blocked = True
        

class ResetStatue(Statue):

    def __init__(self, repeat_max, repeat_time, *args, **kwargs):
        super(ResetStatue, self).__init__(*args, **kwargs)
        self.repeat_count = 0
        self.repeat_max = repeat_max
        self.repeat_time = repeat_time
        
    def say_line(self, dialogue_choice):
        super(ResetStatue, self).say_line(dialogue_choice)
        if self.line != self.script["start"]:
            self.repeat_count += 1
            if self.repeat_count > self.repeat_max and self.repeat_max != 0:
                self.script["start"] = (self.script["newchoices"], self.script["start"][1])
            if not self.keywords:
                self.update_queue.append((self.repeat_time, self.say_line, ["start"]))


class MovingStatue(Orders, ResetStatue):

    def __init__(self, *args, **kwargs):
        self.create_orders()
        super(MovingStatue, self).__init__(*args, **kwargs)
        self.repeat_max = 0

    def say_line(self, dialogue_choice):
        super(MovingStatue, self).say_line(dialogue_choice)
        newX, newY = self.x + randint(-5, 5), self.y + randint(-5, 5)
        walk_path = libtcod.path_new_using_map(self.game.the_map.libtcod_map, 0.0)
        libtcod.path_compute(walk_path, self.x, self.y, newX, newY)
        path_steps = libtcod.path_size(walk_path)
        path_coords = [libtcod.path_get(walk_path, x) for x in range(path_steps)]
        self.set_path(path_coords)
        libtcod.path_delete(walk_path)
        self.add_order(path_steps, self.move_along_path, None)
        
    def update(self):
        super(MovingStatue, self).update()
        self.act()


class RealPerson(Statue): # inherits from statue (!)


    def __init__(self, *args, **kwargs):
        super(RealPerson, self).__init__(*args, **kwargs)
        self.phrase = [libtcod.CHAR_DVLINE, libtcod.CHAR_DTEES, choice(['o', 'O', libtcod.CHAR_BLOCK2])]
        self.vertical = True
        
        
class LinkedStatue(Statue):
    def __init__(self, *args, **kwargs):
        super(LinkedStatue, self).__init__(*args, **kwargs)
        self.current_color = libtcod.purple
        self.honored = False
        self.matched = False
        self.links = []
        
    def add_link(self, statue):
        self.links.append(statue)
            
    def check_links(self, attribute):
        for l in self.links:
            if not getattr(l, attribute):
                return False
        return True
        
        
class BridgeBuilder(Statue):

    bridge_map_location = 148, 80

    def __init__(self, *args, **kwargs):
        super(BridgeBuilder, self).__init__(*args, **kwargs)
        self.effect_frames = {}
        appear_effect = dr.bridge_effect
        frames = appear_effect.get_frame_data()
        self.shape = self.get_shape(frames)
        self.shiny = True

    def get_shape(self, frames):
        shape = []
        bmx, bmy = self.bridge_map_location
        for f in frames:
            shape_coord = f[0] + bmx, f[1] + bmy
            self.effect_frames[shape_coord] = [char for (color, char) in frames[f] if color == libtcod.Color(0, 0, 0)]
            if len(self.effect_frames[shape_coord]) == 0:
                continue
            shape.append(shape_coord)
        return shape

    def do(self):
        if self.shiny:
            for x, y in self.shape:
                changed_tile = self.game.the_map.change_tile(x, y, False,
                    char=libtcod.CHAR_BLOCK2, schimb=False, tile_type=PolishedFloor)
                changed_tile.char_queue.extend(self.effect_frames[changed_tile.location])

            self.shiny = False
        else:
            for x, y in self.shape:
                self.game.the_map.revert_tile(x, y)
            self.shiny = True


    def update(self):
        super(BridgeBuilder, self).update()

            
class Television(Statue):
    def __init__(self, *args, **kwargs):
        super(Television, self).__init__(*args, **kwargs)
        gifs = ("maps/trees-loop.gif", "maps/porn-loop.gif", "maps/sun-loop.gif")
        self.channels = [dr.SpecialEffect(dr.GifReader(gif).get_frame_data(), (self.x, self.y))
                            for gif in gifs]
        self.current_channel = 0
        self.start_channel()
        self.blocked = False
        
    def start_channel(self):
        c = self.channels[self.current_channel]
        self.game.special_effects.append(c)
        c.begin(self.game.the_map)
        print c
    
    def stop_channel(self):
        c = self.channels[self.current_channel]
        self.game.special_effects.remove(c)
        c.complete(self.game.the_map)
        
    def next_channel(self):
        self.stop_channel()
        self.current_channel += 1
        if self.current_channel >= len(self.channels):
            self.current_channel = 0
        self.start_channel()
        
    def prev_channel(self):
        self.stop_channel()
        self.current_channel -= 1
        if self.current_channel < 0:
            self.current_channel = len(self.channels) - 1
        self.start_channel()
    
    def _draw(self):
        pass
    
class BranchingStory(Statue):
    def __init__(self, story_tree, *args, **kwargs):
        super(BranchingStory, self).__init__(*args, **kwargs)
        self.branches = {}
        self.story_tree = story_tree
        self.current_branch = None
            
    def grow_branch(self, tag, branch):
        self.branches[tag] = branch
        branch.visible = False
        if self.current_branch is None:
            self.activate_branch(tag)
            
    def activate_branch(self, tag):
        if tag is None:
            self.current_branch is None
            return
        self.current_branch = self.branches[tag]
        self.current_branch.visible = True
        
    def next_branch(self):
        self.current_branch.visible = False
        self.activate_branch(self.story_tree[self.current_branch.phrase])
    
    def do(self):
        self.next_branch()
            
## TRASH BIN | | |
## (unused)  V V V
            
            

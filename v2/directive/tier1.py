from random import choice, randint
from collections import deque

import libtcodpy as libtcod

import tools, settings, colors
from directive import Directive, DirectiveLink
from tile import Unit, Tile
from orders import Orders



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
        

class Lightener(Directive):
    #should only appear in fixed places, and each disappear after you use it once
    
    script = deque([("light", "Find the light."),
                    ("lantern", "Light me a lantern."),
                    ("illumination", "A mysterious illumination...")]
                   )
    nodes = [(x, x) for x in range(10, 60, 10)]

    def __init__(self, *args, **kwargs):
        super(Lightener, self).__init__(*args, **kwargs)
        self.color = libtcod.black
        self.dormant_color = libtcod.light_grey
        self.current_color = self.color
        self.coords = []
        self.active_node = None
        self.rotate_text()
        
    def rotate_text(self):
        new_keyword, new_sentence = self.script[0]
        self.script.rotate(1)
        self.change_text(new_keyword, sentence = new_sentence)

    def complete(self):
        self.game.player.change_min_sight(2)
        self.game.player.darken_timer = 0
        self.rotate_text()
        self.reset()
        self.visible = False
        
        self.nodes.remove(self.active_node)
        self.active_node = None
        
    def is_visible(self):
        return self.visible
        
    def draw(self):
        for n in self.nodes:
            if tools.get_distance(self.anchor.location, n
                                    ) < self.anchor.sight_radius:
                if self.visible:
                    self.active_node = n
                break
            else:
                self.visible = False
                self.active_node = None
        else:
            if not self.nodes:
                self.visible = False
                self.active_node = None
        super(Lightener, self).draw()

    def _draw(self):
        self.dormant_color = (libtcod.darkest_grey * .5 
                                if not randint(0, 20) 
                                else libtcod.darkest_grey)
        self.phrase_color = (libtcod.Color(*choice(colors.fire_colorset)) 
                                if not randint(0, 15) 
                                else self.dormant_color)
        to_draw = self.sentence 
        keyword_position = to_draw.find(self.phrase)
        for i, char in enumerate(to_draw):
            x, y = self.coords[i]
            if tools.get_distance((x, y), self.game.player.location) > self.game.player.min_sight:
                color = self.dormant_color * .5
            else:
                color = self.dormant_color
            x, y = self.game.camera.to_camera_coordinates(x, y)
            
            keyword_color_index = i - keyword_position
            
            if keyword_color_index < 0 or keyword_color_index > len(self.phrase) - 1:
                pass
            else:
                color = (self.current_color 
                            if self.phrase_clear[keyword_color_index] 
                            else self.phrase_color)
                
            libtcod.console_set_default_foreground(self.con, color)
            libtcod.console_put_char(self.con, x, y, 
                                            char, libtcod.BKGND_NONE)
                                            

    def update(self):
        pass

                                            
class Ban(Directive):
    def complete(self):
        super(Ban, self).complete()
        self.anchor.delete()

        
class Bow(Directive):
    def __init__(self, *args, **kwargs):
        self.blue = False
        super(Bow, self).__init__(*args, **kwargs)

    def tick_phrase(self, letter):
        if self.blue:
            if not self.anchor.links:
                self.delete()
            return
        else:
            return super(Bow, self).tick_phrase(letter)

    def complete(self):
        self.anchor.honored = True
        self.blue = True
        if self.anchor.check_links("honored"):
            super(Bow, self).complete()
            self.anchor.delete()
            
    def _draw(self):
        if self.blue:
            self.current_color = libtcod.blue + libtcod.grey
        else:
            self.current_color = self.color
        super(Bow, self)._draw()
            
    def reset(self):
        if not self.blue:
            super(Bow, self).reset()
            
class Dismiss(Directive):
    def complete(self):
        self.anchor.honored = True
        self.blue = True
        for l in self.anchor.links:
            l.delete()
        
            
class WordMatch(Bow):
    def __init__(self, words, *args, **kwargs):
        self.blue = False
        self.words = words
        self.phrase = self.words.pop(0)
        self.keyword = self.phrase
        super(Bow, self).__init__(*args, **kwargs)
        self._change_text()
        
    def change_text(self, _):
        self._change_text()
        
    def _change_text(self):
        self.words.append(self.phrase)
        self.phrase = self.words.pop(0)
        self.reset()
        
    def complete(self):
        self._change_text()
        if self.phrase == self.keyword:
            self.anchor.matched = True
            if self.anchor.check_links("matched"):
                pass
                print "DO THE THING"
        else:
            self.anchor.matched = False
    
    def reset(self):
        self.phrase_clear = [False] * len(self.phrase)
        self.phrase_index = 0
        self.completed = False
        
    def _draw(self):
        Ploc = self.game.player.location
        Sloc = self.anchor.location
        in_range = tools.get_distance(Ploc, Sloc) < self.range
        self.dormant_color = libtcod.red if in_range else libtcod.grey
        to_draw = self.phrase
        x_minus = self.phrase.index(self.anchor.char.lower())
        in_fov = libtcod.map_is_in_fov(self.game.the_map.libtcod_map, self.x, self.y)
        for i, char in enumerate(to_draw):
            x, y = Sloc[0] + i - x_minus, Sloc[1]
            if (x, y) == self.anchor.location:
                continue
            x, y = self.game.camera.to_camera_coordinates(x, y)
            if (in_range or in_fov) and not (x, y) == self.anchor.location:
                color = (self.current_color if self.phrase_clear[i] else self.dormant_color)
                libtcod.console_set_default_foreground(self.con, color)
                libtcod.console_put_char(self.con, x, y, 
                                                char, libtcod.BKGND_NONE)
                                                
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

class PlayerArrow(Directive):
    def change_text(self, text):
        self.phrase = text
        self.phrase_clear = [False]
        self.phrase_index = 0
        self.completed = False

    def _draw(self):
        return
        if self.game.the_map.run_collision(self.x, self.y):
            return
        char = chr(self.phrase)
        color = (self.current_color if self.pressed else libtcod.red)
        libtcod.console_set_default_foreground(self.con, color)
        libtcod.console_put_char(self.con, self.x, self.y, 
                                        char, libtcod.BKGND_NONE)
                                        
    def tick_phrase(self, letter):
        return

        
class PlayerWASD(Directive):
    def _draw(self):
        pass
           
    def tick_phrase(self, letter):
        if letter == 'W':
            self.anchor.facing = (0, -1)
        if letter == 'A':
            self.anchor.facing = (-1, 0)
        if letter == 'S':
            self.anchor.facing = (0, 1)
        if letter == 'D':
            self.anchor.facing = (1, 0)

           
class SCHIMB(Directive): # Deprecated, and non-functional
    def __init__(self, indices, *args, **kwargs):
        super(SCHIMB, self).__init__(*args, **kwargs)
        self.coordinates = []
        for i in indices:
            self.coordinates.append(tools.get_xy_from_index(i, len(self.game.tilemap[0])))
        self.color2 = libtcod.blue - libtcod.grey
        self.color = libtcod.blue - libtcod.red
        self.revert_color()
            
        to_draw = zip(self.phrase, self.coordinates)
    def draw(self):
        for i, letter in enumerate(to_draw):
            x, y = letter[1][0], letter[1][1]
            color = (self.current_color if self.phrase_clear[i] else self.color2)
            if libtcod.map_is_in_fov(self.game.the_map.libtcod_map, x, y):
                libtcod.console_set_default_foreground(self.con, color)
                libtcod.console_put_char(self.con, x, y, 
                                                letter[0], libtcod.BKGND_NONE)
                                            
    def complete(self):
        super(SCHIMB, self).complete()
        self.game.the_map.schimb()

        
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
        
        

class SpeakingObject(Unit):

    line_index_by_num_words = {1:(1,), 2:(1, 0), 3:(1, 0, -1), 4:(1, 0, 0, -1),
                               5:(1, 1, 0, 0, -1), 6:(1, 1, 0, 0, -1, -1),
                               7:(1, 1, 0, 0, 0, -1, -1)}

    def __init__(self, script, *args):
        self.loop = False
        self.script = script
        self.words = []
        self.nextwords = []
        self.line = ""
        
        super(SpeakingObject, self).__init__(*args)
        self.say_line("start")
        
    def say_line(self, dialogue_choice):
        # {"start":("town city", 'I will go to town or city')}
        if self.script:
            self.line = self.script[dialogue_choice]
            self.keywords = self.line[0].split()
            individual_words = self.line[1].split()
            if self.loop:
                if not self.keywords:
                    self.keywords = ["start"]
                    individual_words.extend([">", "start"])

            for nw in self.nextwords:
                try:
                    self.game.player.remove_child(nw)
                except ValueError:
                    pass
            self.nextwords = []
            self.words = []
 
            for i, w in enumerate(individual_words):
                x = self.x + (len(individual_words[i-1]) + 1 if i%2 else 0)
                x -= len(individual_words[0])
                y = self.y + i/2
                if w in self.keywords:
                    x = x - self.x
                    y = y - self.y
                    choice = DialogueChoice(self, self.game, static=True, text=w, offset=(x, y))
                    self.nextwords.append(choice)
                    self.game.player.add_child(choice)
                    continue
                next_word = Tile(x, y, ' ', libtcod.grey, self.con, self.game, phrase=w)
                self.words.append(next_word)
                
                    
    def draw(self):
        for w in self.words:
            if self.is_visible():
                w._draw()
        super(SpeakingObject, self).draw()
            
    def clear(self):
        super(SpeakingObject, self).clear()
        for w in self.words:
            w.clear()
        for n in self.nextwords:
            n.clear()

class Statue(SpeakingObject):
    def __init__(self, *args, **kwargs):
        super(Statue, self).__init__(*args, **kwargs)
        self.blocked = True
        
        
class LStatue(Statue):
    def clear(self):
        super(LStatue, self).clear()
        
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
            
class AnnoyStatue(ResetStatue):
    pass
        
class RealPerson(Statue): # inherits from statue (!)


    def __init__(self, *args, **kwargs):
        super(RealPerson, self).__init__(*args, **kwargs)
        self.phrase = [choice(['o', 'O', libtcod.CHAR_BLOCK2]), libtcod.CHAR_DTEES, libtcod.CHAR_DVLINE]

    def clear(self):
        for i, char in enumerate(self.phrase):
            x, y = self.game.camera.to_camera_coordinates(self.x, self.y + i)
            libtcod.console_put_char(self.con, x, y, 
                                           ' ', libtcod.BKGND_NONE)
        for c in self.children:
            c.clear()
        for w in self.words:
            w.clear()
        for n in self.nextwords:
            n.clear()
        
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
        

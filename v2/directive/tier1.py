import libtcodpy as libtcod

import tools
from directive import Directive
from tile import Unit, Word



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
        
    def complete(self):
        if self.current_phrase == self.phrase1:
            self.current_phrase = self.phrase2
        else:
            self.current_phrase = self.phrase1
        self.phrase_clear = [False] * len(self.current_phrase)
        self.phrase_index = 0
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
        
class Bow(Directive):

    def __init__(self, *args, **kwargs):
        super(Bow, self).__init__(*args, **kwargs)
        self.blue = False

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
        
class DialogueChoice(Next):
    def complete(self):
        self.anchor.say_line(self.phrase)
        self.game.player
        
    def _draw(self):
        Ploc = self.game.player.get_location()
        Sloc = self.anchor.get_location()
        in_range = tools.get_distance(Ploc, Sloc) < self.range
        self.dormant_color = libtcod.red if in_range else libtcod.grey
        to_draw = self.phrase
        for i, char in enumerate(to_draw):
            x, y = self.x + i, self.y
            is_lit = self.game.the_map.tile_is_lit(*self.get_location())
            in_fov = libtcod.map_is_in_fov(self.game.the_map.libtcod_map, self.x, self.y)
            if not self.game.the_map.run_collision(x, y) and (is_lit or in_fov):
                color = (self.current_color if self.phrase_clear[i] else self.dormant_color)
                libtcod.console_set_default_foreground(self.con, color)
                libtcod.console_put_char(self.con, x, y, 
                                                char, libtcod.BKGND_NONE)

class PlayerArrow(Directive):
    def change_text(self, text):
        self.phrase = text
        self.phrase_clear = [False]
        self.phrase_index = 0
        self.completed = False

    def _draw(self):
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
           
class SCHIMB(Directive):
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
        path = p.get_path(p.get_location(), self.anchor.get_location())
        self.game.player.add_order(len(path) * .1, p.move_along_path)
        self.reset()
        
    def is_visible(self):
        player_proximity = tools.get_distance(self.get_location(), 
                                            self.game.player.get_location())
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
        # "start":("town city", 'I will go to town or city')
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
                next_word = Word(w, x, y, ' ', libtcod.grey, self.con, self.game)
                self.words.append(next_word)

                    
    def draw(self):
        super(SpeakingObject, self).draw()
        for w in self.words:
            w.draw()
            
    def clear(self):
        for w in self.words:
            w.clear()
        for n in self.nextwords:
            n.clear()

class Statue(SpeakingObject):
    def __init__(self, *args, **kwargs):
        super(Statue, self).__init__(*args, **kwargs)
        self.char = libtcod.CHAR_DVLINE
        self.blocked = True
        
        
class LinkedStatue(Statue):
    def __init__(self, *args, **kwargs):
        super(LinkedStatue, self).__init__(*args, **kwargs)
        self.char = libtcod.CHAR_TEES
        self.current_color = libtcod.purple
        self.honored = False
        self.links = []
        
    def add_link(self, statue):
        self.links.append(statue)
            
    def check_links(self, attribute):
        for l in self.links:
            if not getattr(l, attribute):
                return False
        return True
        
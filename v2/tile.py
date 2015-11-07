import libtcodpy as libtcod

import tools

class Tile(object):
    def __init__(self, x, y, char, color, con, game):
        self.x, self.y = x, y
        self.char = char
        self.current_char = char
        self.color = color
        self.current_color = color
        self.con = con
        self.game = game
        self.next = None
        self.prev = None
        
        self.visible = True

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        
    def get_location(self):
        return self.x, self.y

    def place(self, x, y):
        self.move(-self.x + x, -self.y + y)

    def revert_color(self):
        self.current_color = self.color

    def toggle_visible(self):
        if self.visible:
            self.visible = False
        else:
            self.visible = True
        return self.visible
        
    def get_visible(self):
        lights = self.game.the_map.light_sources
        seen = libtcod.map_is_in_fov(self.game.the_map.libtcod_map, self.x, self.y)
        lit = False
        for l in lights:
            if tools.get_distance(l.get_location(), self.get_location()) < l.radius:
                lit = True
        return seen or lit and self.visible
      
    def draw(self):
        if self.get_visible():
            self._draw()
        else:
            self.clear()
    
    
    def _draw(self):
        self.current_char = self.char
        self.current_color = self.color
        libtcod.console_set_default_foreground(self.con, self.current_color)
        libtcod.console_put_char(self.con, self.x, self.y, 
                                        self.current_char, libtcod.BKGND_NONE)

    def clear(self):
        libtcod.console_put_char(self.con, self.x, self.y, 
                                       ' ', libtcod.BKGND_NONE)

    def update(self):
        pass


class EnvironmentTile(Tile):
    def __init__(self, blocked, *args):
        super(EnvironmentTile, self).__init__(*args)
        self.blocked = blocked
        if self.blocked:
            self.color = libtcod.white
            self.revert_color()
            self.char = '#'
            
class Unit(Tile):   # has collision
    def move(self, dx, dy):
        newX = self.x + dx
        newY = self.y + dy
        if not self.game.the_map.run_collision(newX, newY):
            self.x += dx
            self.y += dy
            return True
        return False
        
class Word(Tile):
    def __init__(self, word, *args):
        super(Word, self).__init__(*args)
        self.word = word
        
    def draw(self):
        for i, letter in enumerate(self.word):
            x, y = self.x + i, self.y
            if libtcod.map_is_in_fov(self.game.the_map.libtcod_map, x, y):
                libtcod.console_set_default_foreground(self.con, self.current_color)
                libtcod.console_put_char(self.con, x, y, 
                                                letter, libtcod.BKGND_NONE)

        
class SpeakingObject(Unit):

    line_index_by_num_words = {1:(1,), 2:(1, 0), 3:(1, 0, -1), 4:(1, 0, 0, -1),
                               5:(1, 1, 0, 0, -1), 6:(1, 1, 0, 0, -1, -1),
                               7:(1, 1, 0, 0, 0, -1, -1)}

    def __init__(self, script, *args):
        super(SpeakingObject, self).__init__(*args)
        self.script = script
        self.words = []
        self.line = ""
        self.say_line()
        
    def say_line(self):
        if self.script:
            self.line = self.script.pop(0)
            self.words = []
            individual_words = self.line.split()
            num_words = len(individual_words)
            y_distribution = self.line_index_by_num_words[num_words]
            words_by_xy = {}
            for i, w in enumerate(individual_words):
                try:
                    rank = words_by_xy[y_distribution[i]]
                    if rank:
                        rank.append(w)
                except KeyError:
                    words_by_xy[y_distribution[i]] = [w]
            for rank, word_list in words_by_xy.iteritems():
                if rank != 0:
                    line_length = len(''.join(word_list)) + len(word_list) - 1
                    for i, word in enumerate(word_list):
                        x = self.x-line_length/2 + len(''.join(word_list[:i])) + i
                        y = self.y - rank
                        self.words.append(
                            Word(word, x, y, ' ', libtcod.grey, self.con, self.game)
                                          )
                else:
                    for i, word in enumerate(word_list):
                        halfway = len(word_list)/2
                        if i < halfway:
                            x = self.x - len(''.join(word_list[:halfway])) - i
                            y = self.y
                            self.words.append(
                                Word(word, x, y, ' ', libtcod.grey, self.con, self.game)
                                              )
                        else:
                            x = self.x + 1 + len(''.join(word_list[halfway:i])) + i
                            y = self.y
                            self.words.append(
                                Word(word, x, y, ' ', libtcod.grey, self.con, self.game)
                                              )
                    
    def draw(self):
        super(SpeakingObject, self).draw()
        for w in self.words:
            w.draw()

class Statue(SpeakingObject):
    def __init__(self, *args, **kwargs):
        super(Statue, self).__init__(*args, **kwargs)
        self.char = libtcod.CHAR_DVLINE
        self.blocked = True
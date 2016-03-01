import libtcodpy as libtcod


class Tile(object):

    name = ""
    phrase = None

    def __init__(self, x, y, char, color, con, game, phrase=None):
        self.x, self.y = x, y
        self.char = char
        self.phrase = phrase
        self.current_char = char
        self.color = color
        self.current_color = color
        self.color_queue = []
        self.char_queue = []
        self.con = con
        self.game = game
        self.next = None
        self.prev = None
        self.effects_mode = "discard"
        
        self.children = []
        self.effects = []
        
        self.visible = False
        self.transparent = True
        
        self.update_queue = []
        self.next_char = None
        self.next_color = None

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
        
    def is_visible(self):
        return self.visible

    def draw(self):
        if self.is_visible():
            self._draw()
            for c in self.children:
                c.draw()
#        else:
#            self.clear()

    def _draw(self):
        if self.next_char:
            char = self.next_char
        else:
            char = self.current_char
        if self.next_color:
            color = self.next_color
        else:
            color = self.current_color

        # awkward that there are two effects systems here, but maybe the 
        # checks are low cost enough that I don't have to worry about it?

        if self.phrase:
            for i, char in enumerate(self.phrase):
                x, y = self.game.camera.to_camera_coordinates(self.x + i, self.y)
#                if not self.game.the_map.run_collision(x, y):
                libtcod.console_set_default_foreground(self.con, color)
                libtcod.console_put_char(self.con, x, y, 
                                                char, libtcod.BKGND_NONE)
        else:
            x, y = self.game.camera.to_camera_coordinates(*self.get_location())
            
            libtcod.console_set_default_foreground(self.con, color)
            libtcod.console_put_char(self.con, x, y, 
                                            char, libtcod.BKGND_NONE)

    def clear(self):
        for c in self.children:
            c.clear()
        if self.phrase:
            for i, char in enumerate(self.phrase):
                x, y = self.game.camera.to_camera_coordinates(self.x + i, self.y)
                libtcod.console_put_char(self.con, x, y, 
                                                ' ', libtcod.BKGND_NONE)
        else:
            x, y = self.game.camera.to_camera_coordinates(*self.get_location())
            libtcod.console_put_char(self.con, x, y, 
                                            ' ', libtcod.BKGND_NONE)

    def update(self):
        # ACTIONS
        to_remove = []
        if self.update_queue:
            for i, action in enumerate(self.update_queue):
                if action[0] == 0:
                    action[1](*action[2])
                    to_remove.append(action)
                else:
                    self.update_queue[i] = (action[0] - 1, action[1], action[2])
            for completed_action in to_remove:
                self.update_queue.remove(completed_action)

        # DRAWING EFFECTS
        if self.effects and not self.game.the_map.run_collision(*self.get_location()):
            self.next_color, self.next_char = self.effects[-1].get_char(*self.get_location())
        else:
            self.next_color, self.next_char = None, None

        if self.color_queue:
            self.next_color = self.color_queue.pop(0)
            if self.effects_mode == "hold":
                self.color_queue.append(self.next_color)

        if self.char_queue:
            self.next_char = self.char_queue.pop(0)
            if self.effects_mode == "hold":
                self.char_queue.append(self.next_char)
                
        #
        
        self.visible = libtcod.map_is_in_fov(self.game.the_map.libtcod_map, self.x, self.y)

    def add_child(self, child, offset=None):
        self.children.append(child)
        if not offset:
            oX, oY = self.offsets[self.next_offset]
            self.next_offset = (self.next_offset + 1 if self.next_offset < len(self.offsets) - 1 else 0)
        else:
            oX, oY = offset
        child.offsetX = oX
        child.offsetY = oY
    
    def remove_child(self, child):
        self.children.remove(child)
        
    def delete(self):
        self.game.the_map.remove(self)
        del self


class EnvironmentTile(Tile):
    def __init__(self, blocked, *args):
        super(EnvironmentTile, self).__init__(*args)
        self.blocked = blocked
        if self.blocked:
            self.char = '#'
            self.transparent = False


class BottomlessPit(EnvironmentTile):
    def __init__(self, *args):
        super(BottomlessPit, self).__init__(*args)
        self.transparent = True
        self.char = ' '
    
            
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
        
    def _draw(self):
        for i, letter in enumerate(self.word):
            x, y = self.game.camera.to_camera_coordinates(self.x + i, self.y)
            libtcod.console_set_default_foreground(self.con, self.current_color)
            libtcod.console_put_char(self.con, x, y, 
                                            letter, libtcod.BKGND_NONE)
                                                
    def clear(self):
        for i, letter in enumerate(self.word):
            x, y = self.game.camera.to_camera_coordinates(self.x + i, self.y)
            libtcod.console_put_char(self.con, x, y, 
                                            ' ', libtcod.BKGND_NONE)
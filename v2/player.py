import libtcodpy as libtcod

from tile import Unit
from directive import Directive, PlayerArrow

class Player(Unit):

    arrow_keys = [libtcod.KEY_UP, libtcod.KEY_DOWN,
                  libtcod.KEY_RIGHT, libtcod.KEY_LEFT]

    def __init__(self, *args):
        super(Player, self).__init__(*args)

        self.children = []
        self.directives = []
        self.current_directive = None
        self.offsets = [(-2, -2), (-2, 2), (2, 3), (2, -3), (-2, -2), (-2, 2), (2, 3), (2, -3)]
        self.next_offset = 0

        self.arrows = {libtcod.CHAR_ARROW_N:None, libtcod.CHAR_ARROW_S:None, 
                       libtcod.CHAR_ARROW_E:None, libtcod.CHAR_ARROW_W:None}
        self.set_arrows()
        
    def set_arrows(self):
        NSEW = {(0, 1): libtcod.CHAR_ARROW_N, 
                (0, -1): libtcod.CHAR_ARROW_S, 
                (1, 0): libtcod.CHAR_ARROW_E, 
                (-1, 0): libtcod.CHAR_ARROW_W} 
        for offset, char in NSEW.iteritems():
            newD = PlayerArrow(self, self.game, text=char)
            self.add_directive(newD, offset=offset)
            self.add_arrow(newD)
        
    def add_arrow(self, arrow):
        self.arrows[arrow.phrase] = arrow

    def move(self, dx, dy):
        if super(Player, self).move(dx, dy):
            for t in self.game.the_map.get_NSEW(self.x - dx, self.y - dy):
                t.current_color = t.color
            for t in self.game.the_map.get_NSEW(self.x, self.y):
                if not t.blocked:
                    t.current_color = t.current_color + libtcod.dark_grey

    def handle_keys(self):
        for a in self.arrows.values():
            if a:
                a.pressed = False
        dx, dy = 0, 0
        key = libtcod.console_check_for_keypress()  #real-time
        if key.vk == libtcod.KEY_CHAR or key.vk in self.arrow_keys:
            self.handle_letter(key)
     
        if key.vk == libtcod.KEY_ENTER and key.lalt:
            #Alt+Enter: toggle fullscreen
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
        elif key.vk == libtcod.KEY_ESCAPE:
            return True  #exit game
     
        if libtcod.console_is_key_pressed(libtcod.KEY_UP):
            dx, dy = (0, -1)
            self.arrows[libtcod.CHAR_ARROW_N].pressed = True
        elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
            dx, dy = (0, 1)
            self.arrows[libtcod.CHAR_ARROW_S].pressed = True
        elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
            dx, dy = (-1, 0)
            self.arrows[libtcod.CHAR_ARROW_W].pressed = True
        elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
            dx, dy = (1, 0)
            self.arrows[libtcod.CHAR_ARROW_E].pressed = True
        if dx or dy:
            self.move(dx, dy)
            
    def add_child(self, child):
        self.children.append(child)
        
    def remove_child(self, child):
        self.children.remove(child)

    def add_directive(self, directive, offset=None):
        self.add_child(directive)
        self.directives.append(directive)
        if not offset:
            oX, oY = self.offsets[self.next_offset]
            self.next_offset = (self.next_offset + 1 if self.next_offset < len(self.offsets) else 0)
        else:
            oX, oY = offset
        directive.offsetX = oX
        directive.offsetY = oY

    def remove_directive(self, directive):
        self.remove_child(directive)
        self.directives.remove(directive)
        self.current_directive = None

    def handle_letter(self, key):
        letter = (chr(key.c) if key.c else key.vk)
        if self.current_directive:
            if self.current_directive.tick_phrase(letter):
                pass
            else:
                self.current_directive.reset()
                self.current_directive = None
        else:
            for d in self.directives:
                if d.tick_phrase(letter):
                    self.current_directive = d
                

    def draw(self):
        super(Player, self).draw()
        for d in self.directives:
            d.draw()

    def clear(self):
        super(Player, self).clear()
        for d in self.directives:
            d.clear()
        
    def update(self):
        for d in self.directives:
            d.update()

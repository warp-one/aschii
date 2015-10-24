import libtcodpy as libtcod

class Tile(object):
    def __init__(self, x, y, char, color, con, game):
        self.x, self.y = x, y
        self.char = char
        self.color = color
        self.current_color = color
        self.con = con
        self.game = game
        self.next = None
        self.prev = None

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def place(self, x, y):
        self.move(-self.x + x, -self.y + y)

    def revert_color(self):
        self.current_color = self.color

    def draw(self):
        libtcod.console_set_default_foreground(self.con, self.current_color)
        libtcod.console_put_char(self.con, self.x, self.y, 
                                        self.char, libtcod.BKGND_NONE)

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

class Statue(Unit):
    def __init__(self, *args):
        super(Statue, self).__init__(*args)
        self.char = libtcod.CHAR_DVLINE
        self.blocked = True
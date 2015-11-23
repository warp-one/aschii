import libtcodpy as libtcod

from basic_level import Level
from directive import *
from items import *

statue_script = [("dreamt alive", 'He dreamt that it was alive, tremulous'),
                 ("was bastard", 'it was not the atrocious bastard'),
                 ("tiger colt", 'of a tiger and a colt, but'),
                 ("both these", 'at the same time both of these'),
                 ("fiery also", 'fiery creatures, and also'),
                 ("bull rose", 'a bull, a rose, and a storm')]


class LevelZero(Level):

    start_location = 15, 15

    def __init__(self, *args):
        super(LevelZero, self).__init__(*args)
        self.player.add_power(Power(self.player, self, static=True, offset=(0, 30+len(self.player.children))))
        self.player.add_power(Sprint(self.player, self, text="sprint", static=True, offset=(0, 30+len(self.player.children))))
        self.player.add_observer(self.the_map)
        self.player.place(*self.start_location)
        
        self.statues = []
        for _ in range(1):
            s = Statue(statue_script, 10 + _*3, 10 + _, 'S', libtcod.green, self.foreground, self)
            self.statues.append(s)
            self.the_map.add(s.x, s.y, s)
#            self.player.add_child(Next(s, self, text="bow", static=True, offset = (2, 2)))
            self.player.add_child(Waypoint(s, self, text="approach", static=True, offset=(-1,-1)))
        self.flashlight = Flashlight(False, 20, 20, 'I', libtcod.yellow, self.foreground, self)
        x, y = self.flashlight.get_location()
        self.the_map.add(x, y, self.flashlight)
        self.player.add_child(ItemGrab(self.flashlight, self, text="pick up", offset = (-2, 2)))
        s = self.the_map.schimb()

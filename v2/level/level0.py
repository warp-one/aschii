from random import randint

import libtcodpy as libtcod

from basic_level import Level
from directive import *
from items import *
from maps import Med10x10_1 as m1, Boulders

statue_script = {"start":("town city", 'I will go to town or city'),
                     "town":("walk statue", 'and walk past the statue of the men'),
                         "walk":("", 'briskly, with my collar up.'),
                         "statue":("", ', the accursed Men of Grava'),
                     "city":("out, down", 'In or out, up or down'),
                         "out,":("", 'with my flashlight to light the way'),
                         "down":("caves", 'into one of the caves'),
                            "caves":("caves", 'yes, deep into the caves')}
                            
statue_script1 = {"start":("frozen, time", 'Everything is frozen, as if in time'),
                      "frozen,":("changed,", 'It can be changed, but only a little'),
                        "changed,":("suppose moments", "I suppose it is actually many moments"),
                          "suppose":("", "Catch the ones you can and leave the rest."),
                          "moments":("", "If you find one you like, you can leave it that way."),
                      "time":("specific right", "It's a specific moment. But is it the right moment?"),
                        "right":("know changing", "You'll know when it is. Until then, keep changing things."),
                          "know":("you leave", "It's up to you when to leave the caves."),
                            "you":("anyone will", "I don't know if anyone else will come down here."),
                              "anyone":("time", "Not for a long time, at least."),
                              "will":("", "Not for 10,000 years."),
                            "leave":("ever", "You don't really have to go ever"),
                              "ever":("time", "You can just stay here for a time"),
                          "changing":("things change", "If it weren't for you, some things would never change"),
                            "things":("time", "They would be the same for all time"),
                            "change":("", "They wouldn't ever be interfered with."),
                        "specific":("like now", "What is it like right now?"),
                          "like":("time", "It's fairly damp. And jacket weather. The time"),
                          "now":("", "It's very today, today.")}
                          


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
            s = Statue(statue_script1, 10 + _*3, 10 + _, 'S', libtcod.green, self.foreground, self)
            s.loop = True
            self.statues.append(s)
            self.the_map.add(s.x, s.y, s)
#            self.player.add_child(Next(s, self, text="bow", static=True, offset = (2, 2)))
            self.player.add_child(Waypoint(s, self, text="approach", 
                                            static=True, offset=(-1,-1)))

            t = LinkedStatue({}, 10, 20, 'S', libtcod.brass, self.foreground, self)
            self.the_map.add(t.x, t.y, t)
            self.player.add_child(Bow(t, self, text="bow", static=True, offset=(-1,-1)))

            u = LinkedStatue({}, 13, 20, 'S', libtcod.brass, self.foreground, self)
            self.the_map.add(u.x, u.y, u)
            self.player.add_child(Bow(u, self, text="bow", static=True, offset=(-1,-1)))
            u.add_link(t)
            t.add_link(u)
            
            v = LinkedStatue({}, 10, 25, 'T', libtcod.brass, self.foreground, self)
            self.the_map.add(v.x, v.y, v)
            v_ = WordMatch(["away", "find", "angle", "stalagmite"], 
                                    v, self, static=True, offset=(-1,-1))
            self.player.add_child(v_)

            w = LinkedStatue({}, 15, 25, 'T', libtcod.brass, self.foreground, self)
            self.the_map.add(w.x, w.y, w)
            w_ = WordMatch(["go", "mushroom", "set", "frighten"], 
                                    w, self, static=True, offset=(-1,-1))
            self.player.add_child(w_)
            w.add_link(v)
            v.add_link(w)
            

        self.flashlight = Flashlight(False, 20, 20, 'I', libtcod.yellow, self.foreground, self)
        x, y = self.flashlight.get_location()
        self.the_map.add(x, y, self.flashlight)
        
        self.gam = Gammon(False, 22, 20, 'd', libtcod.pink, self.foreground, self)
        x, y = self.gam.get_location()
        self.the_map.add(x, y, self.gam)

        
        self.player.add_child(ItemGrab(self.flashlight, self, text="pick up", offset = (-2, 2)))
        self.player.add_child(ItemGrab(self.gam, self, text="pick up", offset = (-2, 2)))
        s = self.the_map.schimb()
        self.the_map.load_doodad(25, 25, m1)
        for b in Boulders:
            x, y = randint(0, 100), randint(0, 80)
            self.the_map.load_doodad(x, y, b)

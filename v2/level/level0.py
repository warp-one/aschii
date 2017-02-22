from basic_level import Level
from directive import *
from items import *
from maps import drawings
from directive.faders import DirectiveLineFade

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
                          
statue_script2 = {"start":("", 'I would rather be...')}

            
                          
reveal_script0 = {"start":("bug", 'bug'),
                      "bug":("", 'noo noooo no')}
                      
reveal_script1 = {"start":("GOBLINS", 'CAVE OF THE GOBLINS ---->'),
                    "GOBLINS":("",'grrr'),
                    "newchoices":(" CAVE"),
                    "CAVE":("dark", 'Pretty dark in here, isn\'t it?'),
                    "dark":("", 'Almost too dark to see.')}
                    
gates_data = [((70, 16), "I"),
              ((71, 16), "swear"),
              ((79, 28), "I"),
              ((74, 44), "didn't"),
              ((70, 41), "do"),
              ((72, 37), "it"),
              ((79, 31), "please")]
                          
                          
class FieldOfRealPeople(object):

    '''A little field of 3-character upright "people" with a title card. "THE
    FIELD OF REAL PEOPLE". All of them have the same looping voice lines, which
    the persistent find lead to an end path: join the field in the available
    place.'''

    def __init__(self):
        pass


class LevelZero(Level):

    start_location = 8, 5

    def __init__(self, *args):
        super(LevelZero, self).__init__(*args)
        self.player.add_power(Power(self.player, self, static=True, offset=(0, 30+len(self.player.children))))
        self.player.add_power(Sprint(self.player, self, text="sprint", static=True, offset=(0, 30+len(self.player.children))))
        self.player.add_observer(self.the_map)
        self.player.place(*self.start_location)
        
        self.statues = []
        for _ in range(1):
            s = Statue(statue_script2, 19, 27 + _, ' ', libtcod.green, self.foreground, self)
            s.loop = False
            self.statues.append(s)
            self.the_map.add(s.x, s.y, s)
            
            s = MovingStatue(0, 50, reveal_script0, 56, 49 + _, 'R', libtcod.grey, self.foreground, self)
            s.loop = False
            self.statues.append(s)
            self.the_map.add(s.x, s.y, s)
#            self.player.add_child(Next(s, self, text="bow", static=True, offset = (2, 2)))
#            self.player.add_child(Waypoint(s, self, text="approach", 
#                                            static=True, offset=(-1,-1)))
                                            
            t = LinkedStatue({}, 15, 31, ' ', libtcod.brass, self.foreground, self)
            self.the_map.add(t.x, t.y, t)
            self.player.add_child(Bow(t, self, text="brighter", static=True, offset=(-1,-1)))

            u = LinkedStatue({}, 24, 32, ' ', libtcod.brass, self.foreground, self)
            self.the_map.add(u.x, u.y, u)
            self.player.add_child(Bow(u, self, text="fleeter", static=True, offset=(-1,-1), new_fader=DirectiveLineFade))
            u.add_link(t)
            t.add_link(u)
            
            schimber = Lightener(self.player, self, text="light", sentence="Find the light", static=True, offset=(0, 0))
            schimber.visible = False
            self.player.add_child(schimber)
            self.the_map.schimber = schimber
            
            for info in gates_data:
                # something different should happen based on which order you complete them
                # "please I didn't do it"
                # "please do it"
                # "it didn't"
                g = LStatue({}, info[0][0], info[0][1], 'X', libtcod.yellow, self.foreground, self)
                self.statues.append(g)
                self.the_map.add(g.x, g.y, g)
                self.player.add_child(Ban(g, self, text=info[1], static=True, offset=(-2, 2)))
                
            s = ResetStatue(2, 30, reveal_script1, 8, 1, ' ', libtcod.light_red, self.foreground, self)
            s.loop = False
            self.statues.append(s)
            self.the_map.add(s.x, s.y, s)
#            self.player.add_child(Next(s, self, text="bow", static=True, offset = (2, 2)))
            #self.player.add_child(Waypoint(s, self, text="approach", 
#                                            static=True, offset=(-1,-1)))
                                            
            rp = RealPerson(None, 11, 40, ' ', libtcod.light_blue, self.foreground, self)
            rp.loop = True
            self.statues.append(rp)
            self.the_map.add(rp.x, rp.y, rp)
            
            v = LinkedStatue({}, 56, 40, 'L', libtcod.brass, self.foreground, self)
            self.the_map.add(v.x, v.y, v)
            v_ = WordMatch(["holy", "look", "angle", "stalagmite"], 
                                    v, self, static=True, offset=(-1,-1))
            self.player.add_child(v_)

            w = LinkedStatue({}, 67, 40, 'T', libtcod.brass, self.foreground, self)
            self.the_map.add(w.x, w.y, w)
            w_ = WordMatch(["bite", "tap", "set", "frighten"], 
                                    w, self, static=True, offset=(-1,-1))
            self.player.add_child(w_)
            w.add_link(v)
            v.add_link(w)

        self.figurine = Idol(False, 28, 28, 'i', libtcod.white, self.foreground, self)
        x, y = self.figurine.location
        self.the_map.add(x, y, self.figurine)
        
        self.lamp = Lamp(False, 24, 24, 'T', libtcod.yellow, self.foreground, self)
        x, y = self.lamp.location
        self.the_map.add(x, y, self.lamp)
        
        self.lute = Lute(False, 22, 20, 'Q', libtcod.light_sepia, self.foreground, self)
        x, y = self.lute.location
        self.the_map.add(x, y, self.lute)

        self.player.add_child(ItemGrab(self.figurine, self, text="pick up", offset = (-2, 2)))
        self.player.add_child(ItemGrab(self.lute, self, text="pick up", offset = (-2, 2)))
        self.player.add_child(ItemGrab(self.lamp, self, text="pick up", offset = (-2, 2)))

        a = self.special_effects.append(drawings.tv)
        drawings.tv.begin(self.the_map)

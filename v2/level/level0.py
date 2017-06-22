from basic_level import Level
from directive import *
from items import *
from maps import drawings
from directive.faders import DirectiveLineFade


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

    start_location = 18, 14
    
    lightener_nodes = [(x, randint(10, 20)) for x in range(25, 55, 8)]

    def __init__(self, *args):
        super(LevelZero, self).__init__(*args)
#        self.player.add_power(Power(self.player, self, static=True, offset=(0, 30+len(self.player.children))))
#        self.player.add_power(Sprint(self.player, self, text="sprint", static=True, offset=(0, 30+len(self.player.children))))
        
#        self.narrative = narrative.RunningNarrative()
        self.statues = []
        #s = Statue(statue_script2, 19, 27 + _, ' ', libtcod.green, self.foreground, self)
        #s.loop = False
        #self.statues.append(s)
        #self.the_map.add(s.x, s.y, s)
        
#            s = MovingStatue(0, 50, reveal_script0, 56, 49 + _, 'R', libtcod.grey, self.foreground, self)
#            s.loop = False
#            self.statues.append(s)
#            self.the_map.add(s.x, s.y, s)
#            self.player.add_child(Next(s, self, text="bow", static=True, offset = (2, 2)))
#            self.player.add_child(Waypoint(s, self, text="approach", 
#                                            static=True, offset=(-1,-1)))
                                            
#            t = LinkedStatue({}, 15, 31, ' ', libtcod.brass, self.foreground, self)
#            self.the_map.add(t.x, t.y, t)
#            self.player.add_child(Bow(t, self, text="brighter", static=True, offset=(-1,-1)))

#            u = LinkedStatue({}, 24, 32, ' ', libtcod.brass, self.foreground, self)
#            self.the_map.add(u.x, u.y, u)
#            self.player.add_child(Bow(u, self, text="fleeter", static=True, offset=(-1,-1), new_fader=DirectiveLineFade))
#            u.add_link(t)
#            t.add_link(u)
            
        schimber = Lightener(lightener_script_0, self.player, self,
                             nodes = [(x, x) for x in range(10, 60, 10)])
        schimber.visible = False
        schimber.nodes = self.lightener_nodes
        self.player.add_child(schimber)
        self.the_map.schimbers.append(schimber)
        self.the_map.scribe.add_directive(schimber)
        
        schimber1 = Schimber(schimber_script_0, self.player, self,
                             nodes = [(x, x) for x in range(10, 110, 30)])
        schimber1.visible = False
        self.player.add_child(schimber1)
        self.the_map.schimbers.append(schimber1)
        self.the_map.scribe.add_directive(schimber1)
        
        schimber2 = Storyteller(story_script_0, self.player, self, 
                                nodes = [(x/2, x) for x in range(10, 110, 20)])
        schimber2.visible = False
        self.player.add_child(schimber2)
        self.the_map.schimbers.append(schimber2)
        self.the_map.scribe.add_directive(schimber2)
        
        bridge = BridgeBuilder(20, 20, "!", libtcod.dark_green, 
                               self.foreground, self)
        bridge_toggle = Directive(bridge, self, 
                                  text="crank", 
                                  sentence="turn the crank",
                                  offset=(-4, 4), 
                                  on_completion_callable=bridge.do,
                                  color_scheme=ColorScheme(basic_green))
        bridge_talker = RotatingDirective(bridge_script_0, bridge, self, 
                                  offset=(1, 1), 
                                  text_layout=RollingLayout(3, 0, 3, 0, 1), 
                                  on_completion_callable=None)
        self.the_map.add(bridge.x, bridge.y, bridge)
        self.player.add_child(bridge_toggle)
        self.player.add_child(bridge_talker)
        
        plinth = EnvironmentTile(True, 81, 75, "m", libtcod.white, self.foreground, self)
        self.the_map.add(plinth.x, plinth.y, plinth)
        broken_pot = TestingDirective(plinth, self,
                                      text="pottery",
                                      sentence="several pieces of luminescent white pottery lie on the ground",
                                      offset=(-5, 2),
                                      on_completion_callable=None,
                                      color_scheme=SparklyKeyword(basic_grey))
        pot_layout = GatherLayout(broken_pot, 0, 15, 5, 0, 1)
        broken_pot.text_layout = pot_layout
        self.player.add_child(broken_pot)
        
        sign = Television(40, 17, ">", libtcod.dark_blue, 
                          self.foreground, self)
        sign_border = RotatingDirective(sign_script_0, sign, self, 
                                  text="?",
                                  static=False, 
                                  offset=(-1, -1), 
                                  text_layout=RectangleLayout(5, 14, 8, 0, 1), 
                                  on_completion_callable=sign.next_channel, 
                                  range=3)
        self.the_map.add(sign.x, sign.y, sign)
        self.player.add_child(sign_border)
        
        tree = BranchingStory({"dance":"draft", "draft":"munches", "munches":None},
                                  50, 50, 'F', libtcod.red, self.foreground, self)
        self.the_map.add(tree.x, tree.y, tree)
        tree0 = RotatingDirective(tree_script_0, tree, self, 
                                  text="?",
                                  static=False, 
                                  offset=(-1, -1), 
                                  text_layout=ScatterLayout([(-5, -5), (-3, -4), (0, -3), (-4, -2), (-1, -1), (2, 1), (-3, 2)]), 
                                  on_completion_callable=tree.next_branch)
        
        tree1 = Directive(tree, self, 
                                  text=tree_script_1[0],
                                  sentence=tree_script_1[1],
                                  static=False, 
                                  offset=(3, 1), 
#                                  text_layout=RectangleLayout(5, 14, 8, 0, 1), 
                                  on_completion_callable=tree.next_branch)
                                  
        tree2 = Directive(tree, self, 
                                  text=tree_script_2[0],
                                  sentence=tree_script_2[1],
                                  static=False, 
                                  offset=(-3, 3), 
#                                  text_layout=RectangleLayout(5, 14, 8, 0, 1), 
                                  on_completion_callable=tree.next_branch)
        tree_branches = [tree0, tree1, tree2]
        tree0.persistent = False
        for t in tree_branches:
            tree.grow_branch(t.phrase, t)
            self.player.add_child(t)
            
        tourist = RealPerson(66, 42, ' ', libtcod.blue, self.foreground, self)
        self.the_map.add(tourist.x, tourist.y, tourist)
                                  
 #       news = Directive(bridge, self, 
 #                        text=news_script_0[0][0], 
 #                        sentence=news_script_0[0][1],
 #                        static = False, 
 #                        offset = (4, -2), 
 #                        width = 12)
 #       self.player.add_child(news)
#            for info in gates_data:
                # something different should happen based on which order you complete them
                # "please I didn't do it"
                # "please do it"
                # "it didn't"
#                g = Statue({}, info[0][0], info[0][1], 'X', libtcod.yellow, self.foreground, self)
#                self.statues.append(g)
#                self.the_map.add(g.x, g.y, g)
#                self.player.add_child(Ban(g, self, text=info[1], static=True, offset=(-2, 2)))
                
#            s = ResetStatue(2, 30, reveal_script1, 8, 1, ' ', libtcod.light_red, self.foreground, self)
#            s.loop = False
#            self.statues.append(s)
#            self.the_map.add(s.x, s.y, s)
#            self.player.add_child(Next(s, self, text="bow", static=True, offset = (2, 2)))
            #self.player.add_child(Waypoint(s, self, text="approach", 
#                                            static=True, offset=(-1,-1)))
                                            
#            rp = RealPerson(None, 11, 40, ' ', libtcod.light_blue, self.foreground, self)
#            rp.loop = True
#            self.statues.append(rp)
#            self.the_map.add(rp.x, rp.y, rp)
            
#            v = LinkedStatue({}, 56, 40, 'L', libtcod.brass, self.foreground, self)
#            self.the_map.add(v.x, v.y, v)
#            v_ = WordMatch(["holy", "look", "angle", "stalagmite"], 
#                                    v, self, static=True, offset=(-1,-1))
#            self.player.add_child(v_)

#            w = LinkedStatue({}, 67, 40, 'T', libtcod.brass, self.foreground, self)
#            self.the_map.add(w.x, w.y, w)
#            w_ = WordMatch(["bite", "tap", "set", "frighten"], 
#                                    w, self, static=True, offset=(-1,-1))
#            self.player.add_child(w_)
#            w.add_link(v)
#            v.add_link(w)

#        self.figurine = Idol(False, 28, 28, 'i', libtcod.white, self.foreground, self)
#        x, y = self.figurine.location
#        self.the_map.add(x, y, self.figurine)
        
        self.lamp = Lamp(False, 24, 24, 'T', libtcod.yellow, self.foreground, self)
        x, y = self.lamp.location
        self.the_map.add(x, y, self.lamp)
        
#        self.lute = Lute(False, 22, 20, 'Q', libtcod.light_sepia, self.foreground, self)
#        x, y = self.lute.location
#        self.the_map.add(x, y, self.lute)

#        self.player.add_child(ItemGrab(self.figurine, self, text="pick up", offset = (-2, 2)))
#        self.player.add_child(ItemGrab(self.lute, self, text="pick up", offset = (-2, 2)))
        self.player.add_child(ItemGrab(self.lamp, self, text="pick up", offset = (-2, 2)))

    def load_object(self, thing):
        self.the_map.add(thing.x, thing.y, thing)
        self.narrative.add(thing)
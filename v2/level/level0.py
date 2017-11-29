from basic_level import Level
from directive import *
from items import *


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

    start_location = 136, 89
    
    lightener_nodes = [(x, randint(10, 20)) for x in range(25, 55, 8)]
    directive_stories = []
    
    def __init__(self, *args):
        super(LevelZero, self).__init__(*args)

        self.statues = []

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
        
        bridge = BridgeBuilder(136, 87, "C", libtcod.dark_green, 
                               self.foreground, self)
        describe(bridge, crank_about)
        btd = (RotatingDirective, (bridge_script_0, bridge, self),
                                  dict(offset=(-4, 4),
                                  text_layout=(RollingLayout, (3, 0, 3, 0, 1)),
                                  on_completion_callable=bridge.do))
        bridge_talker = btd[0](*btd[1], **btd[2])
        bridge_talker.max_rotations = 1
        self.load_object(bridge)
        self.player.add_child(bridge_talker)
        
        pot_story = DirectiveGrouper(self)
        self.directive_stories.append(pot_story)
        
        plinth = EnvironmentTile(True, 60, 90, "m", libtcod.white, self.foreground, self)
        describe(plinth, plinth_about)
        self.load_object(plinth)
        
        broken_pot_data = (TestingDirective, 
                            (plinth, self),
                            dict(text="pottery",
                                sentence="What's this? A big pile of pottery?",
                                offset = (0, 0),
                                on_completion_callable=None,
                                static = True, 
                                color_scheme=SparklyKeyword(basic_grey),
                                text_layout = (GatherLayout, ("self", 0, 15, 5, 0, 1))
                                )
                                )
        
        plinth2 = EnvironmentTile(True, 75, 90, "n", libtcod.white, self.foreground, self)
        describe(plinth2, plinth_about)
        self.load_object(plinth2)
        
        broken_pot2_data = (TestingDirective, 
                            (plinth2, self),
                            dict(text="Another",
                                sentence="Another one! And broken too!",
                                offset = (0, 0),
                                on_completion_callable=None,
                                static = True, 
                                color_scheme=SparklyKeyword(basic_grey),
                                text_layout = (GatherLayout, ("self", 0, 15, 5, 0, 1))
                                )
                                )
                                
        pot_story.add_directive(broken_pot_data, "start")
        pot_story.add_directive(broken_pot2_data, "pottery")
                                
        sign = Television(40, 17, ">", libtcod.dark_blue, 
                          self.foreground, self)
        sign_border = RotatingDirective(sign_script_0, sign, self, 
                                  text="?",
                                  static=False, 
                                  offset=(-1, -1), 
                                  text_layout=(RectangleLayout, (5, 14, 8, 0, 1)), 
                                  on_completion_callable=sign.next_channel, 
                                  range=3)
        self.the_map.add(sign.x, sign.y, sign)
        self.narrative.add_object(sign)
        self.player.add_child(sign_border)
        
        tree = BranchingStory({"dance":"draft", "draft":"munches", "munches":None},
                                  50, 50, 'F', libtcod.red, self.foreground, self)
        self.the_map.add(tree.x, tree.y, tree)
        self.narrative.add_object(tree)
        tree0 = RotatingDirective(tree_script_0, tree, self, 
                                  text="?",
                                  static=False, 
                                  offset=(-1, -1), 
                                  text_layout=(ScatterLayout, ([(-5, -5), (-3, -4), (0, -3), (-4, -2), (-1, -1), (2, 1), (-3, 2)],)), 
                                  on_completion_callable=tree.next_branch)
        
        tree1 = Directive(tree, self, 
                                  text=tree_script_1[0],
                                  sentence=tree_script_1[1],
                                  static=False, 
                                  offset=(3, 1), 
                                  on_completion_callable=tree.next_branch)
                                  
        tree2 = Directive(tree, self, 
                                  text=tree_script_2[0],
                                  sentence=tree_script_2[1],
                                  static=False, 
                                  offset=(-3, 3), 
                                  on_completion_callable=tree.next_branch)
        tree_branches = [tree0, tree1, tree2]
        tree0.persistent = False
        for t in tree_branches:
            tree.grow_branch(t.phrase, t)
            self.player.add_child(t)
            
        tourist = RealPerson(66, 42, ' ', libtcod.blue, self.foreground, self)
        self.load_object(tourist)
                                  
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
                

        self.figurine = Idol(False, 28, 28, 'i', libtcod.white, self.foreground, self)
        self.load_object(self.figurine)
        
        self.lamp = Lamp(False, 24, 24, 'T', libtcod.yellow, self.foreground, self)
        self.load_object(self.lamp)
        
        self.lute = Lute(False, 22, 20, 'Q', libtcod.light_sepia, self.foreground, self)
        self.load_object(self.lute)

        self.player.add_child(ItemGrab(self.figurine, self, text="pick up", offset = (-2, 2)))
        self.player.add_child(ItemGrab(self.lute, self, text="pick up", offset = (-2, 2)))
        self.player.add_child(ItemGrab(self.lamp, self, text="pick up", offset = (-2, 2)))

        for d in self.directive_stories:
            d.start()
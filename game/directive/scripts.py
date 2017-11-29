from collections import deque



def describe(unit, about_script): # all this is only used by the narrative hud
        unit.name = about_script[0][0]
        unit.sight = about_script[0][1]
        unit.abouts = about_script[1:]
        unit.current_about = unit.abouts[0]
            


## ROTATING SCRIPTS
#
#

default_script = deque([("left", "Let's go left."),
                    ("right", "No, I like right.")
                    ]
                   )

lightener_script_0 = deque([("light", "I quiver and hang in a loop of light."),
                    ("lantern", "Like a lantern down a dark lane."),
                    ("glow", "A mysterious glow against a stand of yew trees."),
                    ("candle", "To lXXXt a candle is to cast a shadow..."),
                    ("luminous", "You are not yourself luminous!")
                    ]
                   )

schimber_script_0 = deque([("ants", "This line is being eaten by ants."),
                    ("point", "Could you point your headlamp over there?"),
                    ("your", "Watch your foot!"),
                    ("way", "Is this the right way?"),
                    ("forward", "I think forward is the only possibility.")
                    ]
                   )

story_script_0 = deque([("moths", "Do you ever think about moths?"),
                    ("wings", "The quiet flap of their wings?"),
                    ("eyes",  "An enormous pair of dark eyes."),
                    ]
                   )

bridge_script_0 = deque([("crank", "crank?"),
                    ("uncrank", "uncrank."),
                    ]
                   )
                   
sign_script_0 = deque([(">", "WOW! WOW! WOW! WOW! WOW! WOW! > WOW! WOW!")
                    ]
                   )

news_script_0 = deque([("time", "For some time I have been disturbed by the sudden appearance of button mushrooms along the path to work")
                    ]
                   )
                   
tree_script_0 = deque([("hands", "A tree with leaves like ladies' hands"),
                       ("bands", "Two worms curled round are wedding bands"),
                       ("dance", "The wind will lead the wedding dance")
                    ]
                   )
                   
tree_script_1 = ("draft", "Where is that draft coming from?")

tree_script_2 = ("munches", "Something munches near the ground")

## BRANCHING SCRIPTS
#
#

statue_script_0 = {"start":("town city", 'I will go to town or city'),
                     "town":("walk statue", 'and walk past the statue of the men'),
                         "walk":("", 'briskly, with my collar up.'),
                         "statue":("", ', the accursed Men of Grava'),
                     "city":("out, down", 'In or out, up or down'),
                         "out,":("", 'with my flashlight to light the way'),
                         "down":("caves", 'into one of the caves'),
                            "caves":("caves", 'yes, deep into the caves')}
                            
statue_script_1 = {"start":("frozen, time", 'Everything is frozen, as if in time'),
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
                          
statue_script_2 = {"start":("", 'I would rather be...')}

reveal_script_0 = {"start":("bug", 'bug'),
                      "bug":("", 'noo noooo no')}
                      
reveal_script_1 = {"start":("GOBLINS", 'CAVE OF THE GOBLINS ---->'),
                    "GOBLINS":("",'grrr'),
                    "newchoices":(" CAVE"),
                    "CAVE":("dark", 'Pretty dark in here, isn\'t it?'),
                    "dark":("", 'Almost too dark to see.')}

                    
## OBJECT DESCRIPTIONS

plinth_about = [("plinth", "a plinth made of white stone"), "Around it are scattered some luminous pieces of pottery", "The reconstructed pot gleams like a silver tooth in the quiet cavern."]

crank_about = [("rusty", "An old, rusty crank."), ""]
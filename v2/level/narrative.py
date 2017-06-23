from collections import deque

import libtcodpy as libtcod

import settings, directive, tile

class RunningNarrative(tile.Tile):
    width = settings.SCREEN_WIDTH
    
    def __init__(self, *args, **kwargs):
        super(RunningNarrative, self).__init__(*args, **kwargs)
        self.descriptions = {}
        
    def draw(self): # descriptions are directives?
        pass  
        
    def is_visible(self):
        return True
        
    @property
    def location(self):
        return self.x, self.y
        
    def update(self):
        for d in self.descriptions.itervalues():
            d.visible = False
        active_descriptions = [self.descriptions[u] for u in self.descriptions if u.is_visible()]
        len_prev_sentences = 0
        for d in active_descriptions:
            d.visible = True
            d.offset = len_prev_sentences % self.width, len_prev_sentences/self.width
            len_prev_sentences += len(d.to_draw)
        
    def clear(self): #oof
        return
        for tx in range(self.width):
            for ty in range(5):
                libtcod.console_put_char(self.con, tx + self.x, ty + self.y, 
                                        ' ', libtcod.BKGND_NONE)

        
    def add_object(self, thing):
        try:
            thing_sentence = deque([(thing.name, thing.description)])
        except AttributeError:
            thing_sentence = deque([("object", "There's a mysterious object on the ground.")])

        name_color = thing.current_color
        colors = directive.make_color_scheme(keyword=name_color, letters=(name_color+libtcod.dark_grey))
        thing_narrative = directive.RotatingDirective( 
                                    thing_sentence,
                                    self,
                                    self.game,
                                    static=True,
                                    text_layout=directive.NarrativeLayout(),
                                    color_scheme=directive.ColorScheme(colors),
                                    on_completion_callable=self.elaborate)
        thing_narrative.range = 1000
        self.descriptions[thing] = thing_narrative
        self.game.player.add_child(thing_narrative)
                                    
    def remove_object(self, thing):
        del self.descriptions[thing]
        self.game.player.remove_child(thing_narrative)
                    
    def elaborate(self):
        pass
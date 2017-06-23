from collections import deque

import libtcodpy as libtcod

import settings, directive, tile

class RunningNarrative(tile.Tile):
    width = settings.SCREEN_WIDTH
    
    def __init__(self, *args, **kwargs):
        super(RunningNarrative, self).__init__(*args, **kwargs)
        self.descriptions = []
        self.current_elaboration = None
        self.current_thing = None
        
    def draw(self): # descriptions are directives?
        if self.current_elaboration:
            for i, l in enumerate(self.current_elaboration):
                libtcod.console_set_default_foreground(self.con, libtcod.white)
                libtcod.console_put_char(self.con, self.x + i, settings.SCREEN_HEIGHT - 3, 
                                                l, libtcod.BKGND_NONE)
                
    def is_visible(self):
        return True
        
    def update(self):
        active_descriptions = [u for u in self.descriptions if u.anchor.is_visible()]
        if self.current_thing not in active_descriptions:
            self.current_elaboration = None
        len_prev_sentences = 0
        for d in active_descriptions:
            d.offset = self.x + len_prev_sentences % self.width, self.y + len_prev_sentences/self.width
            len_prev_sentences += len(d.to_draw)
        
    def clear(self): #oof
        return
        for tx in range(self.width):
            for ty in range(5):
                libtcod.console_put_char(self.con, tx + self.x, ty + self.y, 
                                        ' ', libtcod.BKGND_NONE)

        
    def add_object(self, thing):
        try:
            thing_sentence = deque([(thing.name, thing.sight)])
        except AttributeError:
            thing_sentence = deque([("object", "There's a mysterious object on the ground.")])

        name_color = thing.current_color - libtcod.grey
        colors = directive.make_color_scheme(keyword=name_color, letters=(name_color+libtcod.dark_grey))
        thing_narrative = directive.NarrativeDirective( 
                                    thing_sentence,
                                    thing,
                                    self.game,
                                    static=True,
                                    offset=(self.x, self.y),
                                    text_layout=directive.NarrativeLayout(),
                                    color_scheme=directive.ColorScheme(colors),
                                    on_completion_callable=self.elaborate)
        thing_narrative.range = 1000
        self.descriptions.append(thing_narrative)
        self.game.player.add_child(thing_narrative)
                                    
    def remove_object(self, thing):
        self.descriptions.remove(thing)
        self.game.player.remove_child(thing)
                    
    def elaborate(self, description):
        self.current_thing = description
        self.current_elaboration = description.anchor.current_about
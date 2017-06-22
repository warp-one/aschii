from collections import deque

import settings, directive

class RunningNarrative(object):
    x = 0
    y = settings.SCREEN_HEIGHT - 5
    width = settings.SCREEN_WIDTH
    
    def __init__(self, level):
        self.level = level
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
            len_prev_sentences += len(l.to_draw)
        
    def clear(self):
        pass
        
    def add_object(self, thing):
        thing_narrative = directive.RotatingDirective( 
                                    deque([("thing", "It's a thing!")]),
                                    self,
                                    self.level,
                                    static=True,
                                    on_completion_callable=self.elaborate)
        self.descriptions[thing] = thing_narrative
        self.level.player.add_child(thing_narrative)
                                    
    def remove_object(self, thing):
        del self.descriptions[thing]
        self.level.player.remove_child(thing_narrative)
                    
    def elaborate(self):
        pass
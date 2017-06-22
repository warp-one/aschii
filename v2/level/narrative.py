import settings

class RunningNarrative(object):
    x = 0
    y = settings.SCREEN_HEIGHT - 5
    
    def __init__(self):
        self.describable_objects = []
        
    def draw(self): # descriptions are directives?
        descriptions = [o.description for o in self.describable_objects if o.is_visible()]
        text = " ".join(descriptions)
        for l in text:
            
        
    def update(self):
        pass
        
    def clear(self):
        pass
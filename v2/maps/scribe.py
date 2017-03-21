from random import shuffle

class TheScribe(object):
    def __init__(self):
        self.directive_id = 0
        self.directives = {}
        self.inactive_directives = {}
        
    def add_directive(self, directive):
        self.directive_id += 1
        directive.id = self.directive_id
        self.directives[directive.id] = directive
        
    def disable_directive(self, directive):
        try:
            self.inactive_directives[directive.id] = self.directives.pop(directive.id)
        except KeyError:
            print "Not an active directive!"
        
    def enable_directive(self, directive):
        try:
            self.directives[directive.id] = self.inactive_directives.pop(directive.id)
        except KeyError:
            print "Not an inactive directive!"
        
    def write_floor(self, tiles_to_write):
        num_tiles = len(tiles_to_write)
        num_directive_letters = 0
        
        mandatory_directives = []
        optional_directives = []
        current_directive = None
        end_of_current_sentence = 0
        
        letter = '?'
        
        for d in self.directives.itervalues():
            if d.mandatory and d.player_in_range():
                mandatory_directives.append(d)
            else:
                optional_directives.append(d)
        
        shuffle(mandatory_directives)
        optional_directives.sort(key=lambda x: x.priority)
        
        
        for i, t in enumerate(tiles_to_write):
            if not current_directive and mandatory_directives:
                current_directive = mandatory_directives.pop(0)
                end_of_current_sentence = i + len(current_directive.sentence)
                current_directive.visible = True
                current_directive.coords = []
            if current_directive and i >= end_of_current_sentence:
                current_directive = None
            if current_directive:
                current_directive.coords.append( ((t.x, t.y), t.current_color) )
            
            
            t.current_char = letter
from random import shuffle

import libtcodpy as libtcod

import markovgen as mg
import settings

class TheScribe(object):
    def __init__(self):
        self.directive_id = 0
        self.directives = {}
        self.inactive_directives = {}
        
        self.mutated_text = []

        
        with open('waves.txt', 'r') as f:
            self.waves = mg.Markov(f)
        with open('nightland.txt', 'r') as f:
            self.nightland = mg.Markov(f)
        with open('goblin.txt', 'r') as f:
            self.goblins = mg.Markov(f)
            
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
            
    def organize_directives_for_writing(self):
        mandatory_directives = []
        optional_directives = []
        
        for d in self.directives.itervalues():
            if d.mandatory and d.player_in_range():
                mandatory_directives.append(d)
                d.coords = []
            else:
                optional_directives.append(d)
                
        shuffle(mandatory_directives)
        optional_directives.sort(key=lambda x: x.priority)
        
        return mandatory_directives, optional_directives
        
    def write_floor(self, tiles_to_write):
        # this most likely continues to be the most time-intensive
        # part of the program, given that it is called every frame
        # of movement and you loop through the entire visible area
        # (again). something to think about.
        
        num_tiles = len(tiles_to_write)
        num_directive_letters = 0
        
        mandatory_directives, optional_directives = self.organize_directives_for_writing()
        current_directive = None
        end_of_current_sentence = 0
        len_directives_written = 0
        
        if len(self.mutated_text) < num_tiles:
            self.mutated_text = self.create_ocean_text(self.waves)
        
        for i, t in enumerate(tiles_to_write):
            current_place_in_text = i - len_directives_written
            current_letter = self.mutated_text[current_place_in_text]
            previous_letter = self.mutated_text[current_place_in_text - 1]
            previouser_letter = self.mutated_text[current_place_in_text - 2]
            if previous_letter == ' ' and previouser_letter == '.':
                end_of_sentence = True
            else:
                end_of_sentence = False
            if not current_directive and mandatory_directives and end_of_sentence:
                end_of_current_sentence = i + len(mandatory_directives[0].sentence)
                if end_of_current_sentence > num_tiles:
                    pass
                else:
                    current_directive = mandatory_directives.pop(0)
                    current_directive.draw_on_floor = True
                    current_directive.visible = True
                    len_directives_written += 1
            if current_directive and i >= end_of_current_sentence:
                current_directive = None
            if current_directive:
                current_directive.coords.append( ((t.x, t.y), t.current_color) )
                len_directives_written += 1
            t.current_char = current_letter
            
        if mandatory_directives: # i.e., if /still/ mandatory_directives
            for i, md in enumerate(mandatory_directives):
                md.draw_on_floor = False
                y = settings.SCREEN_HEIGHT - i - 1
                md.coords = [((x, y), libtcod.white) for x in range(len(md.sentence) + 1)]
            
        self.mutated_text = self.mutated_text[len(tiles_to_write):]
            
    def create_ocean_text(self, novel):
        print "schimband..."
        num_cells = 10000
        prose = novel.generate_markov_text(size=num_cells/3)
        while not prose:
            prose = novel.generate_markov_text(size=num_cells/3)
        text = prose
        text = text.replace("Bernard", "XXXXXXX")
        text = text.replace("Jinny", "XXXXX")
        text = text.replace("Louis", "XXXXX")
        text = text.replace("Neville", "XXXXXXX")
        text = text.replace("Rhoda", "XXXXX")
        text = text.replace("Susan", "XXXXX")
        text = text.replace("Percival", "PPPPPPPP")
        return text

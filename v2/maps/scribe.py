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
            
    def organize_directives_for_writing(self, num_tiles):
        mandatory_directives = []
        optional_directives = []
        directives_to_write = []
        empty_places = self.mutated_text.count('. ', 0, num_tiles)
        print empty_places, "empties"
        
        for d in self.directives.itervalues():
            d.coords = []
            if d.player_in_range():
                # the worry here is that some node locations might
                # not be available, or map well, to where the scribe
                # activates, leading to "missing" or dead directives.
                # it also duplicates functionality with enabling and
                # disabling them.
                if d.mandatory:
                    mandatory_directives.append(d)
                else:
                    optional_directives.append(d)

        optional_directives.sort(key=lambda x: x.priority)
        directives_to_write = (mandatory_directives + optional_directives)[:empty_places]
        if len(directives_to_write) < empty_places:
            directives_to_write += [None] * (empty_places - len(directives_to_write))
                
        shuffle(directives_to_write)
        
        return directives_to_write
        
    def write_floor(self, tiles_to_write):
        # this most likely continues to be the most time-intensive
        # part of the program, given that it is called every frame
        # of movement and you loop through the entire visible area
        # (again). something to think about.
        
        num_tiles = len(tiles_to_write)
        if len(self.mutated_text) < num_tiles:
            self.mutated_text = self.create_ocean_text(self.waves)
        num_directive_letters = 0
        
        directives_to_write = self.organize_directives_for_writing(num_tiles)
        current_directive = None
        end_of_current_sentence = 0
        len_directives_written = 0
        just_finished_one = False
        
        for i, t in enumerate(tiles_to_write):
            current_place_in_text = i - len_directives_written
            current_letter = self.mutated_text[current_place_in_text]
            previous_letter = self.mutated_text[current_place_in_text - 1]
            previouser_letter = self.mutated_text[current_place_in_text - 2]
            t.current_char = current_letter
            
            if previous_letter == ' ' and previouser_letter == '.':
                end_of_sentence = True
            else:
                end_of_sentence = False
            if not current_directive and not just_finished_one and (
                                directives_to_write and end_of_sentence):
                current_directive = directives_to_write.pop(0)
                if current_directive is None:
                    continue
                end_of_current_sentence = i + len(current_directive.sentence)
                if end_of_current_sentence < num_tiles:
                    current_directive.draw_on_floor = True
                    current_directive.visible = True
                    len_directives_written += 1
                else:
                    current_directive.visible = False
                    current_directive = None
            just_finished_one = False
            if current_directive and i >= end_of_current_sentence:
                current_directive = None
                just_finished_one = True
            if current_directive:
                current_directive.coords.append( ((t.x, t.y), t.current_color) )
                len_directives_written += 1
            
        if directives_to_write: # i.e., if /still/ directives_to_write
            for i, md in enumerate(directives_to_write):
                if md is not None:
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

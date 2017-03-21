from random import randint, choice

import libtcodpy as libtcod

from items import Flashlight
from tile import EnvironmentTile, BottomlessPit
from observer import Listener
from scribe import TheScribe
import markovgen as mg
import tools

import drawings


class TileMap(Listener, object):
    def __init__(self, w, h, con, game):
        self.con = con
        self.game = game
        self.drawing = drawings.cave
        self.width, self.height = self.drawing.w, self.drawing.h
        self.tilemap = [[
                    drawings.make_tile(self.drawing, x, y, self.con, self.game)
                    for y in xrange(self.height)]
                    for x in xrange(self.width)]
                            
        self.libtcod_map = libtcod.map_new(self.width, self.height)
        for t in self.get_tiles():
            libtcod.map_set_properties(self.libtcod_map, t.x, t.y, 
                                       t.transparent, not t.blocked)
           
        self.light_sources = []
           
        with open('waves.txt', 'r') as f:
            self.waves = mg.Markov(f)
        with open('nightland.txt', 'r') as f:
            self.nightland = mg.Markov(f)
        with open('goblin.txt', 'r') as f:
            self.goblins = mg.Markov(f)

        self.obs = []
        self.render_area = (0, 0, 0, 0, "default")
        self.last_render = []
        
        self.mutated_text = []
        
        self.scribe = TheScribe()
        self.scribe.add_directive
        
    def load_doodad(self, x, y, doodad):
        for t in doodad.get_tile_data():
            blocked, c, r = t
            if blocked:
                blocked = True
            else:
                blocked = False
            self.change_tile(x + c, y + r, blocked)
        for t in self.get_tiles():
            libtcod.map_set_properties(self.libtcod_map, t.x, t.y, 
                                       not t.blocked, not t.blocked)

    def change_tile(self, x, y, blocked, schimb=False):
        in_square = self.tilemap[x][y].next
        new_tile = drawings.make_tile(self.drawing, x, y, self.con, self.game, blocked)
        self.tilemap[x][y] = new_tile
        self.tilemap[x][y].next = in_square
        libtcod.map_set_properties(self.libtcod_map, x, y, 
                                   new_tile.transparent, not new_tile.blocked)
        if schimb:
            self.game.player.schimb = True
        
    def get_tile(self, x, y):
        try:
            return self.tilemap[x][y]
        except IndexError:
            print x, y
            return False

    def can_schimb(self, x, y):
        return not self.get_tile(x, y).blocked
            
    def get_area(self, x, y, w, h, anchor="center"):
        if anchor == "center":
            Xstart = x - w/2
            Xend = x + (w/2 if w%2 else w/2 + 1)
            Ystart = y - h/2
            Yend = y + (h/2 if h%2 else h/2 + 1)
        else:
            Xstart, Xend = x, x + w
            Ystart, Yend = y, y + h
            
        if Xstart < 0: Xstart = 0
        if Xend >= self.width: Xend = self.width
        if Ystart < 0: Ystart = 0
        if Yend >= self.height: Yend = self.height
        
        for y in xrange(Ystart, Yend):
            for x in xrange(Xstart, Xend):
                yield self.tilemap[x][y]

    def get_round_area(self, origin, radius):
        for p in tools.generate_Z2(radius, origin):
            try:
                yield self.tilemap[p[0]][p[1]]
            except IndexError:
                continue
            
    def get_item(self, x, y):
        try:
            tile = self.tilemap[x][y]
            while tile.next:
                tile = tile.next
            while tile:
                if isinstance(tile, Flashlight):
                    return tile
                tile = tile.prev
            return None
        except IndexError:
            return False

    def get_tiles(self):
        for y in xrange(self.height):
            for x in xrange(self.width):
                yield self.tilemap[x][y]
                
    def get_tiles_in_render_area(self):
        player = self.game.player
        return self.get_area(player.x-player.max_sight, 
                             player.y-player.max_sight, 
                             player.max_sight*2,        # but it performs
                             player.max_sight*2,        # fine and solves
                             anchor="default")          # update problems

    def get_tiles_in_clear_area(self):
        x, y, w, h, anchor = self.render_area
        return self.get_area(x - 2, y - 2, w + 4, h + 4, anchor=anchor)
        
    def get_all_in_render_area(self):
        return self.get_tiles_by_layer(self.get_tiles_in_render_area())
        
    def get_all_in_clear_area(self):
        return self.get_tiles_by_layer(self.get_tiles_in_clear_area())
                
    def get_visible_tiles(self, tiles):
        for t in tiles:
            if t.is_visible():
                yield t

    def get_all_tiles(self):
        return self.get_tiles_by_layer(self.get_tiles())

    def get_tiles_by_layer(self, tiles):
        schimber_yield = False
        while tiles:
            next_layer = []
            for t in tiles:
                if t.next:
                    next_layer.append(t.next)
                yield t
            if not schimber_yield:
                yield self.schimber
                schimber_yield = True
            tiles = next_layer

    def get_NSEW(self, x, y):
        targets = [(x, y-1), (x, y+1), (x+1, y), (x-1, y)]
        failures = 0
        for t in targets:
            try:
                yield self.tilemap[t[0]][t[1]]
            except IndexError:
                failures += 1
                
    def add(self, x, y, unit):
        tail = self.tilemap[x][y]
        while tail.next:
            tail = tail.next
        tail.next = unit
        unit.prev = tail
        return unit

    def remove(self, unit):
        if not unit.prev:
            return
        if unit.next:
            unit.prev.next = unit.next
            unit.next.prev = unit.prev
        else:
            unit.prev.next = None
        unit.next = None
        unit.prev = None
        
    def move(self, x, y, unit):
        self.remove(unit)
        self.add(x, y, unit)
        
    def run_collision(self, x, y):
        try:
            unit = self.tilemap[x][y]
        except IndexError:
            unit = None
            print "Out of bounds!"
        while unit:
            if unit.blocked:
                return True
            unit = unit.next
        return False
        
    def _schimb(self, novel):
        print "schimband..." # needs the uh din ah.
        num_cells = self.width * self.height
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

    def apply_tile_effect(self, frame_data, mode="add", 
                          anchor=(0, 0), set_effect=None):
        # frame_data is a dict:
        # {(x, y):[(color, char), ...], (x, y): ...}
        for xy, effect in frame_data.iteritems():
            x, y = xy[0] + anchor[0], xy[1] + anchor[1]
            tile = self.get_tile(x, y)
            if set_effect:
                tile.effects_mode = set_effect
            colors, chars = zip(*effect)
            if not self.run_collision(x, y):
                if mode == "add":
                    if colors:
                        tile.color_queue.extend(colors)
                    if chars:
                        tile.char_queue.extend(chars)
                if mode == "replace":
                    if colors:
                        tile.color_queue = list(colors)
                    if chars:
                        tile.char_queue = list(chars)

    def schimb(self, tiles=None):
        # you call this EVERY FRAME OF MOVEMENT!!
        # so, uh, maybe work on it a bit. to do: 
        # separate out into its own method the checks
        # for being seen and unblocked. the "floor check"
    
        if tiles is None:
            render_tiles = self.get_tiles_in_render_area()
            visible_environment = self.get_visible_tiles(render_tiles)
            tiles_to_write = [x for x in visible_environment if not x.blocked]
        else:
            tiles_to_write = tiles
            
        # NEW WAY    
        return self.scribe.write_floor(tiles_to_write)
        # NEW WAY
            
        num_tiles = len(tiles_to_write)
        word_len = len(self.schimber.sentence)
        word_pos = num_tiles
        self.schimber.coords = []
        room = 0
        
        if len(self.mutated_text) < num_tiles:
            self.mutated_text = self._schimb(self.waves)

        num_spaces = self.mutated_text.count('.', 0, num_tiles)
        try:
            chosen_space = randint(0, num_spaces - 1)
        except ValueError:
            chosen_space = 0

        for i, t in enumerate(tiles_to_write):
            if room:
                if room > 1:
                    if len(self.schimber.coords) < word_len:
                        self.schimber.coords.append( ((t.x, t.y), t.current_color) )
                room += 1

            if word_pos < num_tiles:
                if i <= word_pos + word_len:
                    letter = ' '
                else:
                    letter = self.mutated_text[i - word_len - 1]
            else:
                letter = self.mutated_text[i]
            if letter == '.' and not room and self.schimber.player_in_range():

                if i + word_len + 1 < num_tiles:  # that '1' is because we write the sentence one space over
                    room = 1
                    word_pos = i
                else:
                    pass

            t.current_char = letter

        if room and self.schimber.coords:
            self.schimber.visible = True
        else:
            self.schimber.visible = False
            
        self.mutated_text = self.mutated_text[len(tiles_to_write):]
                    
    def on_notify(self, entity, event):
        if event == "player move":
            fade = [libtcod.Color(a, a, a) 
                    for a in xrange(255, libtcod.darkest_grey.r, -10)]
            if entity.left_foot:
                foot_displacement = entity.left_foot_displacement
            else:
                foot_displacement = 0
            x = entity.x + (entity.facing[1]*foot_displacement)
            y = entity.y + (entity.facing[0]*foot_displacement)
            if self.run_collision(x, y):
                entity.left_foot_displacement *= (-1)
                foot_displacement = entity.left_foot_displacement
            x = entity.x + (entity.facing[1]*foot_displacement)
            y = entity.y + (entity.facing[0]*foot_displacement)
            self.apply_tile_effect({(x, y): [(color, '.') for color in fade]})


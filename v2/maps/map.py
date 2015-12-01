from random import randint, choice

import libtcodpy as libtcod

from items import Item, Flashlight
from tile import EnvironmentTile
from observer import Listener
import markovgen as mg
import tools


class TileMap(Listener, object):
    def __init__(self, w, h, con, game):
        self.con = con
        self.game = game
        self.width, self.height = w, h
        walls = []
        for L in [(25, 0, 25, 15), (0, 16, 15, 16)]:
            libtcod.line_init(*L)
            while True:
                x, y = libtcod.line_step()
                if x is None:
                    break
                walls.append((x, y))
        self.tilemap = [[EnvironmentTile(
                (True if (x, y) in walls else False), 
                x, y, '@', libtcod.darkest_grey, self.con, self.game
                                         )
                            for y in range(h)]
                            for x in range(w)]
                            
        self.libtcod_map = libtcod.map_new(self.width, self.height)
        for t in self.get_tiles():
            libtcod.map_set_properties(self.libtcod_map, t.x, t.y, not t.blocked, not t.blocked)
           
        self.light_sources = []
           
        with open('waves.txt', 'r') as f:
            self.waves = mg.Markov(f)
        with open('race.txt', 'r') as f:
            self.race = mg.Markov(f)
            
        self.obs = []
        self.render_area = (0, 0, 0, 0, "default")
        
    def load_doodad(self, x, y, doodad):
        for t in doodad.get_tile_data():
            blocked, c, r = t
            if blocked:
                blocked = True
            else:
                blocked = False
            self.change_tile(x + c, y + r, blocked)
        for t in self.get_tiles():
            libtcod.map_set_properties(self.libtcod_map, t.x, t.y, not t.blocked, not t.blocked)

    def change_tile(self, x, y, attr):
        in_square = self.tilemap[x][y].next
        self.tilemap[x][y] = EnvironmentTile(
                attr, 
                x, y, '@', libtcod.darkest_grey, self.con, self.game
                                         )
        self.tilemap[x][y].next = in_square                                 
        
    def get_tile(self, x, y):
        try:
            return self.tilemap[x][y]
        except IndexError:
            return False
            
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
        
        for y in range(Ystart, Yend):
            for x in range(Xstart, Xend):
                yield self.tilemap[x][y]
            
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
        for y in range(self.height):
            for x in range(self.width):
                yield self.tilemap[x][y]
                
    def tile_is_lit(self, x, y):
        player = self.game.player
        for l in self.light_sources + [player]:
            Lradius = (l.Lradius if not l is player else l.sight_radius)
            if tools.get_distance((x, y), l.get_location()) <= Lradius:
                return True
        return False
        
    def get_tiles_in_render_area(self):
        player = self.game.player
        def x(light):
            return light.get_location()[0]
        def y(light):
            return light.get_location()[1]
        Xmins = [x(l) - l.Lradius for l in self.light_sources]
        Xmaxs = [x(l) + l.Lradius for l in self.light_sources]
        Ymins = [y(l) - l.Lradius for l in self.light_sources]
        Ymaxs = [y(l) + l.Lradius for l in self.light_sources]
        PXmin = player.x - player.sight_radius - 1
        PXmax = player.x + player.sight_radius + 1
        PYmin = player.y - player.sight_radius - 1
        PYmax = player.y + player.sight_radius + 1
        minX, minY = min([PXmin] + (Xmins if Xmins else [])), min([PYmin] + (Ymins if Ymins else []))
        maxX, maxY = max([PXmax] + (Xmaxs if Xmaxs else [])), max([PYmax] + (Ymaxs if Ymaxs else []))
        w = maxX - minX
        h = maxY - minY
        self.render_area = minX, minY, w, h, "default"
        return self.get_area(minX, minY, w, h, anchor="default")

    def get_tiles_in_clear_area(self):
        x, y, w, h, anchor = self.render_area
        return self.get_area(x - 2, y - 2, w + 4, h + 4, anchor=anchor)
        
    def get_all_in_render_area(self):
        return self.get_tiles_by_layer(self.get_tiles_in_render_area())
        
    def get_all_in_clear_area(self):
        return self.get_tiles_by_layer(self.get_tiles_in_clear_area())
                
    def get_visible_tiles(self, tiles):
        for t in tiles:
            if t.is_visible() and self.tile_is_lit(*t.get_location()):
                yield t
                
    def get_lit_tiles(self, tiles):
        for t in tiles:
            if self.tile_is_lit(*t.get_location()):
                yield t
    
                
    def get_tiles_by_layer(self, tiles):
        while tiles:
            next_layer = []
            for t in tiles:
                if t.next:
                    next_layer.append(t.next)
                yield t
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
        old_chain = unit.prev
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
        self.schimb()
        
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
        num_cells = self.width * self.height
        prose = novel.generate_markov_text(size=num_cells/3)
        while not prose:
            prose = novel.generate_markov_text(size=num_cells/3)
        text = prose[0:num_cells]
        text = text.replace("Bernard", "XXXXXXX")
        text = text.replace("Jinny", "XXXXX")
        text = text.replace("Louis", "XXXXX")
        text = text.replace("Neville", "XXXXXXX")
        text = text.replace("Rhoda", "XXXXX")
        text = text.replace("Susan", "XXXXX")
        text = text.replace("Percival", "PPPPPPPP")
        return text
        
        
    def schimb(self):
        waves = self._schimb(self.waves)
        race = self._schimb(self.race)
        wletter = 0
        rletter = 0
        for i, t in enumerate(self.get_lit_tiles(self.get_tiles_in_clear_area())):
            if not t.blocked:
                t.char = waves[wletter]
                wletter += 1
            elif t.blocked:
                t.char = race[rletter]
                while t.char == ' ':
                    rletter += 1
                    t.char = race[rletter]
            rletter += 1        
                    
    def on_notify(self, entity, event):
        if event == "player move":
            self.schimb()
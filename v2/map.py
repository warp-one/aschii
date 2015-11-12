from random import randint

import libtcodpy as libtcod

from items import Item, Flashlight
from tile import EnvironmentTile
from observer import Listener
import markovgen as mg

class BoardSetup(object):
    pass

class TileMap(Listener, object):
    def __init__(self, w, h, con, game):
        self.con = con
        self.game = game
        self.width, self.height = w, h
        self.tilemap = [[EnvironmentTile(
                (False if randint(-6, 1) < 2 else True), 
                x, y, '@', libtcod.darkest_grey, self.con, self.game
                                         )
                            for y in range(h)]
                            for x in range(w)]
                            
        self.libtcod_map = libtcod.map_new(self.width, self.height)
        for t in self.get_tiles():
            libtcod.map_set_properties(self.libtcod_map, t.x, t.y, not t.blocked, not t.blocked)
           
        self.light_sources = []
           
        with open('waves.txt', 'r') as f:
            self.text = mg.Markov(f)
            
        self.obs = []
        
    def get_tile(self, x, y):
        try:
            return self.tilemap[x][y]
        except IndexError:
            return False
            
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
                
    def get_visible_tiles(self):
        for t in self.get_tiles():
            if t.is_visible():
                yield t
                
    def get_tiles_by_layer(self):
        tiles = self.get_tiles()
        while True:
            next_layer = []
            for t in tiles:
                if t.next:
                    next_layer.append(t.next)
                yield t
            if next_layer:
                tiles = next_layer
            else:
                break
                     
            

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
        
    def run_collision(self, x, y):
        unit = self.tilemap[x][y]
        while unit:
            if unit.blocked:
                return True
            unit = unit.next
        return False
        
    def schimb(self):
        num_cells = self.width * self.height
        prose = self.text.generate_markov_text(size=num_cells/3)
        text = prose[0:num_cells]
        text = text.replace("Bernard", "XXXXXXX")
        text = text.replace("Jinny", "XXXXX")
        text = text.replace("Louis", "XXXXX")
        text = text.replace("Neville", "XXXXXXX")
        text = text.replace("Rhoda", "XXXXX")
        text = text.replace("Susan", "XXXXX")
        text = text.replace("Percival", "PPPPPPPP")
        special_letters = set()
        for i, t in enumerate(self.get_visible_tiles()):
            if not t.blocked:
                t.char = text[i]
        while len(special_letters) < 6:
            special_letters.add(randint(0, num_cells - 1))
        self.notify(special_letters, "SCHIMB")
        
    def on_notify(self, entity, event):
        if event == "player move":
            self.schimb()
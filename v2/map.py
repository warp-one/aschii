from random import randint

import libtcodpy as libtcod

from tile import EnvironmentTile
import markovgen as mg

class TileMap(object):
    def __init__(self, w, h, con, game, player):
        self.con = con
        self.game = game
        self.width, self.height = w, h
        self.tilemap = [[EnvironmentTile(
                (False if randint(-6, 1) < 1 else True), 
                x, y, '@', libtcod.darkest_grey, self.con, self.game
                                         )
                            for y in range(h)]
                            for x in range(w)]
                            
        with open('waves.txt', 'r') as f:
            self.text = mg.Markov(f)
            
        self.obs = []
        self.add_observer(player)

    def get_tiles(self):
        for y in range(self.height):
            for x in range(self.width):
                yield self.tilemap[x][y]

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
        
    def remove(self, x, y, unit):
        if unit.next:
            unit.prev.next = unit.next
        else:
            unit.prev.next = None
        unit.next = None
        unit.prev = None
        
    def run_collision(self, x, y):
        unit = self.tilemap[x][y]
        while unit:
            if unit.blocked:
                return True
            unit = unit.next
        return False
        
    def add_observer(self, observer):
        self.obs.append(observer)
        
    def remove_observer(self, observer):
        self.obs.remove(observer)
        
    def notify(self, entity, event):
        for o in self.obs:
            o.on_notify(entity, event)
            
    def schimb(self):
        num_cells = self.width * self.height
        prose = self.text.generate_markov_text(size=num_cells/3)
        text = prose[0:num_cells]
        special_letters = set()
        for i, t in enumerate(self.get_tiles()):
            if not t.blocked:
                t.char = text[i]
        while len(special_letters) < 6:
            special_letters.add(randint(0, num_cells - 1))
        self.notify(special_letters, "SCHIMB")
        
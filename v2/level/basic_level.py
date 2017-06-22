import libtcodpy as libtcod

import settings, narrative
from maps import TileMap
from player import Player


class Camera(object):
    
    camera_x = 0
    camera_y = 0
    
    def __init__(self, level):
        self.map_width, self.map_height = settings.LVL0_MAP_WIDTH, settings.LVL0_MAP_HEIGHT
        self.w = settings.SCREEN_WIDTH
        self.h = settings.SCREEN_HEIGHT

    def to_camera_coordinates(self, x, y):
        x, y = x - self.camera_x, y - self.camera_y
        return x, y
        
    def move_camera(self, target_x, target_y):
        x = target_x - self.w/2
        y = target_y - self.h/2
        
        if x < 0: x = 0
        if y < 0: y = 0
        x_overset = self.map_width - self.w - 1
        y_overset = self.map_height - self.h - 1
        if x > x_overset: x = x_overset
        if y > y_overset: y = y_overset
        
        self.camera_x, self.camera_y = x, y


class Level(object):

    start_location = 5, 15
    hud = []

    def __init__(self, game, map_drawing):
        self.game = game
        self.create_consoles()
        self.the_map = TileMap(self.game.width, self.game.height, map_drawing, self.foreground, self)
        self.tilemap = self.the_map.tilemap
        self.camera = Camera(self)
        self.player = Player(3, 3, ' ', libtcod.white, self.foreground, self)
        self.player.add_observer(self.the_map)
        self.player.place(*self.start_location)
        
        self.narrative = narrative.RunningNarrative(self)
        
        self.last_render = []
        self.next_render = []
        self.special_effects = []
        
    def create_consoles(self):
        self.background = libtcod.console_new(self.game.width, self.game.height)
        self.foreground = libtcod.console_new(self.game.width, self.game.height)
        libtcod.console_set_default_background(self.background, libtcod.blue)
        self.consoles = [self.background, self.foreground]

    def update_all(self):
        self.next_render = [x for x in self.the_map.get_all_in_render_area()]
        self.player.update()
        for t in self.next_render:
            if t is self.player:
                continue
            t.update()
        for i in self.hud:
            i.update()
        for e in self.special_effects:
            e.update()
            
    def render_all(self):
        self.camera.move_camera(self.player.x, self.player.y)
        for t in self.next_render:
            t.draw()
        for i in self.hud:
            i.draw()
        self.last_render = self.next_render
        self.next_render = []

    def clear_all(self):
        for t in self.last_render:
            t.clear()
        for i in self.hud:
            i.clear()
        self.last_render = []
        
        for a in self.player.action_manager.actions:
            a.clear()


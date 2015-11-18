from pyglet.window import key
import pyglet

import screen, resources

class LevelAdministrator(screen.Screen):
    def __init__(self, game):
        self.game = game
        self.foreground = pyglet.graphics.OrderedGroup(1)
        self.background = pyglet.graphics.OrderedGroup(0)
        
    def on_key_press(self, symbol, modifiers):
        pass            

    def start(self):
        self.batch = pyglet.graphics.Batch()
        print "GO"

    def on_draw(self):
        self.game.window.clear()
        self.batch.draw()

    def clear(self):
        pass
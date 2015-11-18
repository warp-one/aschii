import pyglet
from pyglet.window import key

import screen, resources

class MainMenu(screen.Screen):
    def __init__(self, game):
        self.game = game
        
    def handleNewGame(self):
        self.game.startPlaying()
                                             
    def on_key_press(self, symbol, modifiers):
        if symbol == key.SPACE:
            self.game.startPlaying()
        else:
            pass
        
    def clear(self):
        pass
        
    def start(self):
        self.batch = pyglet.graphics.Batch()
        self.hello = pyglet.sprite.Sprite(img=resources.title, 
                                          x=0, 
                                          y=0, 
                                          batch=self.batch)
        
    def on_draw(self):
        self.game.window.clear()
        self.batch.draw()

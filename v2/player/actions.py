import libtcodpy as libtcod

class ActionManager(object):
    def __init__(self, player):
        self.actions = []
        self.current_actions = []
        self.player = player
        
    def add_action(self, action):
        self.actions.append(action)
        
    def remove_action(self, action):
        if action in self.actions:
            if action in self.current_actions:
                self.current_actions.remove(action)
            self.actions.remove(action)
        
    def handle_letter(self, key):
        letter = (chr(key.c) if key.c else key.vk)
        for a in self.actions:
            if a.dormant_color == libtcod.grey:
                continue
            if a.tick_phrase(letter):
                if a.active:
                    pass
                else:
                    a.toggle_active()
            else:
                if a.active:
                    a.reset()
                    a.toggle_active()
        
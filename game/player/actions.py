import libtcodpy as libtcod

class ActionManager(object):

    static_directive_slots = {(5, 5):None, (15, 5):None, (5, 15):None, (15, 15):None}

    def __init__(self, player):
        self.actions = []
        self.current_actions = []
        self.player = player
        
    def add_action(self, action):
        self.actions.append(action)
        if action.static and action.arrangeable:
            for coord, directive in self.static_directive_slots.iteritems():
                if directive is None:
                    self.static_directive_slots[coord] = action
                    action.offset = coord
                break

    def request_static_slot(self, action):
        for coord, directive in self.static_directive_slots.iteritems():
            if directive is None:
                self.static_directive_slots[coord] = action
                action.screen_location = coord
            break
        else:
            return False

    def drop_static_slot(self, coord):
        self.static_directive_slots[coord] = None
        
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
        
class ActionMenu(object):
    def __init__(self):
        self.actions = {}
        
    def add_action(self, action):
        self.actions.append(action)
        action.y = self.actions.index(action)
        
    def remove_action(self, action):
        self.actions.remove(action)
        for i, a in enumerate(self.actions):
            a.y = i
            
        
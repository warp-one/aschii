class Listener(object):
    def add_observer(self, observer):
        self.obs.append(observer)
        
    def remove_observer(self, observer):
        self.obs.remove(observer)

    def notify(self, entity, event):
        for o in self.obs:
            o.on_notify(entity, event)
            

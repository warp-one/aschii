class DirectiveGrouper(object):
    def __init__(self, level):
        self.level = level
        self.directives = {}
        
    def add_directive(self, directive, trigger):
        #these directives are a type, their args, and their kwargs
        try:
            self.directives[trigger].append(directive)
        except KeyError:
            self.directives[trigger] = [directive]
        
    def remove_directives(self, trigger):
        del self.directives[trigger]
    
    def complete_directive(self, trigger):
        print trigger
        for d in self.directives[trigger]:
            print trigger, d
            new_directive = d[0](*d[1], **d[2])
            new_directive.story_group = self
            self.level.player.add_child(new_directive)
            print new_directive.phrase + "is here!"
        self.remove_directives(trigger)
                    
    def start(self):
        self.complete_directive("start")
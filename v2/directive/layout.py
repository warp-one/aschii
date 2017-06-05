class DirectiveLayout(object):
    def __init__(self, period, width, height, split, direction):
        self.period = period
        self.width = width
        self.height = height
        self.split = split
        self.direction = direction
        
    def modulate(self, x, y, i, in_range):
        line = i/self.width
        return x + i%self.width, y + line
            
    def tick(self, width):
        pass
                    
class RollingLayout(DirectiveLayout):
    def modulate(self, x, y, i, in_range):
        x, y = super(RollingLayout, self).modulate(x, y, i, in_range)
        if in_range:
            y = (y if i > self.split else y - self.direction) - self.height
        return x, y
            
    def tick(self, width):
        self.width = width
        if True:#not randint(0, 4):
            self.split += 1
            if self.split >= self.width:
                self.split = 0
                self.height += self.direction
                if self.height >= self.period:
                    self.direction = -1
                elif self.height <= 0:
                    self.direction = 1

                    
class RectangleLayout(DirectiveLayout):
    def __init__(self, *args):
        super(RectangleLayout, self).__init__(*args)
        self.set_rectangle()
        
        
    def set_rectangle(self):
        self.rectangle_top = [(w, -self.height) for w in range(self.width)]
        self.rectangle_right = [(self.width - 1, -h) for h in range(self.height - 1, 1, -1)]
        self.rectangle_bottom = [(w, -1) for w in range(self.width)]
        self.rectangle_left = [(0, -h) for h in range(self.height - 1, 1, -1)]
        self.rectangle = self.rectangle_top + self.rectangle_left + self.rectangle_right + self.rectangle_bottom 
        
    def modulate(self, x, y, i, in_range):
        try:
            space = self.rectangle[i]# if self.direction == 1 else self.rectangle[-i]
        except IndexError:
            return x, y
        return x + space[0] - 1, y + space[1] + self.height - 1

        
    def tick(self, width):
        pass

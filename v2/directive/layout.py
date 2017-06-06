from random import randint


class DirectiveLayout(object):
    def __init__(self, period, width, height, split, direction):
        self.period = period
        self.width = width
        self.height = height
        self.split = split
        self.direction = direction
        self.words = None
        
    def get_coords(self, x, y, len_sentence):
        coords = []
        for i in range(len_sentence):
            line = i/self.width
            coords.append((x + i%self.width, y + line))
        return coords
        
    def modulate(self, x, y, i, in_range):
        line = i/self.width
        return x + i%self.width, y + line
            
    def tick(self, width):
        pass


class RollingLayout(DirectiveLayout):
    def get_coords(self, x, y, len_sentence):
        coords = super(RollingLayout, self).get_coords(x, y, len_sentence)
        for i, c in enumerate(coords):
            if i < self.split:
                coords[i] = c[0], c[1] - self.direction - self.height
            else:
                coords[i] = c[0], c[1] - self.height
        while len(coords) < len_sentence:
            coords.append((0, 0))
        return coords
        
    def modulate(self, x, y, i, in_range): # use for completion effect
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
        
    def get_coords(self, x, y, len_sentence):
        coords = []
        for r in self.rectangle:
            coords.append((x + r[0], y + r[1] + self.height))
        while len(coords) < len_sentence:
            coords.append((0, 0))
        return coords
        
    def modulate(self, x, y, i, in_range): # use for completion effect
        try:
            space = self.rectangle[i]# if self.direction == 1 else self.rectangle[-i]
        except IndexError:
            return x, y
        return x + space[0], y + space[1] + self.height

        
    def tick(self, width):
        pass
        

class ScatterLayout(DirectiveLayout):
    def __init__(self, points):
        self.points = points
        Xs = [x for (x, _) in self.points]
        Ys = [y for (_, y) in self.points]
        self.minX = min(Xs)
        self.maxX = max(Xs)
        self.minY = min(Ys)
        self.maxY = max(Ys)

    def get_coords(self, x, y, len_sentence):
        coords = []
        if self.words:
            while len(self.points) < len(self.words):
                x = randint(self.minX, self.maxX)
                y = randint(self.minY, self.maxY)
                self.points.append((x, y))
            for i, w in enumerate(self.words):
                px, py = self.points[i]
                word_len = len(w) + 1
                coords.extend([(x + j + px, y + py) for j in range(word_len)])
        return coords
        
    def tick(self, width):
        pass

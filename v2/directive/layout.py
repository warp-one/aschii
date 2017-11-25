from random import randint, shuffle

import settings

class HUDLayoutTracker(object):
    directives = [None] * 4
    def add_directive(self, directive):
        for i, d in enumerate(HUDLayoutTracker.directives):
            if d is None:
                HUDLayoutTracker.directives[i] = d
                return
        return False


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
        
        
class NarrativeLayout(DirectiveLayout):
    def __init__(self):
        self.n_width = settings.SCREEN_WIDTH - 11
        
    def get_coords(self, x, y, len_sentence):
        coords = []
        line = 0
        current_x = x
        for i in xrange(len_sentence):
            line = (x + i)/self.n_width
            lx = (x + i)%self.n_width
            coords.append((lx, y + line))
        return coords
        
    def tick(self, indentation):
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


class GatherLayout(DirectiveLayout):
    def __init__(self, directive, *args):
        super(GatherLayout, self).__init__(*args)
        self.directive = directive
        self.letter_pile = []
        starting_x, current_y = 0, 0
        current_x = starting_x
        ox, oy = self.directive.offset
        while len(self.letter_pile) < len(self.directive.phrase):
            self.letter_pile.append((current_x - ox, current_y - oy - 5))
            current_x += 1
            if current_x > abs(starting_x):
                current_y += 1
                starting_x -= 1
                current_x = starting_x
        shuffle(self.letter_pile)
       
    def get_coords(self, x, y, len_sentence):
        coords = super(GatherLayout, self).get_coords(x, y, len_sentence)
        unguessed_len = len(self.directive.phrase) - len(self.directive.guessed)
        unguessed_start = self.directive.phrase_location + len(self.directive.guessed) 
        unguessed_end = unguessed_start + unguessed_len 
        coords[unguessed_start:unguessed_end] = [(p[0] + x, p[1] + y)
                                                 for p in self.letter_pile[:unguessed_len]]
        return coords
        
        
class MarqueeLayout(DirectiveLayout):
    pass
    
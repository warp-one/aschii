class Orders(object):
    def create_orders(self):
        self.orders = [] # (t, callable)
        self.current_action = None
        self.current_params = []
        self.time_left = 0
        self.path = []
        
    def act(self):
        if self.current_action:
            if self.current_params:
                self.current_action(*self.current_params)
            else:
                self.current_action()
            self.time_left -= 1
            if self.time_left <= 0:
                self.end_action()
        else:
            if self.orders:
                self.time_left, self.current_action, self.current_params = self.orders.pop(0)
                
    def add_order(self, time, order, params):
        self.orders.append((time, order, (params if params else [])))
        
    def move_along_path(self):
        try:
            next_tile = self.path.pop(0)
        except IndexError:
            self.end_action()
            return
        dx = next_tile[0] - self.x
        dy = next_tile[1] - self.y
        if self.game.the_map.run_collision(self.x + dx, self.y + dy):
            self.end_action()
            return
        self.move(dx, dy)
        
    def set_path(self, path):
        self.path = path
        return self.path
        
    def get_path(self, start, finish):
        self.path = []
        x_dif = finish[0] - start[0] 
        y_dif = finish[1] - start[1]
        if x_dif: 
            x_sign = x_dif/abs(x_dif)
        else:
            x_sign = 1
        for x in range(x_sign, x_dif + 1, x_sign):
            self.path.append((start[0] + x, start[1]))
        if y_dif: 
            y_sign = y_dif/abs(y_dif)
        else:
            y_sign = 1
        for y in range(y_sign, y_dif + 1, y_sign):
            self.path.append((start[0] + x_dif, start[1] + y))
        return self.path
        
    def end_action(self):
        self.current_action = None
        self.time_left = 0

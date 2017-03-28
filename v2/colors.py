from random import randint

fire_colorset = [(250, 225, 80),  #yellow
                 (219, 64, 16),   #orange-red
                 (255, 244, 142), #pale yellow
                 (254, 141, 1)    #orange
                 ]
                 
random_colorset = [(randint(0, 255), randint(0, 255), randint(0, 255)) for _ in range(4)]
import libtcodpy as libtcod

from player import Player

class TestLevel(Object):
    def __init__(self, con):
        self.con = con
    
    
        self.player = Player(15, 15, ' ', libtcod.white, self.foreground, self)
        
        
        
        
        
        
        
        
        
        
        

        self.create_consoles()
        self.add_map()
        self.player.move(5, 5)
        self.player.add_power(Power(self.player, self, static=True, offset=(0, 30+len(self.player.children))))
        self.player.add_power(Sprint(self.player, self, text="sprint", static=True, offset=(0, 30+len(self.player.children))))
        self.player.add_observer(self.the_map)
        
        self.statues = []
        for _ in range(1):
            s = tile.Statue(['He dreamt that it was alive, tremulous', 'it was not the atrocious bastard', 'of a tiger and a colt, but', 'at the same time both of these', 'fiery creatures, and also', 'a bull, a rose, and a storm'], 10 + _*3, 10 + _, 'S', libtcod.green, self.foreground, self)
            self.statues.append(s)
            self.the_map.add(s.x, s.y, s)
            self.player.add_child(Next(s, self, text="bow", static=True, offset = (2, 2)))
            self.player.add_child(Waypoint(s, self, text="approach", static=True, offset=(-1,-1)))
        s = self.the_map.schimb()

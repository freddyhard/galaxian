from player import Player
from states import States

class Laser(Player):
    def __init__(self, x, y, sprite):
        Player.__init__(self, x, y - 7, sprite)
        
        
        self.inActiveY = y - 7
        self.active = False

     
    def move(self, x, galaxians):
        if self.active:
            # updates the sprite and hit rectangle
            Player.move(self)
            
            state = States()
            for f in range(len(galaxians)):
                if self.hitArea.colliderect(galaxians[f].hitArea):
                    x_offset = self.hitArea[0] - galaxians[f].hitArea[0]
                    y_offset = self.hitArea[1] - galaxians[f].hitArea[1]
                    
                    if galaxians[f].getMask().overlap(self.mask, (x_offset, y_offset)):
                        galaxians[f].destroyed = True
                        if galaxians[f].state == state.FORMATION_DIVING and galaxians[f].number != 17 and galaxians[f].number != 33:
                            self.reduceDivingArray(galaxians, galaxians[f].number)
                        self.active = False
                        # no BREAK - let it run through array of galaxians,
                        # because a laser can destroy multiple galaxians
            
            # only move if active other wise reinitialise back to rocket ship position
            if self.active:
                self.y -= 12 * self.active
                if self.y < 30:
                    self.active = False
                    self.reinit(x)
            else:
                self.reinit(x)
            
            
        else:
            self.reinit(x)
        
        
        
    def reinit(self, x):
        self.x = x
        self.y = self.inActiveY
    
    
    def reduceDivingArray(self, galaxians, number):
        leaderNumber = 33
        if number < 27:
            leaderNumber = 17
        
        for f in range(len(galaxians)):
            if galaxians[f].number == leaderNumber:
                galaxians[f].reduceDivingArray(number)
                return
        
        
        
        
        
        
        

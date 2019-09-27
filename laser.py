from player import Player
from states import States

class Laser(Player):
    def __init__(self, x, y, sprite):
        Player.__init__(self, x, y - 7, sprite)
        self.inActiveY = y - 7
        self.active = False

     
    def move(self, rocketShipX, galaxians):
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
                        if galaxians[f].state == state.FORMATION_DIVING and galaxians[f].colour == "red":
                            self.adjustTeam(galaxians, galaxians[f])
                        self.active = False
                        # no BREAK - let it run through array of galaxians,
                        # because a laser can destroy multiple galaxians
            
            # only move if active other wise reinitialise back to rocket ship position
            if self.active:
                self.y -= 12
                if self.y < 30:
                    self.active = False
                    self.reinit(rocketShipX)
            else:
                self.reinit(rocketShipX)
        else:
            self.reinit(rocketShipX)
        
        
        
    def reinit(self, x):
        self.x = x
        self.y = self.inActiveY
    
    """
    if the laser hits a red galaxian and it's state is FORMATION_DIVING then the leader needs to adjust it's
    diving team to reflect 1 less in team and increases bonus score if the leader gets destroyed as well"""
    def adjustTeam(self, galaxians, redGalaxian):        
        for f in range(len(galaxians)):
            if galaxians[f].number == redGalaxian.leadNumber:
                galaxians[f].reduceDivingArray(redGalaxian.number)
                return

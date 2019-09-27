import glob, pygame, os, math
from explosion import Explosion
from functions import matchCentre, vector, wrap360, pointDirection, pointDistance
from states import States
from random import random
from bomb import Bomb
from floatingscore import FloatingScore



class Galaxian():
    def __init__(self, sprite, FPS, x, y, startFrame, galaxianNumber, width, height):
        #self.number = num
        self.x = x
        self.y = y
        
        # after a dive they need to get back into formation
        self.formationX = x
        self.formationY = y
        
        self.colour = sprite
        self.leadNumber = -1
        self.escaped = False
        
        self.number = galaxianNumber
        self.offScreenX = 50
        
        self.screenWidth = width
        self.screenHeight = height
        
        self.FPS = FPS
        
        # basic setup for all galaxians. additional settings is done below with the if/elif statements
        self.score = 30
        self.bombTotal = 3
        # for yellow galaxian and formation diving only 
        self.bonusScore = [200, 300, 800]
        #self.bonusScoreIndex = 0
        
        self.dxRate = 0.05
        # the player can move at speed 3.0. additional rates added below
        self.dxMax = 2.25
        
        # extra settings for other galaxians
        if sprite == "magenta":
            self.score += 10
            self.bombTotal += 1
            self.dxMax += 3.0
        elif sprite == "red":
            self.score += 20
            self.bombTotal += 3
            self.dxMax += 1.0
        elif sprite == "yellow":
            startFrame = 0
            self.score += 30
            self.bombTotal += 3
            # let leader accelerate twice as fast as the others
            self.dxRate += 0.05
            self.dxMax += 1.25
            # special limits for formation diving of yellow galaxian only
            self.dxRateCap = 0.05
            self.dxMaxCap = 0.25
            
        
        # initialise with correct bomb load
        self.bombLoad = self.bombTotal
        
        # sideways movement
        self.dx = 0.0
        
        # array of formation diving team
        self.divingTeam = []
        self.divingTeamStartSize = 0
        # number for RED galaxians to know who is in control
        self.divingLeaderNo = 0
        
        # decided to load the array of sprites in total once instead of loading every time a new frame is needed  
        self.spriteArray = []
        spriteIndex = glob.glob(os.path.join("images", sprite + "_gal_*.png"))
        for f in range(len(spriteIndex)):
            self.spriteArray.append(pygame.image.load(spriteIndex[f]).convert_alpha())
        
        
        self.sprite = self.spriteArray[startFrame]
        self.hitArea = self.sprite.get_rect()
        
        self.direction = 90.0
        self.speed = 0.0
        
        # do NOT load sound with every galaxian in constructor!!!!
        # there is a undesirable pause when loading an array of galaxians
        # instead load sound through function and assign it to variable below
        self.soundDiving = None
        
        # used to time frame updates
        self.spriteCounter = 0
        self.spriteStep = FPS / 3
        self.spriteFrame = startFrame
        
        self.turn = 0.0
        
        state = States()
        self.state = state.FORMATION
        
        self.destroyed = False
    
    """
    - this will constantly try and set the galaxians x position to the same as the player"""
    def targetPlayer(self, player, dxRateCap = 0.0, dxMaxCap = 0.0):
        drift = player.x - self.x
        # test to see whether +/- the side ways acceleration from the current sideways speed
        if drift != 0:
            drift = drift / math.fabs(drift)
            self.dx += (self.dxRate - dxRateCap) * drift
        
        # limit the sideways speed to the galaxians max speed
        if self.dx > self.dxMax - dxMaxCap:
            self.dx = self.dxMax - dxMaxCap
        elif self.dx < -(self.dxMax - dxMaxCap):
            self.dx = - (self.dxMax - dxMaxCap)
        
    
    """
    - this is called when a YELLOW galaxian is randomly picked from main.py to attack the player
    - it checks for any RED galaxians that are in formation under the YELLOW one and will take 2 if available"""
    def getTeam(self, galaxianAliveArray, galaxians):
        state = States()
        checkNumbers = []
        
        # if any of these Red galaxians add them to array to check for formation dive
        for f in range(6, 8, 1):
            if galaxianAliveArray[self.number - f]:
                checkNumbers.append(self.number -f)
            
        if galaxianAliveArray[self.number - 1]:
            checkNumbers.append(self.number - 1)
            
        if galaxianAliveArray[self.number + 5]:
            checkNumbers.append(self.number + 5)
        

        for f in range(len(checkNumbers)):
            for gal in range(len(galaxians)):
                if galaxians[gal].number == checkNumbers[f] and galaxians[gal].state == state.FORMATION and galaxians[gal].colour == "red":
                    self.divingTeam.append(galaxians[gal])
                    # when red galaxian gets destroyed in formation this number will identify the group leader
                    galaxians[gal].leadNumber = self.number
                    galaxians[gal].state = state.FORMATION_DIVING
                    self.divingTeamStartSize += 1
                    # team full so break out of loop
                    if len(self.divingTeam) > 1:
                        return
                    break
                    
    
    
    """
    - this is called every frame while a YELLOW galaxian is in a state of FORMATION_DIVING 
    - this will move the RED galaxians that are in a formation dive
    - most of the time it will reposition them on the screen and then at the end it will
    - free them from the formation dive and set their state to landing"""
    def updateDivingTeam(self, dx, dy, landing = False):
        state = States()
        for f in range(len(self.divingTeam)):
            if not landing:
                self.divingTeam[f].x += dx
                self.divingTeam[f].y += dy
                self.divingTeam[f].direction = self.direction
            else:
                self.divingTeam[f].changeState(state.LANDING)
                
        
    
    
    
    """
    - when the galaxian is changing its state this will initialise the new state"""
    def changeState(self, stateChange):
        state = States()
        
        if stateChange == state.FORMATION:
            self.turn = 0.0
            self.speed = 0.0
            self.direction = 90
            self.x = self.formationX
            self.y = self.formationY
            self.state = stateChange
            return
        
        if stateChange == state.LAUNCHING:
            self.speed = 2.0
            self.turn = 3.5 * ((self.x - self.screenWidth / 2) / math.fabs(self.x - self.screenWidth / 2))
            self.state = stateChange
            return
        
        if stateChange == state.DIVING:
            self.turn = 0.0
            self.playDivingSound()
            self.direction = wrap360(self.direction)
            self.downSpeed = random() + 3
            
            if len(self.divingTeam) > 0:
                self.state = state.FORMATION_DIVING
            else:
                self.state = stateChange
            
            return
        
        if stateChange == state.LANDING:
            self.speed = 3.0
            self.bombLoad = self.bombTotal
            self.divingTeamStartSize = 0
            self.leadNumber = -1
            self.y = -20
            self.dx = 0.0
            self.state = stateChange
            return

    """
    - this destroys the galaxian a creates an explosion to show this. 
    - if the galaxian collided with the player then it will also create an explosion that matches the player sprite. 
    - this will add the appropriate score to the players score"""
    def killSelf(self, explosions, player, explodePlayer, floatingScores):
        state = States()
        explosions.append(Explosion(self.x, self.y, self.FPS, "gal"))
        
        # set true if galaxian has collided with the player
        if explodePlayer:
            explosions.append(Explosion(player.x, player.y, self.FPS, "player"))
        
        if self.soundDiving != None and len(self.divingTeam) == 0:
            # it might not be playing, but send stop command anyway
            self.soundDiving.stop()
        
        # update status to be dropped from the array of galaxians in main.py
        self.destroyed = True
        
        if self.state == state.DIVING:
            self.score *= 2
        elif self.state == state.FORMATION_DIVING:
            if self.colour == "yellow":
                # free up the team to dive individually - if any are left
                for f in range(len(self.divingTeam)):
                    self.divingTeam[f].state = state.DIVING
                    self.divingTeam[f].downSpeed = self.downSpeed
                    self.divingTeam[f].dx = self.dx
                
                scoreX = self.x
                if scoreX < 0:
                    scoreX = 0
                elif scoreX + 30 > self.screenWidth:
                    scoreX = self.screenWidth - 30
                
                self.score = self.bonusScore[self.divingTeamStartSize - len(self.divingTeam)]
                floatingScores.append(FloatingScore(scoreX, self.y, self.score, self.FPS))
            else:
                self.score *= 2
        elif self.state == state.LAUNCHING and len(self.divingTeam) > 0:
            for f in range(len(self.divingTeam)):
                self.divingTeam[f].state = state.LAUNCHING
                self.divingTeam[f].direction = self.direction
                self.divingTeam[f].turn = self.turn
                self.divingTeam[f].speed = 2.0
        
        player.score += self.score
    
    
    def reduceDivingArray(self, number):
        for f in range(len(self.divingTeam)):
            if self.divingTeam[f].number == number:
                self.divingTeam.pop(f)
                return
    
    """
    all galaxians carry out these instructions
    - drop bombs
    - point towards the player
    - limit their rotation to look downwards even when they pass under the player"""
    def commonMove(self, explosions, player, bombs):   
        if self.y > 270 and random() * 30 < 1 and self.bombLoad > 0:
            bombs.append(Bomb(self.x, self.y, self.dx, self.downSpeed, self.FPS))
            self.bombLoad -= 1
            
        self.direction = wrap360(pointDirection(self.x, self.y, player.x, player.y))
        
        if self.direction < 220 and self.direction > 90:
            self.direction = 220
        elif self.direction > 320 or self.direction <= 90:
            self.direction = 320
        
        
    def collideWithPlayer(self, explosions, player, floatingScores):
        if self.y > 610 and self.hitArea.colliderect(player.hitArea) and not self.destroyed and player.alive:
            x_offset = self.hitArea[0] - player.hitArea[0]
            y_offset = self.hitArea[1] - player.hitArea[1]
            if player.mask.overlap(self.getMask(), (x_offset, y_offset)):
                player.alive = False
                self.killSelf(explosions, player, True, floatingScores)
    
    
    """
    - testing when it should be destroyed
    - drop bombs
    - move in 1 of its 5 states
    - tests for collision with player"""
    def move(self, explosions, formationMove, player, bombs, floatingScores, extraGalaxians):
        state = States()
        self.formationX += formationMove
        
        # galaxian gets set destroyed when a laser detects a collision with this galaxian
        # or below when the galaxian detects a collision with the player 
        if self.destroyed:
            self.killSelf(explosions, player, False, floatingScores)
            return

        if self.state == state.FORMATION:
            self.x = self.formationX
            self.y = self.formationY
            # set true to animate sprite
            self.animateSprite(True)
            """========================================================================================================="""
        elif self.state == state.LAUNCHING:
            # main will initialise this. 
            # continue sequence until direction = 270ish
            self.direction += self.turn
            (add_x, add_y) = vector(self.direction, self.speed)
            self.x += add_x
            self.y += add_y
            
            
            # if this is a leader and he has a team dive going on the move the team 
            self.updateDivingTeam(add_x, add_y)
            
            #set false to only keep beat when it gets back into formation
            self.animateSprite(False)
            
            if math.fabs(wrap360(self.direction) - 270) < 5:
                self.changeState(state.DIVING)
            """========================================================================================================="""
        elif self.state == state.DIVING:
            # update x using vector pushing?
            self.targetPlayer(player)
            self.y += self.downSpeed
            self.x += self.dx
            
            #set false to only keep beat when it gets back into formation
            self.animateSprite(False)
            
            # common to DIVING and FORMATION_DIVING
            self.commonMove(explosions, player, bombs)
            self.collideWithPlayer(explosions, player, floatingScores)
            # this will only apply to the magenta galaxians. these can have a lot more side ways speed
            # so possibly move too far off of the side of the screen
            resetX = (self.x < -self.offScreenX or self.x > self.screenWidth + self.offScreenX)
            
            if self.y > self.screenHeight + 20 or resetX:
                if self.colour == "yellow" and extraGalaxians < 2:
                    self.escaped = True
                    return
                if resetX:
                    self.x = self.screenWidth / 2
                self.changeState(state.LANDING)
            """========================================================================================================="""
        elif self.state == state.LANDING:
            #set false to only keep beat when it gets back into formation
            self.animateSprite(False)
            
            if pointDistance(self.x, self.y, self.formationX, self.formationY) < 25:
                # cannot use self.direction because it is used to rotate sprite.
                # create a new variable (bearing) to control the movement
                bearing = pointDirection(self.x, self.y, self.formationX, self.formationY)
                (add_x, add_y) = vector(bearing, self.speed)
                
                if self.direction < 270 and self.direction > 90:
                    self.direction -= 10
                elif self.direction > 270 and self.direction < 450:
                    self.direction += 10
            else:
                self.direction = pointDirection(self.x, self.y, self.formationX, self.formationY)
                (add_x, add_y) = vector(self.direction, self.speed)
                
            self.x += add_x
            self.y += add_y
            
            #print pointDistance(self.x, self.y, self.formationX, self.formationY), angle, self.direction
            if pointDistance(self.x, self.y, self.formationX, self.formationY) < 3:
                self.changeState(state.FORMATION)
            """========================================================================================================="""
        elif self.state == state.FORMATION_DIVING:
            if self.colour == "yellow":
                self.targetPlayer(player, self.dxRateCap, self.dxMaxCap)
                self.y += self.downSpeed
                self.x += self.dx
                
                self.commonMove(explosions, player, bombs)
                self.updateDivingTeam(self.dx, self.downSpeed)
                
                if self.y > self.screenHeight + 20:
                    self.changeState(state.LANDING)
                    self.updateDivingTeam(0.0, 0.0, True)
                    # clear the array
                    self.divingTeam = []
            
            self.collideWithPlayer(explosions, player, floatingScores)
            
            self.animateSprite(False)
        
    
    
    """
    - only create a mask when a rectangular collision has occurred. this improves FPS"""
    def getMask(self):
        return pygame.mask.from_surface(self.sprite)
        
        
    """
    - while the galaxian only animates while in formation, it needs to keep step once it rejoins the formation"""
    def animateSprite(self, animate):
        self.spriteCounter = (self.spriteCounter + 1) % self.spriteStep
        
        if self.spriteCounter == 0:
            self.spriteFrame = (self.spriteFrame + 1) % len(self.spriteArray)
        
        if animate:
            self.sprite = self.spriteArray[self.spriteFrame]
        
        else:
            self.sprite = self.spriteArray[0]
        
        self.sprite = pygame.transform.rotate(self.sprite, self.direction).convert_alpha()
        self.spriteCentre = matchCentre(self.spriteArray[0], self.sprite)
        
        self.hitArea = pygame.Rect(self.x + self.spriteCentre.x, self.y + self.spriteCentre.y, 
                                   self.spriteCentre.width, self.spriteCentre.height)
        
        
    """
    - the sound for diving will only be loaded once the galaxian starts to dive. this is why this function was added
    - it helps with performance"""
    def playDivingSound(self):
        if self.soundDiving == None:
            self.soundDiving = pygame.mixer.Sound(os.path.join("sounds", "ju87.ogg"))
            self.soundDiving.set_volume(0.35)
        
        self.soundDiving.play()
            
    
    """
    - draw the galaxian in the windhole"""
    def draw(self, window):
        window.blit(self.sprite, (self.x + self.spriteCentre[0], self.y + self.spriteCentre[1]))
        
        # ------------
        # TESTING ONLY
        #pygame.draw.rect(window, (0,255,100), (self.hitArea.x, self.hitArea.y, self.hitArea[2], self.hitArea[3]), 1)
        #pygame.draw.rect(window, (0,255,100), (self.x, self.y, 1, 1), 1)
        # ------------

import pygame,os
from laser import Laser
from player import Player
from functions import limits
from states import States


class RocketShip(Player):
    def __init__(self, FPS, x, y, sprite, spriteLaser):
        Player.__init__(self, x, y, sprite)
        
        self.soundLaser = pygame.mixer.Sound(os.path.join("sounds", "laser.ogg"))
        self.soundLaser.set_volume(0.5)
        
        self.leftCTRL_UP = False
        
        # the player can only have 1 laser active, so one 1 is every created. 
        self.laser = Laser(self.x, self.y - self.spriteCentre.height / 2, spriteLaser)
        
        self.score = 0
        # player will start game alive
        self.alive = True
        self.lives = 2
        
        # every time a screen is cleared this will be incremented. 
        # this effects how many galaxians can dive at once and the time delay between galaxians launching.
        self.level = 0
        
        # wait 4 seconds to reinitialise the player or decide the game is over
        self.waitTime = FPS * 4
        # this timer is only decremented once the player is NOT alive
        self.waitTimer = self.waitTime
        
        self.spriteLife = pygame.image.load(os.path.join("images", "rocketShipLife.png")).convert_alpha()
        self.spriteLifeRect = self.spriteLife.get_rect()
        
        
        
    def move(self, gal, screenWidth):
        # updates the sprite and hit rectangle
        Player.move(self)
        
        if self.alive:
            userInput = pygame.key.get_pressed()
            if userInput[pygame.K_LEFT] and self.alive:
                self.x -= 3
            if userInput[pygame.K_RIGHT] and self.alive:
                self.x += 3
            if userInput[pygame.K_LCTRL] and self.leftCTRL_UP and not self.laser.active:
                self.laser.active = True
                self.soundLaser.play()
            
            # stop the player moving off the screen
            self.x = limits(self.x, 0, screenWidth, self.spriteCentre.width / 2)
            
            # prevents auto fire
            self.leftCTRL_UP = not userInput[pygame.K_LCTRL]
            
            # update the laser, regardless if it is active or not
            self.laser.move(self.x, gal)
            
            # game is not over, return false
            return False
        
        else:
            self.sprite = self.spriteBlank
            
            if self.laser.active:
                self.laser.move(self.x, gal)
            else:
                # just keep it out of sight for now
                self.laser.sprite = self.laser.spriteBlank
            
            state = States()
            # wait until all galaxians are back in formation before setting the player back up
            for f in range(len(gal)):
                if not gal[f].state == state.FORMATION:
                    # the players lives might be < 0, but return false until all galaxians are back in formation
                    return False
            
            
            if self.waitTimer > 0:
                self.waitTimer -= 1
                
            
            if self.waitTimer == 0:
                self.lives -= 1
                if self.lives >= 0:
                    self.alive = True
                    self.x = screenWidth / 2
                    self.laser.x = self.x
                    self.waitTimer = self.waitTime
                    self.sprite = self.spriteStart
                    self.laser.sprite = self.laser.spriteStart
                    # player still has lives
                    return False
                else:
                    # game over now!
                    return True
                
    

    def draw(self, window, screenHeight):
        Player.draw(self, window)
        self.laser.draw(window)
        
        for f in range(self.lives):
            window.blit(self.spriteLife, (10 + f * (self.spriteLifeRect.width + 5), screenHeight - self.spriteLifeRect.height))
            



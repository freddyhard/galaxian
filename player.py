import pygame, os
from functions import matchCentre


#    ------------------------------------------------------------------------
#                      ABSTRACT SUPER CLASS OF ROCKETSHIP & LASER
#    ------------------------------------------------------------------------
class Player():
    def __init__(self, x, y, sprite):
        self.x = x
        self.y = y
        
        
        self.spriteBlank = pygame.image.load(os.path.join("images", "blank.png")).convert_alpha()
        self.spriteStart = pygame.image.load(os.path.join("images", sprite)).convert_alpha()
        
        self.sprite = self.spriteStart
        
        self.spriteCentre = matchCentre(self.sprite, self.sprite)
        self.hitArea = pygame.Rect(self.x + self.spriteCentre.x, self.y + self.spriteCentre.y, 
                                   self.spriteCentre.width, self.spriteCentre.height)
        
        
        self.mask = pygame.mask.from_surface(self.sprite)
        
    
    
    def move(self):
        self.spriteCentre = matchCentre(self.sprite, self.sprite)
        self.hitArea = pygame.Rect(self.x + self.spriteCentre.x, self.y + self.spriteCentre.y, 
                                   self.spriteCentre.width, self.spriteCentre.height)
        
        
        
        
        
        
    def draw(self, window):
        window.blit(self.sprite, (self.x + self.spriteCentre[0], self.y + self.spriteCentre[1]))

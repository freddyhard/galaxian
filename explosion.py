import pygame, os, glob
from functions import matchCentre
from random import randint

class Explosion():
    def __init__(self, x, y, FPS, sprite):
        
        self.x = x
        self.y = y
        
        self.spriteIndex = glob.glob(os.path.join("images", "explosion_" + sprite + "_??.png"))
        self.sprite = pygame.image.load(self.spriteIndex[0]).convert_alpha()
        
        self.spriteCentre = matchCentre(self.sprite, self.sprite) 
        
        self.changeFrame = (FPS / 3) / len(self.spriteIndex)
        self.timer = self.changeFrame * len(self.spriteIndex)
        
        self.frame = 0
        self.destroyed = False
        
        explosion = pygame.mixer.Sound(os.path.join("sounds", "crash" + str(randint(0, 1)) + ".ogg"))
        explosion.play()
        
        
        
    def move(self):
        self.timer -= 1
        
        if self.timer > 0:
            if self.timer % self.changeFrame == 0:
                self.frame += 1
                self.sprite = pygame.image.load(self.spriteIndex[self.frame]).convert_alpha()
        else:
            self.destroyed = True
    
    
    
    def draw(self, window):
        window.blit(self.sprite, (self.x + self.spriteCentre[0], self.y + self.spriteCentre[1]))
        
        

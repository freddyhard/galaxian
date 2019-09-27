import pygame
from random import randint

class Star():
    def __init__(self, FPS, screenWidth, screenHeight):
        colours = ((205,0,0), (0,205,0), (0,0,205), (200,0,180), (0,205,185))
        
        self.sprite = pygame.Surface((3, 3))
        self.sprite.fill(colours[randint(0, len(colours) - 1)])
        
        self.timer = FPS / 2
        self.counter = randint(0, self.timer)
        
        self.x = randint(0, screenWidth - 3)
        self.y = 0.0
        self.offScreen = screenHeight
        self.destroyed = False
    
    
    def move(self):
        self.y += 1.5
        self.counter = (self.counter + 1) % self.timer
        
        self.destroyed = (self.y > self.offScreen)
    
    
    def draw(self, window):
        if self.counter > self.timer / 2:
            window.blit(self.sprite, (self.x, self.y))
        

        
        
        
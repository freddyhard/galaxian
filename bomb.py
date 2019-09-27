import pygame, os
from explosion import Explosion
from functions import matchCentre

class Bomb():
    def __init__(self, x, y, dx, dy, FPS):
        self.x = x
        self.y = y
        
        self.FPS = FPS
        
        self.sprite = pygame.image.load(os.path.join("images", "bomb.png")).convert_alpha()
        self.spriteCentre = matchCentre(self.sprite, self.sprite)
        self.hitArea = pygame.Rect(self.x + self.spriteCentre.x, self.y + self.spriteCentre.y, 
                                   self.spriteCentre.width, self.spriteCentre.height)
        
        self.mask = pygame.mask.from_surface(self.sprite)
        
        self.add_x = dx * 0.35
        self.add_y = dy + 1.0
        
        self.destroyed = False
        
        
    def move(self, player, explosions, screenHeight):
        self.x += self.add_x
        self.y += self.add_y
        
        if self.y > screenHeight:
            self.destroyed = True
            return
        
        self.hitArea = pygame.Rect(self.x + self.spriteCentre.x, self.y + self.spriteCentre.y, 
                                   self.spriteCentre.width, self.spriteCentre.height)
        if player.alive and self.y > 625:
            if self.hitArea.colliderect(player.hitArea):
                x_offset = self.hitArea[0] - player.hitArea[0]
                y_offset = self.hitArea[1] - player.hitArea[1]
                if player.mask.overlap(self.mask, (x_offset, y_offset)):
                    player.alive = False
                    self.destroyed = True
                    explosions.append(Explosion(player.x, player.y, self.FPS, "player"))


    def draw(self, window):
        window.blit(self.sprite, (self.x + self.spriteCentre[0], self.y + self.spriteCentre[1]))
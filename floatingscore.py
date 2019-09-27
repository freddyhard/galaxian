

class FloatingScore():
    def __init__(self, x, y, score, FPS):
        self.x = x
        self.y = y
        self.score = str(score)
        self.destroyed = False
        self.timer = FPS * 1.5
        self.colourChange = 0.0
        self.colourChangeRate = 255 / (FPS * 1.5)
        
        
    def move(self):
        self.timer -= 1
        
        self.y -= 0.5
        self.colourChange += self.colourChangeRate
        
        if self.timer < 0:
            self.destroyed = True
    
    
    
    def draw(self, font, window):
        floatingScoreTxt = font.render(self.score, 1, (255,self.colourChange,self.colourChange))
        window.blit(floatingScoreTxt, (self.x, self.y))
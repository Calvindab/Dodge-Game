import pygame

class finishLineBlock():

    def __init__(self, screenWidth, screenHeight, width, height, color):
        self.width = width
        self.height = height
        self.color = color
        self.x = screenWidth - self.width  
        self.y = (screenHeight // 2) - (self.height // 2)

    def updatePos(self, screenWidth, screenHeight):
        self.x = screenWidth - self.width  
        self.y = (screenHeight // 2) - (self.height // 2)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))

    def getRect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    

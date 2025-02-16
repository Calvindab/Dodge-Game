import pygame

class HealerBlock():
    activeHealers = []

    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))

    def getRect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    



import pygame

class Bullet():
    playerBulletCooldown = 0
    obstacleBulletCooldown = 0

    firedBullets = []

    def __init__(self, x, y, dx, dy, width, height, color, owner):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.width = width
        self.height = height
        self.color = color
        self.owner = owner

    def move(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))

    def hitBoundary(self, screenWidth, screenHeight):
        if self.x <= 0 or self.x + self.width > screenWidth or self.y <= 0 or self.y + self.height > screenHeight:
            return True
        
        return False
    
    def bounce(self):
        self.dx *= -1
        self.dy *= -1

    def getRect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

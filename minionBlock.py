import pygame
import math
from variablesConst import colorRGB

class MinionBlock():

    def __init__(self, boss, angleOffset, orbitDistance, level):
        self.boss = boss

        self.x = None
        self.y = None

        self.width = 40
        self.height = 40

        self.health = min(level, 22)

        # Orbit mechanism
        self.orbitAngle = angleOffset # Angle of orbit relative from the boss
        self.orbitDistance = orbitDistance # Orbit distance from the boss
        self.speed = 1 # Orbit speed

        # Initial position
        self.updatePosition()

    def move(self):
        # Minion move around the boss
        self.orbitAngle += self.speed # Rotate around the boss
        self.updatePosition()

    def minionDied(self):
        if self.health <= 0:
            return True
        return False

    def updatePosition(self):
        boss_centerX = (self.boss.x + self.boss.width // 2) - 25
        boss_centerY = (self.boss.y + self.boss.height // 2) - 25

        # Update minion position based on orbit angle
        self.x = boss_centerX + math.cos(math.radians(self.orbitAngle)) * self.orbitDistance
        self.y = boss_centerY + math.sin(math.radians(self.orbitAngle)) * self.orbitDistance

    def draw(self, surface):
        pygame.draw.rect(surface, colorRGB['dark orange'], (self.x, self.y, self.width, self.height))

        font = pygame.font.Font(None, 28)
        healthText = font.render(str(self.health), True, colorRGB['white'])

        textX = self.x + (self.width // 2) - (healthText.get_width() // 2)
        textY = self.y + (self.height // 2) - (healthText.get_height() // 2)

        surface.blit(healthText, (textX, textY))

    def getRect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

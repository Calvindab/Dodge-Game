import pygame
from variablesConst import colorRGB

# Explanation for angle = (360 / (len(self.activeMinions) + 1)) * len(self.activeMinions) cuz this is genius
# (360 / (len(self.activeMinions) + 1)) is dividing 360 degree (Circle) by number of minions (So it's evenly spread)
# * len(self.activeMinions) is essentially assigning each position of the minion with its orbit angle

"""
for i, minion in enumerate(self.activeMinions):
    minion.orbitAngle = (360 / len(self.activeMinions)) * i
"""
# Does the same thing, but here it's actually assigning the angle and passing it to minion class, genius


class BossBlock():

    def __init__(self, screenWidth, screenHeight, finishBlock, minionBlock, color, level):

        self.width = 250
        self.height = 250
        self.color = color

        self.x = finishBlock.x - self.width - 200
        self.y = (screenHeight // 2) - (self.height // 2)

        self.level = level
        self.health = min(20 + (level), 120) # Max 120 health

        # Shooting mechanism
        self.fireRate = max(2000 - (level * 50), 800) # Fastest bullet firerate at 0.8 sec
        self.nextShotTime = pygame.time.get_ticks() + self.fireRate

        # Minion
        self.minionSpawnRate = max(10000 - (level * 200), 4000) # Fastest spawn rate at 4 sec
        self.nextMinionSpawn = pygame.time.get_ticks() + self.minionSpawnRate
        self.minionSpawn = min(5 + (level // 5), 20) # Max 10 minions per spawn
        self.activeMinions = []
        self.orbitDistance = 250

        # Blitzkrieg formation
        self.blitzFormationActive = False

        # Spawn minion at start first
        self.spawnMinions(minionBlock)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))

        font = pygame.font.Font(None, 28)
        healthText = font.render(str(self.health), True, colorRGB['white'])

        textX = self.x + (self.width // 2) - (healthText.get_width() // 2)
        textY = self.y + (self.height // 2) - (healthText.get_height() // 2)

        surface.blit(healthText, (textX, textY))

    def spawnMinions(self, minionBlock):
        # Spawn in evenly spaced circle
        self.activeMinions.clear()

        for i in range(self.minionSpawn):
            angle = (360 / self.minionSpawn) * i
            newMinion = minionBlock(self, angle, self.orbitDistance, level=self.level)
            self.activeMinions.append(newMinion)

    def updateMinionFormation(self):
        # Recalculate position if minion die
        if len(self.activeMinions) == 0: # All dead - skip function
            return

        for i, minion in enumerate(self.activeMinions):
            minion.orbitAngle = (360 / len(self.activeMinions)) * i

    def spawnMinion(self, minionBlock, level):
        currentTime = pygame.time.get_ticks()

        if currentTime >= self.nextMinionSpawn:
            if len(self.activeMinions) < self.minionSpawn: # If less than the max minion spawn
                newMinion = minionBlock(self, 0, self.orbitDistance, level)
                self.activeMinions.append(newMinion)

                self.reorderMinions() # Recalculate formation

            # Spawn rate based on boss health
            healthFactor = max(0.5, self.health / 300)
            self.nextMinionSpawn = currentTime + int(self.minionSpawnRate * healthFactor)

    def reorderMinions(self):

        minionCount = len(self.activeMinions)

        if minionCount == 0:
            return

        for i, minion in enumerate(self.activeMinions):
            minion.orbitAngle = (360 / minionCount) * i # Evenly spaced minions

    def bossDied(self):
        if self.health <= 0:
            return True
        return False


    def getRect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


    




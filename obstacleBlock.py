import pygame
import random
from variablesConst import colorRGB
from bulletClass import Bullet
from utils import validateObstacleSpawn

class BlockObstacle():
    obstacleList = []
    bulletSpeedMultiplier = 1
    maxSpeed = 24
    maxBulletSpeed = 26

    def __init__(self, screenWidth, screenHeight, width, height, color, dx, dy, splitCount=0):
        self.width = width
        self.height = height
        self.color = color

        self.dx = dx
        self.dy = dy

        # Used for boss fight restoration when restoring the size
        self.originalWidth = width
        self.originalHeight = height

        self.dx_beforeBossFight = None
        self.dy_beforeBossFight = None

        self.x_ratio = random.uniform(0.05, 0.75)
        self.y_ratio = random.uniform(0.05, 0.75)

        self.x = int(screenWidth * self.x_ratio)
        self.y = int(screenHeight * self.y_ratio)
        self.y = min(self.y, screenHeight - self.height - 10)

        self.health = 5

        self.splitCount = splitCount
        self.nextShotTime = pygame.time.get_ticks() + random.randint(1000, 5000)

    def updatePos(self, screenWidth, screenHeight, newScreenWidth, newScreenHeight):
        self.x = int(screenWidth * self.x_ratio)
        self.y = int(screenHeight * self.y_ratio)

        # Adjust speed if screen size change
        if newScreenWidth != screenWidth or newScreenHeight != screenHeight:
            self.dx *= newScreenWidth / screenWidth
            self.dy *= newScreenHeight / screenHeight

    def move(self):
        self.dx = max(-self.maxSpeed, min(self.dx, self.maxSpeed))
        self.dy = max(-self.maxSpeed, min(self.dy, self.maxSpeed))

        self.x += self.dx
        self.y += self.dy

    def checkBoundary(self, screenWidth, screenHeight):
        # Reverse pos to make bouncing effect
        if self.x <= 0 or self.x + self.width > screenWidth:
            self.dx *= -1
        if self.y <= 0 or self.y + self.height > screenHeight:
            self.dy *= -1

    def checkBlockCollision(self):
        for other in BlockObstacle.obstacleList:
            if self == other:
                continue

            if self.getRect().colliderect(other.getRect()):
                self.dx *= -1
                self.dy *= -1

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))

        font = pygame.font.Font(None, 28)
        healthText = font.render(str(self.health), True, colorRGB['black'])

        textX = self.x + (self.width // 2) - (healthText.get_width() // 2)
        textY = self.y + (self.height // 2) - (healthText.get_height() // 2)

        surface.blit(healthText, (textX, textY))

    def shoot(self, bulletDX, bulletDY, level):
        currentTime = pygame.time.get_ticks()

        if currentTime >= self.nextShotTime:
            bulletDX *= BlockObstacle.bulletSpeedMultiplier
            bulletDY *= BlockObstacle.bulletSpeedMultiplier

            directions_and_width_height = [(-bulletDX, 0, 50, 10), (bulletDX, 0, 50, 10), (0, -bulletDY, 10, 50), (0, bulletDY, 10, 50)]

            for bulletDX, bulletDY, bulletWidth, bulletHeight in directions_and_width_height:
                new_bullet = Bullet(self.x + self.width // 2, self.y + self.height // 2, bulletDX, bulletDY, bulletWidth, bulletHeight, colorRGB['orange'], "obstacle")
                Bullet.firedBullets.append(new_bullet)

            fireRate = max(1500, 5000 - (level * 100))  # Lowest firerate is never below 1.5 sec
            self.nextShotTime = currentTime + fireRate

    def obstacleDied(self, player, finishBlock, AllyBlock, screenWidth, screenHeight, level):
        if self.health <= 0 and level >= 5 and self.splitCount < 3:

            # How many children they split into
            if level >= 30:
                numChildren = random.randint(2, 6)
            elif level >= 20:
                numChildren = random.randint(1, 5)
            elif level >= 10:
                numChildren = random.randint(0, 4)
            else:
                numChildren = random.randint(0, 3) # Below level 10

            for _ in range(numChildren):

                # Children size is randomly selected between 50% ~ 75% of the original size
                newWidth = int(self.width * random.uniform(0.5, 0.75))
                newHeight = int(self.height * random.uniform(0.5, 0.75))

                # If size too small (30 pxl) then don't generate
                if newWidth < 60 or newHeight < 60:
                    continue
                    
                # Children speed is reduced by 5% ~ 10% randomly selected
                newDX = int(self.dx * random.uniform(0.9, 0.95))
                newDY = int(self.dy * random.uniform(0.9, 0.95))

                # New health set to 3
                newHealth = min(3 + (level // 10), 12) # Max cannot exceed 12 health

                # Creating children obstacle
                newObstacle = BlockObstacle(screenWidth, screenHeight, newWidth, newHeight, self.color, newDX, newDY, splitCount=self.splitCount + 1)
                newObstacle.health = newHealth
                validateObstacleSpawn(newObstacle, BlockObstacle, player, finishBlock, AllyBlock, screenWidth, screenHeight)
                BlockObstacle.obstacleList.append(newObstacle)

        return self.health <= 0 # Return true if obstacle dead
    
    @staticmethod
    def createBlitzkriegFormation(screenWidth, screenHeight):
        
        # requiredObstacleNum is the number of obstacles required to complete the diagonal part of the Blitzkrieg
        # The rest, we use while loop to generate blocks until it reaches the edge of the screen

        uniformWidth = 50
        uniformHeight = 50
        uniformHealth = 7
        uniformDX, uniformDY = 0, 0

        spacing_x = 20
        spacing_y = 20

        existingObstacles = BlockObstacle.obstacleList

        # Fixed num of obstsacles
        requiredObstacleNum = 10

        if len(existingObstacles) > requiredObstacleNum:
            existingObstacles = existingObstacles[:requiredObstacleNum]

        elif len(existingObstacles) < requiredObstacleNum:
            for _ in range(requiredObstacleNum - len(existingObstacles)):
                newObstacle = BlockObstacle(screenWidth, screenHeight, uniformWidth, uniformHeight, colorRGB['yellow'], uniformDX, uniformDY)
                existingObstacles.append(newObstacle)

        BlockObstacle.obstacleList = existingObstacles # Update global list

        # Spearhead position (Reference point)
        spearhead_x = screenWidth // 2 - 200
        spearhead_y = screenHeight // 2 - uniformHeight + 20

        # Freeze movement and resize
        for obstacle in existingObstacles:
            obstacle.width = uniformWidth
            obstacle.height = uniformHeight

            obstacle.dx_beforeBossFight = obstacle.dx
            obstacle.dy_beforeBossFight = obstacle.dy
            obstacle.dx = uniformDX
            obstacle.dy = uniformDY # Freeze movement

            obstacle.health = uniformHealth


        # Top right diagonal
        existingObstacles_TRDiagonal = existingObstacles[0:requiredObstacleNum // 2]

        prevX_TR = spearhead_x
        prevY_TR = spearhead_y

        for obstacle in existingObstacles_TRDiagonal:
            newX = prevX_TR + uniformWidth + spacing_x
            newY = prevY_TR - uniformHeight - spacing_y
            obstacle.x = newX
            obstacle.y = newY
            prevX_TR, prevY_TR = newX, newY

        # Bottom right diagonal
        existingObstacles_BRDiagonal = existingObstacles[requiredObstacleNum // 2:requiredObstacleNum]

        prevX_BR = spearhead_x
        prevY_BR = spearhead_y

        for obstacle in existingObstacles_BRDiagonal:
            newX = prevX_BR + uniformWidth + spacing_x
            newY = prevY_BR + uniformHeight + spacing_y
            obstacle.x = newX
            obstacle.y = newY
            prevX_BR, prevY_BR = newX, newY


        # Top right Blitzkrieg side
        existingObstacles_TRSide = []

        while prevX_TR + uniformWidth + spacing_x < screenWidth:

            newX = prevX_TR + uniformWidth + spacing_x
            newY = prevY_TR

            newObstacle = BlockObstacle(screenWidth, screenHeight, uniformWidth, uniformHeight, colorRGB['yellow'], uniformDX, uniformDY)
            newObstacle.health = uniformHealth
            newObstacle.x = newX
            newObstacle.y = newY

            existingObstacles_TRSide.append(newObstacle)

            prevX_TR = newX

        existingObstacles_TRSide.pop() # I had to add it cuz for some reason it keeps going off screen boundary

        # Bottom right Blitzkrieg side
        existingObstacles_BRSide = []

        while prevX_BR + uniformWidth + spacing_x < screenWidth:

            newX = prevX_BR + uniformWidth + spacing_x
            newY = prevY_BR

            newObstacle = BlockObstacle(screenWidth, screenHeight, uniformWidth, uniformHeight, colorRGB['yellow'], uniformDX, uniformDY)
            newObstacle.health = uniformHealth
            newObstacle.x = newX
            newObstacle.y = newY

            existingObstacles_BRSide.append(newObstacle)

            prevX_BR = newX

        existingObstacles_BRSide.pop()




        # BUILDING OUTER LAYER
        spearhead_x_outer = spearhead_x - uniformWidth - 20
        spearhead_y_outer = spearhead_y

        uniformDX_outer, uniformDY_outer = -1, 0


        # Outer layer Blitzkrieg diagonal (Top right)
        existingObstacles_TRSide_Outer = []

        prevX_TR_outer = spearhead_x_outer
        prevY_TR_outer = spearhead_y_outer

        while (prevX_TR_outer + uniformWidth + spacing_x < screenWidth) and (prevY_TR_outer + uniformHeight + spacing_y > 0):

            newX = prevX_TR_outer + uniformWidth + spacing_x
            newY = prevY_TR_outer - uniformHeight - spacing_y

            newObstacle_outer = BlockObstacle(screenWidth, screenHeight, uniformWidth, uniformHeight, colorRGB['yellow'], uniformDX_outer, uniformDY_outer)
            newObstacle_outer.health = uniformHealth
            newObstacle_outer.x = newX
            newObstacle_outer.y = newY

            existingObstacles_TRSide_Outer.append(newObstacle_outer)

            prevX_TR_outer = newX
            prevY_TR_outer = newY

        existingObstacles_TRSide_Outer.pop()
        existingObstacles_TRSide_Outer.pop() # Idk why I have to pop it again, but as a result of trail and error, I have to pop it again, don't ask me, ask pygame :(


        # Outer layer Blitzkrieg diagonal (Bottom right)
        existingObstacles_BRSide_Outer = []

        prevX_BR_outer = spearhead_x_outer
        prevY_BR_outer = spearhead_y_outer

        while (prevX_BR_outer + uniformWidth + spacing_x < screenWidth) and (prevY_BR_outer + uniformHeight + spacing_y < screenHeight):

            newX = prevX_BR_outer + uniformWidth + spacing_x
            newY = prevY_BR_outer + uniformHeight + spacing_y

            newObstacle_outer = BlockObstacle(screenWidth, screenHeight, uniformWidth, uniformHeight, colorRGB['yellow'], uniformDX_outer, uniformDY_outer)
            newObstacle_outer.health = uniformHealth
            newObstacle_outer.x = newX
            newObstacle_outer.y = newY

            existingObstacles_BRSide_Outer.append(newObstacle_outer)

            prevX_BR_outer = newX
            prevY_BR_outer = newY

        existingObstacles_BRSide_Outer.pop()



        # Assign last 2 block as center spearhead and center spearhead_outer
        newObstacle = BlockObstacle(screenWidth, screenHeight, uniformWidth, uniformHeight, colorRGB['yellow'], uniformDX, uniformDY)
        newObstacle.health = uniformHealth
        newObstacle.x = spearhead_x
        newObstacle.y = spearhead_y

        newObstacle_outer = BlockObstacle(screenWidth, screenHeight, uniformWidth, uniformHeight, colorRGB['yellow'], uniformDX_outer, uniformDY_outer)
        newObstacle_outer.health = uniformHealth
        newObstacle_outer.x = spearhead_x_outer
        newObstacle_outer.y = spearhead_y_outer

        existingObstacles = existingObstacles_TRDiagonal + existingObstacles_BRDiagonal + existingObstacles_TRSide + existingObstacles_BRSide + existingObstacles_TRSide_Outer + existingObstacles_BRSide_Outer
        existingObstacles.append(newObstacle)
        existingObstacles.append(newObstacle_outer)

        # Update global list
        BlockObstacle.obstacleList = existingObstacles
        

    def getRect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
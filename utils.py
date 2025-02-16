import random

def randomizeObstacle(newObstacle, screenWidth, screenHeight):
    newObstacle.x_ratio = random.uniform(0.05, 0.85)
    newObstacle.y_ratio = random.uniform(0.05, 0.75)

    newObstacle.width = random.randint(50, 150)
    newObstacle.height = random.randint(50, 150)

    newObstacle.x = int(screenWidth * newObstacle.x_ratio)
    newObstacle.y = int(screenHeight * newObstacle.y_ratio)

    newObstacle.x = max(50, min(newObstacle.x, screenWidth - newObstacle.width - 50))
    newObstacle.y = max(50, min(newObstacle.y, screenHeight - newObstacle.height - 50))
    newObstacle.y = min(newObstacle.y, screenHeight - newObstacle.height - 10)
def validateObstacleSpawn(newObstacle, BlockObstacle, player, finishBlock, AllyBlock, screenWidth, screenHeight):
    successfulBlockSpawn = False

    while not successfulBlockSpawn:
        successfulBlockSpawn = True # Assume success unless proven otherwise

        # Obstacles cannot spwawn on top of each other
        for obstacle in BlockObstacle.obstacleList:

            if newObstacle == obstacle:
                continue

            if newObstacle.getRect().colliderect(obstacle.getRect()):
                randomizeObstacle(newObstacle, screenWidth, screenHeight)
                successfulBlockSpawn = False

        # Obstacles cannot spawn on top of player
        if newObstacle.getRect().colliderect(player.getRect()):
            randomizeObstacle(newObstacle, screenWidth, screenHeight)
            successfulBlockSpawn = False

        # Obstacle cannot spawn on top of finish line
        if newObstacle.getRect().colliderect(finishBlock.getRect()):
            randomizeObstacle(newObstacle, screenWidth, screenHeight)
            successfulBlockSpawn = False

        # Obstacle cannot spawn on top of ally
        for ally in AllyBlock.aliveAlly:
            if newObstacle.getRect().colliderect(ally.getRect()):
                randomizeObstacle(newObstacle, screenWidth, screenHeight)
                successfulBlockSpawn = False



def randomizeHealer(newHealer, screenWidth, screenHeight):
    newHealer.x = random.randint(50, screenWidth - newHealer.width - 50)
    newHealer.y = random.randint(50, screenHeight - newHealer.height - 50)

    newHealer.width = random.randint(40, 60)
    newHealer.height = random.randint(40, 60)
def validateHealerSpawn(newHealer, player, finishBlock, screenWidth, screenHeight):
    successfulSpawn = False

    while not successfulSpawn:
        successfulSpawn = True # Assume success unless proven otherwise

        # Healer cannot spawn on top of player
        if newHealer.getRect().colliderect(player.getRect()):
            randomizeHealer(newHealer, screenWidth, screenHeight)
            successfulSpawn = False

        # Healer cannot spawn on top of finish line
        if newHealer.getRect().colliderect(finishBlock.getRect()):
            randomizeHealer(newHealer, screenWidth, screenHeight)
            successfulSpawn = False



def randomizeAlly(newAlly, screenWidth, screenHeight):
    newAlly.x = random.randint(50, screenWidth - newAlly.width - 50)
    newAlly.y = random.randint(50, screenHeight - newAlly.height - 50)
def validateAllySpawn(newAlly, AllyBlock, player, finishBlock, BlockObstacle, screenWidth, screenHeight):
    successfulSpawn = False

    while not successfulSpawn:
        successfulSpawn = True  # Assume success unless proven otherwise

        # Ally cannot spawn on top of player
        if newAlly.getRect().colliderect(player.getRect()):
            randomizeAlly(newAlly, screenWidth, screenHeight)
            successfulSpawn = False

        # Ally cannot spawn on top of the finish line
        if newAlly.getRect().colliderect(finishBlock.getRect()):
            randomizeAlly(newAlly, screenWidth, screenHeight)
            successfulSpawn = False

        # Ally cannot spawn on top of an obstacle
        for obstacle in BlockObstacle.obstacleList:
            if newAlly.getRect().colliderect(obstacle.getRect()):
                randomizeAlly(newAlly, screenWidth, screenHeight)
                successfulSpawn = False

        # Ally cannot spawn on top of another ally
        for ally in AllyBlock.aliveAlly:
            if newAlly.getRect().colliderect(ally.getRect()):
                randomizeAlly(newAlly, screenWidth, screenHeight)
                successfulSpawn = False


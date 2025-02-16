import pygame
import random
from obstacleBlock import BlockObstacle
from finishLineBlock import finishLineBlock
from characterClass import Character
from bulletClass import Bullet
from healBlock import HealerBlock
from variablesConst import colorRGB
from allyBlock import AllyBlock, drawAO_icon
from bossBlock import BossBlock
from minionBlock import MinionBlock
from utils import validateObstacleSpawn, validateHealerSpawn, validateAllySpawn

pygame.init()

# Initial setting
global screenWidth, screenHeight, level, blockSplitEnable, score, bossFightActive
screenWidth, screenHeight = pygame.display.Info().current_w, pygame.display.Info().current_h
mainScreen = pygame.display.set_mode((screenWidth, screenHeight), pygame.RESIZABLE)
fullScreen = False

clock = pygame.time.Clock()
level = 0
score = 0
nextHealerSpawnLevel = 0
nextAllySpawnScore = 0
bossFightActive = False

screenWidth, screenHeight = mainScreen.get_size()

def bossFightCleanUp_procedure():
    global bossFightActive, bossBlock

    # If boss fight already active
    if bossFightActive:
        return
    
    print("!!Boss fight cleanup procedure in effect!!")

    # Remove healer block
    HealerBlock.activeHealers.clear()

    # At least 3 allies exist
    while len(AllyBlock.aliveAlly) < 3:
        newAlly = AllyBlock(screenWidth, screenHeight, player, random.choice([-20, 20]), random.choice([-20, 20]), 80, 80, colorRGB['darker violet purple'], health=random.randint(5, 7))
        validateAllySpawn(newAlly, AllyBlock, player, finishBlock, BlockObstacle, screenWidth, screenHeight)
        AllyBlock.aliveAlly.append(newAlly)

    # Ally now has 30~50 health
    for ally in AllyBlock.aliveAlly:
        ally.originalHealth = ally.health
        ally.health = random.randint(30, 50)

    # Spawn boss
    bossBlock = BossBlock(screenWidth, screenHeight, finishBlock, MinionBlock, colorRGB['red'], level)

    # Create Blitzkrieg formation
    BlockObstacle.createBlitzkriegFormation(screenWidth, screenHeight)

    print(len(BlockObstacle.obstacleList))

    for obstacle in BlockObstacle.obstacleList:
        print(obstacle.health)
        print(obstacle.dx)
        print(obstacle.dy)
        print()

    print("Procedure complete!!")

    bossFightActive = True

def restoreGameAfterBossFight():
    global bossFightActive
    bossFightActive = False

    print("Boss defeated! Restoring game...")

    # Remove all minions
    bossBlock.activeMinions.clear()

    # Restore size
    obstaclesToRemove_restorationFunc = []

    for obstacle in BlockObstacle.obstacleList:

        # Remove artificial block made during the Blitzkrieg formation creation
        if obstacle.dy == 0: # Because all artificial made block have no verticle speed
            obstaclesToRemove_restorationFunc.append(obstacle)
            continue

        obstacle.width = obstacle.originalWidth
        obstacle.height = obstacle.originalHeight

        # Restore original speed
        if obstacle.dx_beforeBossFight is not None and obstacle.dy_beforeBossFight is not None:
            obstacle.dx = obstacle.dx_beforeBossFight
            obstacle.dy = obstacle.dy_beforeBossFight
            obstacle.dx_beforeBossFight = None # Reset for future fights
            obstacle.dy_beforeBossFight = None

    # Removing obstacle (If any)
    for obstacle in obstaclesToRemove_restorationFunc:
        if obstacle in BlockObstacle.obstacleList:
            BlockObstacle.obstacleList.remove(obstacle)

    
    # Restoring ally health
    for ally in AllyBlock.aliveAlly:
        if ally.originalHealth < ally.health and ally.originalHealth is not None:
            ally.health = ally.originalHealth
            ally.originalHealth = None

    print("Game restoration completed")




def reset_game():
    global level, player, score, nextHealerSpawnLevel, nextAllySpawnScore, bossFightActive

    bossFightActive = False

    level = 0
    score = 0
    nextHealerSpawnLevel = 0
    nextAllySpawnScore = 0

    player.health = 5
    player.x = 0
    player.y = 0
    player.hitTimer = 0

    Bullet.playerBulletCooldown = 0
    Bullet.obstacleBulletCooldown = 0

    BlockObstacle.bulletSpeedMultiplier = 1
    BlockObstacle.maxSpeed = 26
    BlockObstacle.maxBulletSpeed = 30

    AllyBlock.bulletSpeedMultiplier = 1
    AllyBlock.maxBulletSpeed = 15

    for obstacle in BlockObstacle.obstacleList:
        del obstacle
    for bullet in Bullet.firedBullets:
        del bullet
    for healer in HealerBlock.activeHealers:
        del healer
    for ally in AllyBlock.aliveAlly:
        del ally

    BlockObstacle.obstacleList.clear()
    Bullet.firedBullets.clear()
    HealerBlock.activeHealers.clear()
    AllyBlock.aliveAlly.clear()

    # Respawn new obstacles
    for _ in range(4):
        newObstacle = BlockObstacle(screenWidth, screenHeight, random.randint(100, 250), random.randint(100, 250), colorRGB['yellow'], random.choice([-4, 4]), random.choice([-4, 4]))
        validateObstacleSpawn(newObstacle, BlockObstacle, player, finishBlock, AllyBlock, screenWidth, screenHeight)
        BlockObstacle.obstacleList.append(newObstacle)

def displayEndScreen():
    screenWidth, screenHeight = pygame.display.Info().current_w, pygame.display.Info().current_h
    endScreen = pygame.display.set_mode((screenWidth, screenHeight), pygame.RESIZABLE)

    font_path = "minecraftFont.ttf"
    font = pygame.font.Font(font_path, 80)

    gameOverText = font.render("GAME OVER", True, colorRGB['softer green'])
    endScreen.blit(gameOverText, (screenWidth // 2 - gameOverText.get_width() // 2, screenHeight // 3))

    # Creating button
    restartText = "RESTART"
    quitText = "QUIT"

    restartTextSurface = font.render(restartText, True, colorRGB['black'])
    quitTextSurface = font.render(quitText, True, colorRGB['black'])

    button_padding = 40  # Add extra width for padding around text
    restartButtonWidth = restartTextSurface.get_width() + button_padding
    quitButtonWidth = quitTextSurface.get_width() + button_padding
    buttonHeight = 80

    # Create buttons with adjusted width
    restartButton = pygame.Rect(screenWidth // 2 - restartButtonWidth // 2, screenHeight // 2, restartButtonWidth, buttonHeight)
    quitButton = pygame.Rect(screenWidth // 2 - quitButtonWidth // 2, screenHeight // 2 + 120, quitButtonWidth, buttonHeight)

    waiting = True

    while waiting:

        endScreen.fill(colorRGB['darker red'])
        endScreen.blit(gameOverText, (screenWidth // 2 - gameOverText.get_width() // 2, screenHeight // 3))

        drawButton(endScreen, restartText, font, colorRGB['darker red'], restartButton, colorRGB['yellow'], 'softer blue')
        drawButton(endScreen, quitText, font, colorRGB['darker red'], quitButton, colorRGB['yellow'], 'softer pink')

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()

                if event.key == pygame.K_RETURN:
                    reset_game()
                    waiting = False
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
                if event.key == pygame.K_f and (keys[pygame.K_LMETA] or keys[pygame.K_RMETA] or keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]):  
                            fullscreen = False
                            if fullscreen:
                                endScreen = pygame.display.set_mode((screenWidth, screenHeight), pygame.FULLSCREEN)
                            else:
                                endScreen = pygame.display.set_mode((screenWidth, screenHeight), pygame.RESIZABLE)

            # Mouse click
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Left mouse click

                if restartButton.collidepoint(event.pos):
                    reset_game()
                    waiting = False

                if quitButton.collidepoint(event.pos):
                    pygame.quit()
                    exit()

def displayWinScreen():
    font = pygame.font.Font(None, 80)
    gameOverText = font.render("YOU WON!", True, colorRGB['blue'])

    mainScreen.fill(colorRGB['green'])
    mainScreen.blit(gameOverText, (450, 400))
    pygame.display.flip()

    pygame.time.delay(2000)
    pygame.quit()
    exit()

def drawButton(surface, text, font, color, rect, hoverColor, textColor):
    mousePos = pygame.mouse.get_pos()

    # Draw button - If mouse is hovering, button is in hover color, if not then it's in its original color
    pygame.draw.rect(surface, hoverColor if rect.collidepoint(mousePos) else color, rect)

    # Rendering the text on the button
    textSurface = font.render(text, True, colorRGB[textColor])
    surface.blit(textSurface, (rect.x + (rect.width - textSurface.get_width()) // 2, rect.y + (rect.height - textSurface.get_height()) // 2))

def displayMenu():
    global mainScreen, fullScreen

    pygame.font.init()
    font_path = "minecraftFont.ttf"
    font = pygame.font.Font(font_path, 80)

    mainScreen.fill(colorRGB['white'])

    titleText = font.render("DODGE - THE GAME", True, colorRGB['black'])
    mainScreen.blit(titleText, (screenWidth // 2 - titleText.get_width() // 2, screenHeight // 3))

    # Creating buttons
    buttonWidth, buttonHeight = 300, 80
    startButton = pygame.Rect(screenWidth // 2 - buttonWidth // 2, screenHeight // 2, buttonWidth, buttonHeight)
    exitButton = pygame.Rect(screenWidth // 2 - buttonWidth // 2, screenHeight // 2 + 120, buttonWidth, buttonHeight)

    pygame.display.flip()

    waiting = True
    while waiting:

        mainScreen.fill(colorRGB['white'])
        mainScreen.blit(titleText, (screenWidth // 2 - titleText.get_width() // 2, screenHeight // 3))

        # Draw buttons
        drawButton(mainScreen, "START", font, colorRGB['green'], startButton, colorRGB['yellow'], 'black')
        drawButton(mainScreen, "EXIT", font, colorRGB['red'], exitButton, colorRGB['yellow'], 'black')

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()

                if event.key == pygame.K_RETURN:
                    waiting = False
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
                if event.key == pygame.K_f and (keys[pygame.K_LMETA] or keys[pygame.K_RMETA] or keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]):  
                    fullscreen = False
                    if fullscreen:
                        mainScreen = pygame.display.set_mode((screenWidth, screenHeight), pygame.FULLSCREEN)
                    else:
                        mainScreen = pygame.display.set_mode((screenWidth, screenHeight), pygame.RESIZABLE)

            # Mouse click
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse click

                if startButton.collidepoint(event.pos):
                    waiting = False  # Start game

                if exitButton.collidepoint(event.pos):
                    pygame.quit()
                    exit()

# LEVEL UP FUNC
def levelUp():
    global level, nextHealerSpawnLevel, nextAllySpawnScore, bossFightActive

    # Level up
    level += 1
    print(f"LEVEL UP! Now at Level {level}")

    # Check if boss fight should start
    if level == 11 or (level > 11 and (level - 11) % random.randint(12, 22) == 0):
        bossFightCleanUp_procedure()
        return # Skip function

    # If boss fight avtive, function won't run
    if bossFightActive:
        return

    # Increase player ability
    Bullet.playerBulletCooldown = max(6, int(30 - (level * 4)))
    player.speed = min(player.speed * 1.05, 20) # Speed capped at 20
    player.acceleration = min(player.acceleration * 1.02, 2.5) # Increase acceleration by 2% (Capped at 2.5)
    player.friction = max(player.friction * 0.98, 0.75) # Reduce friction by 2% (Capped at 0.75)
    player.hitTimer = min(60, max(30, int(50 - (player.speed * 0.5))))

    # Spawn whenever level is 2-3 level
    if nextHealerSpawnLevel == 0:
        nextHealerSpawnLevel = random.randint(2, 3) # Set the first healer spawn interval

    maxPossibleHealers = max(0, 5 - player.health) # Limit healers to 5 max

    if maxPossibleHealers > 0:
        healersToSpawn = random.randint(1, maxPossibleHealers)

        healerWidth = random.randint(40, 60)
        healerHeight = random.randint(40, 60)

        if level >= nextHealerSpawnLevel:
            for _ in range(healersToSpawn):
                newHealer = HealerBlock(random.randint(50, screenWidth - 50), random.randint(50, screenHeight - 50), healerWidth, healerHeight, colorRGB['cyan'])
                validateHealerSpawn(newHealer, player, finishBlock, screenWidth, screenHeight)
                HealerBlock.activeHealers.append(newHealer)

            nextHealerSpawnLevel += random.randint(2, 3) # Setting next spawn
        
    # Increasing bullet speed
    BlockObstacle.bulletSpeedMultiplier = min(1 + (level * 0.05), BlockObstacle.maxBulletSpeed) # 5% faster per level
    AllyBlock.bulletSpeedMultiplier = min(1 + (level * 0.05), AllyBlock.maxBulletSpeed) # 5% faster per level

    # Increasing obstacle difficulty
    for obstacle in BlockObstacle.obstacleList:
        # Increasing speed by 10%
        obstacle.dx = max(-obstacle.maxSpeed, min(obstacle.dx * 1.1, obstacle.maxSpeed))
        obstacle.dy = max(-obstacle.maxSpeed, min(obstacle.dy * 1.1, obstacle.maxSpeed))

        # Increase helth
        obstacle.health += min(level // 2, 12) # New osbtacle health at most cannot exceed current + 12

    # Checking if there are 1 obstacle left
    if len(BlockObstacle.obstacleList) <= 1:
        for _ in range(3):
            newObstacle = BlockObstacle(screenWidth, screenHeight, random.randint(100, 250), random.randint(100, 250), colorRGB['yellow'], random.choice([-4, 4]), random.choice([-4, 4]))
            validateObstacleSpawn(newObstacle, BlockObstacle, player, finishBlock, AllyBlock, screenWidth, screenHeight)
            BlockObstacle.obstacleList.append(newObstacle)

    # Spawning ally whenever 3 - 5 obstacles killed (3 - 5 score), the next time the player level up, allies spawn
    if nextAllySpawnScore == 0:
        nextAllySpawnScore = random.randint(3, 5) # Set initial

    maxPossibleAlly = max(0, 4 - len(AllyBlock.aliveAlly)) # Limit max allies to 4
    if maxPossibleAlly > 0:
        allyToSpawn = random.randint(1, maxPossibleAlly)

        allyWidth = random.randint(80, 100)
        allyHeight = random.randint(80, 100)

        if score >= nextAllySpawnScore:
            for _ in range(allyToSpawn):
                newAlly = AllyBlock(screenWidth, screenHeight, player, random.choice([-20, 20]), random.choice([-20, 20]), allyWidth, allyHeight, colorRGB['darker violet purple'], health=random.randint(5, 7))
                validateAllySpawn(newAlly, AllyBlock, player, finishBlock, BlockObstacle, screenWidth, screenHeight)
                AllyBlock.aliveAlly.append(newAlly)

            nextAllySpawnScore += random.randint(3, 5) # Setting the next spawn
    
# IN GAME LOOP UTILITY FUNC
def bulletKeyPress(keys):
    global bulletDX, bulletDY, bulletStartPosX, bulletWidth, bulletHeight, player, Bullet

    # Checking bullets key pressed
    if keys[pygame.K_SPACE]:
        if keys[pygame.K_LEFT]:
            bulletDX, bulletDY = -22, 0
            bulletStartPosX = player.x                      # Left side
            bulletStartPosY = player.y + player.size // 2   # Vertical center

            bulletWidth = 50
            bulletHeight = 10
        elif keys[pygame.K_RIGHT]:
            bulletDX, bulletDY = 22, 0
            bulletStartPosX = player.x + player.size        # Right side
            bulletStartPosY = player.y + player.size // 2   # Vertical center

            bulletWidth = 50
            bulletHeight = 10
        elif keys[pygame.K_UP]:
            bulletDX, bulletDY = 0, -22
            bulletStartPosX = player.x + player.size // 2   # Horizontal center
            bulletStartPosY = player.y                      # Up

            bulletWidth = 10
            bulletHeight = 50
        elif keys[pygame.K_DOWN]:
            bulletDX, bulletDY = 0, 22
            bulletStartPosX = player.x + player.size // 2   # Horizontal center
            bulletStartPosY = player.y + player.size        # Down

            bulletWidth = 10
            bulletHeight = 50
        else:
            bulletDX, bulletDY = 22, 0 # Default shoot right
            bulletStartPosX = player.x + player.size        # Right side
            bulletStartPosY = player.y + player.size // 2   # Vertical center

            bulletWidth = 50
            bulletHeight = 10

        if Bullet.playerBulletCooldown == 0:
            newBullet = Bullet(bulletStartPosX, bulletStartPosY, bulletDX, bulletDY, bulletWidth, bulletHeight, colorRGB['purple'], owner='player')
            Bullet.firedBullets.append(newBullet)
            Bullet.playerBulletCooldown = max(6, int(30 - (level * 1.2)))

    if Bullet.playerBulletCooldown > 0:
        Bullet.playerBulletCooldown -= 1

def checkBulletMovement():
    global Bullet, BlockObstacle, AllyBlock, bossBlock, player, bulletsToRemove, obstaclesToRemove, allyToRemove, minionsToRemove, score, level, screenWidth, screenHeight, bossFightActive

    # Checking bullet movement
    bulletsToRemove = []
    obstaclesToRemove = []
    allyToRemove = []
    minionsToRemove = []

    for bullet in Bullet.firedBullets:
        # Checking whether the bullet hit boundary or not
        if bullet.x < 0 or bullet.x > screenWidth or bullet.y < 0 or bullet.y > screenHeight:
            bulletsToRemove.append(bullet)

        # Checking if bullet collided with obstacle
        for obstacle in BlockObstacle.obstacleList:

            # If bullet fired by player hit obstacle: Delete and decrement obstacle health
            if bullet.getRect().colliderect(obstacle.getRect()) and bullet.owner == 'player':
                bulletsToRemove.append(bullet)
                obstacle.health -= 1

                if obstacle.obstacleDied(player, finishBlock, AllyBlock, screenWidth, screenHeight, level):
                    obstaclesToRemove.append(obstacle)
                    score += 1

            # If bullet fired by ally hit obstacle: Delete and decrement obstacle health
            if bullet.getRect().colliderect(obstacle.getRect()) and bullet.owner == 'ally':
                bulletsToRemove.append(bullet)
                obstacle.health -= 1

                if obstacle.obstacleDied(player, finishBlock, AllyBlock, screenWidth, screenHeight, level):
                    obstaclesToRemove.append(obstacle)

        # Checking if bullet collided with minions (Note, DO NOT DEACTIVATE BOSSFIGHTACTIVE HERE, DEACTIVATE AT THE END OF LOOP)
        if bossFightActive:
            if bullet.getRect().colliderect(bossBlock.getRect()) and bullet.owner in ['player', 'ally']:
                bulletsToRemove.append(bullet)
                bossBlock.health -= 1

            for minion in bossBlock.activeMinions:
                if bullet.getRect().colliderect(minion.getRect()) and bullet.owner in ['player', 'ally']:  
                    bulletsToRemove.append(bullet)
                    minion.health -= 1

                    if minion.minionDied():
                        minionsToRemove.append(minion)

        # Checking if bullet collided with player
        # If bullet fired by obstacle and hit player: Delete and decrease player health
        if bullet.getRect().colliderect(player.getRect()) and bullet.owner == 'obstacle':
            bulletsToRemove.append(bullet)
            player.hitTimer = 50
            player.health -= 1

            print(f"Player got shot! Health = {player.health}")

        # If bullet fired by obstacle and hit ally: Delete and decrease ally health
        for ally in AllyBlock.aliveAlly:
            if bullet.getRect().colliderect(ally.getRect()) and bullet.owner == 'obstacle':
                bulletsToRemove.append(bullet)
                ally.health -= 1

                if ally.allyDied():
                    allyToRemove.append(ally)
    
    # Removing bullets (If any)
    for bullet in bulletsToRemove:
        if bullet in Bullet.firedBullets:
            Bullet.firedBullets.remove(bullet)

    # Removing obstacles (If any)
    for obstacle in obstaclesToRemove:
        if obstacle in BlockObstacle.obstacleList:
            BlockObstacle.obstacleList.remove(obstacle)

    # Removing ally (If any)
    for ally in allyToRemove:
        if ally in AllyBlock.aliveAlly:
            AllyBlock.aliveAlly.remove(ally)

    # Removing minions (If any)
    if bossFightActive:
        for minion in minionsToRemove:
            if minion in bossBlock.activeMinions:
                bossBlock.activeMinions.remove(minion)

def checkObstacleMovement():
    global BlockObstacle, player, finishBlock, AllyBlock, screenWidth, screenHeight, level, obstacleToRemove_uponImpact, score

    # Checking obstacle block movement
    obstacleToRemove_uponImpact = []

    for obstacle in BlockObstacle.obstacleList:
        # Let the block move and bounce
        obstacle.move()
        obstacle.checkBoundary(screenWidth, screenHeight)
        obstacle.checkBlockCollision()

        # Check collision with player
        if player.getRect().colliderect(obstacle.getRect()) and player.hitTimer == 0:
            player.hitTimer = min(60, max(30, int(50 - (player.speed * 0.5))))

            player.health -= 1
            player.x = 0
            player.y = 0
            print(f"Collision detected! Health = {player.health}")


        # Check collision with PW Blade
        if player.PW_abilityActive:
            for blade in player.PW_bladeList:
                blade_x, blade_y = blade["pos"]

                # Temporary rect
                blade_rect = pygame.Rect(blade_x, blade_y, player.PW_bladeLength, player.PW_bladeWidth)

                if blade_rect.colliderect(obstacle.getRect()):
                    obstacle.health -= 1

                    if obstacle.obstacleDied(player, finishBlock, AllyBlock, screenWidth, screenHeight, level):
                        obstacleToRemove_uponImpact.append(obstacle)
                        score += 1


        # Removing obstacle (If any)
        for obstacle in obstacleToRemove_uponImpact:
            if obstacle in BlockObstacle.obstacleList:
                BlockObstacle.obstacleList.remove(obstacle)


        # Shoot the damn bullets
        obstacle.shoot(10, 10, level) # Speed of 10 pixels per frame

def checkAllyMovement():
    global AllyBlock, Bullet, BlockObstacle, bossBlock, player, finishBlock, allyToRemove_uponImpact, obstacleToRemove_uponImpact, minionToRemove_uponImpact, screenWidth, screenHeight, level, bossFightActive

    # Check ally block movement
    allyToRemove_uponImpact = []
    obstacleToRemove_uponImpact = []
    minionToRemove_uponImpact = []

    for ally in AllyBlock.aliveAlly:
        # Let the ally move and bounce
        ally.move(player)
        ally.checkBoundary(screenWidth, screenHeight)
        ally.checkAllyCollision()
        ally.checkProtection(player, Bullet.firedBullets, BlockObstacle.obstacleList, Bullet)
        
        # Check collision with obstacle
        for obstacle in BlockObstacle.obstacleList:
            if ally.getRect().colliderect(obstacle.getRect()):
                # Bounce effect

                # Reverse the target position instead of raw dx/dy
                ally.orbitAngle += 180 # Flip orbit direction
                ally.targetX = ally.x + (ally.x - obstacle.x) # Move away from obstacle
                ally.targetY = ally.y + (ally.y - obstacle.y) 

                # Revervse obstacle direction
                obstacle.dx *= -1  
                obstacle.dy *= -1  

                # Reduce health
                ally.health -= 1
                obstacle.health -= 1

                # If ally dead - Append into removal list
                if ally.allyDied():
                    allyToRemove_uponImpact.append(ally)

                # If obstacle dead - Append into removal list
                if obstacle.obstacleDied(player, finishBlock, AllyBlock, screenWidth, screenHeight, level):
                    obstacleToRemove_uponImpact.append(obstacle)

        # Check collision with minions
        if bossFightActive:
            if ally.getRect().colliderect(bossBlock.getRect()):
                # Bounce effect

                # Reverse the target position instead of raw dx/dy
                ally.orbitAngle += 180 # Flip orbit direction
                ally.targetX = ally.x + (ally.x - bossBlock.x) # Move away from obstacle
                ally.targetY = ally.y + (ally.y - bossBlock.y) 

                # Reduce health
                ally.health -= 10 # -10 health for ally otherwise they could exploit
                bossBlock.health -= 1

                # If ally dead - Append into removal list
                if ally.allyDied():
                    allyToRemove_uponImpact.append(ally)

            for minion in bossBlock.activeMinions:
                if ally.getRect().colliderect(minion.getRect()):
                    # Bounce effect

                    # Reverse the target position instead of raw dx/dy
                    ally.orbitAngle += 180 # Flip orbit direction
                    ally.targetX = ally.x + (ally.x - minion.x) # Move away from obstacle
                    ally.targetY = ally.y + (ally.y - minion.y) 

                    # Reduce health
                    ally.health -= 1
                    minion.health -= 1

                    # If ally dead - Append into removal list
                    if ally.allyDied():
                        allyToRemove_uponImpact.append(ally)

                    # If minion dead - Append into removal list
                    if minion.minionDied():
                        minionToRemove_uponImpact.append(minion)

        # Shoot the damn bullets
        ally.shoot(10, 10, level) # Speed of 10 pixels per frame

    # Update abiliity
    for ally in AllyBlock.aliveAlly:
        ally.AO_updateAbility()

    # Removing ally (If any)
    for ally in allyToRemove_uponImpact:
        if ally in AllyBlock.aliveAlly:
            AllyBlock.aliveAlly.remove(ally)

    # Removing obstacle (If any)
    for obstacle in obstacleToRemove_uponImpact:
        if obstacle in BlockObstacle.obstacleList:
            BlockObstacle.obstacleList.remove(obstacle)

    # Removing minions (If any)
    if bossFightActive:
        for minion in minionToRemove_uponImpact:
            if minion in bossBlock.activeMinions:
                bossBlock.activeMinions.remove(minion)

def checkPlayerCollision_withBoss_and_Minion():
    global player, bossBlock, minionToRemove_uponImpact, bossFightActive

    # Check player collision with minion and boss block
    minionToRemove_uponImpact = []

    if bossFightActive:
        if bossBlock.getRect().colliderect(player.getRect()):
            player.hitTimer = min(60, max(30, int(50 - (player.speed * 0.5))))

            player.health -= player.health # Player die instantly
            player.x = 0
            player.y = 0
            print(f"Collision detected! Health = {player.health}")

        for minion in bossBlock.activeMinions:
            if minion.getRect().colliderect(player.getRect()):
                player.hitTimer = min(60, max(30, int(50 - (player.speed * 0.5))))

                player.health -= 1
                player.x = 0
                player.y = 0
                print(f"Collision detected! Health = {player.health}")

    # Removing minions (If any)
    if bossFightActive:
        for minion in minionToRemove_uponImpact:
            if minion in bossBlock.activeMinions:
                bossBlock.activeMinions.remove(minion)

def checkPlayerCollision_withHealBlock():
    global HealerBlock, player, healerToRemove

    # Checking if player hits health block
    healerToRemove = []
    for healer in HealerBlock.activeHealers:
        if healer.getRect().colliderect(player.getRect()):
            healerToRemove.append(healer)

            # Healing player
            player.health += 1

            # Healing ally
            for ally in AllyBlock.aliveAlly:
                ally.health += 1

    # Removing healers (If any)
    for healer in healerToRemove:
        if healer in HealerBlock.activeHealers:
            HealerBlock.activeHealers.remove(healer)

# Creating instances
player = Character(0, 0, 50, 10, colorRGB['blue'], 5)
finishBlock = finishLineBlock(screenWidth, screenHeight, 50, 400, colorRGB['green'])
for i in range(4):
    newObstacle = BlockObstacle(screenWidth, screenHeight, random.randint(100, 250), random.randint(100, 250), colorRGB['yellow'], random.choice([-4, 4]), random.choice([-4, 4]))
    validateObstacleSpawn(newObstacle, BlockObstacle, player, finishBlock, AllyBlock, screenWidth, screenHeight)
    BlockObstacle.obstacleList.append(newObstacle)

displayMenu()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.VIDEORESIZE:
            oldScreenWidth, oldScreenHeight = screenWidth, screenHeight
            screenWidth, screenHeight = event.w, event.h
            mainScreen = mainScreen = pygame.display.set_mode((screenWidth, screenHeight), pygame.RESIZABLE)

            finishBlock.updatePos(screenWidth, screenHeight)
            for obstacle in BlockObstacle.obstacleList:
                obstacle.updatePos(oldScreenWidth, oldScreenHeight, screenWidth, screenHeight)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f and (keys[pygame.K_LMETA] or keys[pygame.K_RMETA] or keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]):  
                fullscreen = False
                if fullscreen:
                    mainScreen = pygame.display.set_mode((screenWidth, screenHeight), pygame.FULLSCREEN)
                else:
                    mainScreen = pygame.display.set_mode((screenWidth, screenHeight), pygame.RESIZABLE)

            # Phantom Whirl (PW)
            if event.key == pygame.K_q:
                player.PW_useAbility()

            # Ally Overclock (AO)
            if event.key == pygame.K_e:
                ally.AO_useAbility(AllyBlock)


    if player.health <= 0:
        displayEndScreen()

    mainScreen.fill(colorRGB['white'])

    keys = pygame.key.get_pressed()
    
    # Shooting bullet
    bulletKeyPress(keys)

    # Player movement
    player.PW_updateAbility()
    player.move(keys)
    player.checkBoundary(screenWidth, screenHeight)

    # Moving bullets
    for bullet in Bullet.firedBullets:
        bullet.move()

    # Checking block movement
    checkBulletMovement()
    checkObstacleMovement()
    checkAllyMovement()

    # Player collision with other block
    checkPlayerCollision_withBoss_and_Minion()
    checkPlayerCollision_withHealBlock()

    # Player hit finishe line
    if player.getRect().colliderect(finishBlock.getRect()):
        player.hitTimer = min(60, max(30, int(50 - (player.speed * 0.5))))

        player.x = 0
        player.y = 0
        levelUp()

    # If there are 1 obstacles left
    if len(BlockObstacle.obstacleList) <= 1:
        player.x = 0
        player.y = 0
        levelUp()

    # Drawing objects
    player.draw(mainScreen)
    player.drawPW_icon(mainScreen, screenWidth, screenHeight)

    if AllyBlock.aliveAlly:
        drawAO_icon(mainScreen, screenWidth, screenHeight, AllyBlock.aliveAlly[0].AO_cooldownTimer)


    for bullet in Bullet.firedBullets:
        bullet.draw(mainScreen)

    for obstacle in BlockObstacle.obstacleList:
        obstacle.draw(mainScreen)

    for healer in HealerBlock.activeHealers:
        healer.draw(mainScreen)

    for ally in AllyBlock.aliveAlly:
        ally.draw(mainScreen)

    finishBlock.draw(mainScreen)

    # THIS IS WHERE IF BOSS BLOCK IS STILL ALIVE LOGIC
    if bossFightActive:
        bossBlock.draw(mainScreen)
        bossBlock.spawnMinion(MinionBlock, level)
        for minion in bossBlock.activeMinions:
            minion.move()
            minion.draw(mainScreen)

        # Check if the boss is defeated
        if bossBlock.bossDied():
            restoreGameAfterBossFight()
            levelUp()

    # Displaying text
    font = pygame.font.Font(None, 50)

    healthText = font.render(f"Health: {player.health}", True, colorRGB['black'])
    mainScreen.blit(healthText, (20, 20))

    levelText = font.render(f"Level: {level}", True, colorRGB['black'])
    mainScreen.blit(levelText, (20, 70))

    scoreText = font.render(f"Score: {score}", True, colorRGB['black'])
    mainScreen.blit(scoreText, (20, 120))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()




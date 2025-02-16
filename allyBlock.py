import pygame
import random
import math
from bulletClass import Bullet
from variablesConst import colorRGB

class AllyBlock():

    aliveAlly = []

    bulletSpeedMultiplier = 1
    maxBulletSpeed = 22

    def __init__(self, screenWidth, screenHeight, player, dx, dy, width, height, color, health):
        self.dx = dx
        self.dy = dy
        self.width = width
        self.height = height
        self.color = color
        self.health = health

        self.originalHealth = None

        # Spawn near the player
        self.x = player.x + random.randint(-100, 100)
        self.y = player.y + random.randint(-100, 100)

        # Prevent spawning off-screen
        self.x = max(10, min(self.x, screenWidth - self.width - 10))
        self.y = max(10, min(self.y, screenHeight - self.height - 10))

        # Movement properties
        self.targetX = self.x # The target position for smooth movement
        self.targetY = self.y
        self.followSpeed = 3 # Speed at which the ally moves toward the target
        self.responseDelay = random.uniform(0.1, 0.3) # Small delay before responding to player movement

        # Collision push effect mechanics
        self.pushForce_x = 0
        self.pushForce_y = 0
        self.pushDelay = 0.9 # Slowly reduce force to create a natural push-back effect

        # Dashing mechanics
        self.dashing = False
        self.dashSpeed = 120  # Dashing speed
        self.dashDuration = 15  # Frames before slowing down
        self.normalSpeed = self.followSpeed  # Reset speed after dash

        # Smart movement
        self.orbitDistance = random.randint(50, 120) # Distance from the player to maintain orbit
        self.orbitAngle = random.uniform(0, 360) # Initial angle around the player

        # Bullet
        self.nextShotTime = pygame.time.get_ticks() + random.randint(1000, 5000)

        # Ally Overclock (AO) active ability
        self.AO_abilityActive = False
        self.AO_abilityTimer = 0
        self.AO_abilityMaxDuration = 300 # 5 sec in effect
        self.AO_fireRateMultiplier = 4.0 # Doubles ally fire rate
        self.AO_movementSpeedMultiplier = 2 # Movement speed multiplier duh

        # Cooldown
        self.AO_cooldownTimer = 0
        self.AO_cooldownMax = 600 # 10 sec cooldown


    def updatePos(self, screenWidth, screenHeight, newScreenWidth, newScreenHeight):
        self.x = int(newScreenWidth * self.x_ratio)
        self.y = int(newScreenHeight * self.y_ratio)

        # Adjust speed if screen size changes
        if newScreenWidth != screenWidth or newScreenHeight != screenHeight:
            self.dx *= newScreenWidth / screenWidth
            self.dy *= newScreenHeight / screenHeight

    def move(self, player):
        # Ally orbits around the player with a sliding effect
        self.orbitAngle += 1.5  # Slight rotation effect each frame
        self.targetX = player.x + math.cos(math.radians(self.orbitAngle)) * self.orbitDistance
        self.targetY = player.y + math.sin(math.radians(self.orbitAngle)) * self.orbitDistance

        # Apply sliding effect toward target (moves based on followSpeed)
        self.x += (self.targetX - self.x) * (0.1 * self.followSpeed)  
        self.y += (self.targetY - self.y) * (0.1 * self.followSpeed)


    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))

        font = pygame.font.Font(None, 28)
        healthText = font.render(str(self.health), True, colorRGB['white'])

        textX = self.x + (self.width // 2) - (healthText.get_width() // 2)
        textY = self.y + (self.height // 2) - (healthText.get_height() // 2)

        surface.blit(healthText, (textX, textY))

    def checkBoundary(self, screenWidth, screenHeight):
        if self.x <= 0 or self.x + self.width > screenWidth:
            self.dx *= -1
        if self.y <= 0 or self.y + self.height > screenHeight:
            self.dy *= -1

    def checkAllyCollision(self):
        for other in AllyBlock.aliveAlly:
            if self == other:
                continue

            if self.getRect().colliderect(other.getRect()):
                self.targetX += (self.x - other.x) * 0.2
                self.targetY += (self.y - other.y) * 0.2
                other.targetX -= (self.x - other.x) * 0.2
                other.targetY -= (self.y - other.y) * 0.2

    def checkProtection(self, player, bullets, obstacles, Bullet):

        # If already dashing - continue
        if self.dashing:
            self.dashDuration -= 1

            # Stop dashing when time runs out
            if self.dashDuration <= 0:
                self.dashing = False
                self.dashDuration = 15  # Reset dash timer
                self.followSpeed = self.normalSpeed  # Reset to normal movement
            return # Skip the function

        nearestThreat = False
        nearestDist = float("inf")

        # Priority 1 - Find nearest bullet (Within 150 pixels)
        for bullet in bullets:

            # Skip if bullet shot by player or ally themselves
            if bullet.owner == 'player' or bullet.owner == 'ally':
                continue
            
            # Distance using pythagoras thereom
            distance = math.sqrt((self.x - bullet.x) ** 2 + (self.y - bullet.y) ** 2)

            if distance < 150 and distance < nearestDist:
                nearestThreat = bullet
                nearestDist = distance

        # Priority 2 - Find nearest obstacle (Within 150 pixels)
        if not nearestThreat:
            for obstacle in obstacles:
                
                distance = math.sqrt((self.x - obstacle.x) ** 2 + (self.y - obstacle.y) ** 2)

                if distance < 150 and distance < nearestDist:
                    nearestThreat = obstacle
                    nearestDist = distance

        # Dash toward the threat
        if nearestThreat:
            self.dashing = True  # Dash mode on
            dx = nearestThreat.x - self.x
            dy = nearestThreat.y - self.y
            distance = max(abs(dx), abs(dy), 1) # Prevent division by zero

            # Move toward the threat
            self.x += (dx / distance) * self.dashSpeed
            self.y += (dy / distance) * self.dashSpeed
            self.targetX = self.x
            self.targetY = self.y

            # If the ally reaches the threat, stop dashing
            # Necessary cuz dash speed too fast, pygame might not register it
            if abs(self.x - nearestThreat.x) < 5 and abs(self.y - nearestThreat.y) < 5:
                if isinstance(nearestThreat, Bullet) and nearestThreat.owner != 'player' and nearestThreat != 'ally': # Remove if it's bullet
                    bullets.remove(nearestThreat)

                # Resetting the ally block to normal
                self.dashing = False
                self.dashDuration = 15
                self.followSpeed = self.normalSpeed
                self.targetX = player.x + random.randint(-100, 100)
                self.targetY = player.y + random.randint(-100, 100)

    def shoot(self, bulletDX, bulletDY, level):
        currentTime = pygame.time.get_ticks()

        if currentTime >= self.nextShotTime:
            bulletDX *= AllyBlock.bulletSpeedMultiplier
            bulletDY *= AllyBlock.bulletSpeedMultiplier

            directions_and_width_height = [(-bulletDX, 0, 50, 10), (bulletDX, 0, 50, 10), (0, -bulletDY, 10, 50), (0, bulletDY, 10, 50)]

            for bulletDX, bulletDY, bulletWidth, bulletHeight in directions_and_width_height:
                new_bullet = Bullet(self.x + self.width // 2, self.y + self.height // 2, bulletDX, bulletDY, bulletWidth, bulletHeight, colorRGB['purple'], "ally")
                Bullet.firedBullets.append(new_bullet)

            # Adjusted fire rate logic
            baseFireRate = max(1500, 5000 - (level * 100)) # Base fire
            if self.AO_abilityActive:
                baseFireRate //= self.AO_fireRateMultiplier # Reduce delay with AO active

            self.nextShotTime = currentTime + baseFireRate

    def AO_useAbility(self, AllyBlock):
        if self.AO_cooldownTimer > 0:
            return

        if not AllyBlock.aliveAlly:
            print("No Ally Blocks available! Cannot activate Ally Overclock.")
            return

        if not self.AO_abilityActive:
            print("Ally Overclock Activated!")
            self.AO_abilityActive = True
            self.AO_abilityTimer = self.AO_abilityMaxDuration

            # Reduce nextShotTime for all allies (Faster fire rate)
            for ally in AllyBlock.aliveAlly:
                ally.nextShotTime = max(500, ally.nextShotTime // self.AO_fireRateMultiplier) # Limit min fire rate
                ally.followSpeed *= self.AO_movementSpeedMultiplier

    def AO_updateAbility(self):
        if self.AO_abilityActive:
            self.AO_abilityTimer -= 1

            if self.AO_abilityTimer <= 0:
                self.AO_abilityActive = False

                # Restore fire rate and movement speed
                self.nextShotTime = max(1500, self.nextShotTime * self.AO_fireRateMultiplier) # Restore timing
                self.followSpeed /= self.AO_movementSpeedMultiplier # Reset movement speed

                # Start cooldown
                self.AO_cooldownTimer = self.AO_cooldownMax

        # Reduce cooldown timer
        if self.AO_cooldownTimer > 0:
            self.AO_cooldownTimer -= 1


    def allyDied(self):
        if self.health <= 0:
            return True # Dead
        
        return False # Alive
    
    def getRect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

# Not included in the class as this method is not for specific instances
def drawAO_icon(surface, screen_width, screen_height, cooldownTimer):
    iconWidth, iconHeight = 50, 50
    iconX = screen_width - 20 - iconWidth
    iconY = screen_height - 20 - iconHeight

    font = pygame.font.Font(None, 30)

    if cooldownTimer > 0:  
        pygame.draw.rect(surface, colorRGB['gray'], (iconX, iconY, iconWidth, iconHeight))  
        cooldownTimeLeft = max(0, cooldownTimer // 60)
        cooldownText = font.render(f"{cooldownTimeLeft}", True, colorRGB['white'])  
        surface.blit(cooldownText, (iconX + 15, iconY + 10))  
    else:
        pygame.draw.rect(surface, colorRGB['green'], (iconX, iconY, iconWidth, iconHeight))  
        ready_text = font.render("E", True, colorRGB['black'])  
        surface.blit(ready_text, (iconX + 15, iconY + 10))
import pygame
import math
from variablesConst import colorRGB

class Character():

    def __init__(self, x, y, size, speed, color, health):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.color = color
        self.health = health
        self.hitTimer = 0

        # Acceleration mechanics
        self.vx = 0
        self.vy = 0
        self.acceleration = 1.2 # How quickly player reaches max speed
        self.friction = 0.85 # How quickly player slows down

        # Phantom Whirl (PW) Active ability
        self.PW_abilityActive = False
        self.PW_abilityTimer = 0
        self.PW_abilityMaxDuration = 180 # For 3 sec
        self.PW_speedMultiplier = 1.2 # 20% increase in speed during PW

        self.PW_cooldownTimer = 0
        self.PW_cooldownMax = 1800 # 30 seconds

        
        # Blade properties
        self.PW_bladeLength = self.size * 3 # Blade is 3x player size
        self.PW_bladeWidth = self.size // 4 # Thin blade, 4x thinner
        self.PW_rotationAngle = 0
        self.PW_rotationSpeed = 30 # Degrees per frame
        self.PW_orbitDistance = self.size * 1.5 # Distance from player

        self.PW_bladeList = []

    def draw(self, surface):
        if self.hitTimer > 0:
            pygame.draw.rect(surface, colorRGB['red'], (self.x, self.y, self.size, self.size))
            self.hitTimer -= 1
        else:
            pygame.draw.rect(surface, self.color, (self.x, self.y, self.size, self.size))

        # Draw blade if PW active
        if self.PW_abilityActive:
            for blade in self.PW_bladeList:
                blade_x, blade_y = blade["pos"]
                blade_angle = blade["angle"]

                # Create a blade surface
                blade_surface = pygame.Surface((self.PW_bladeLength, self.PW_bladeWidth), pygame.SRCALPHA)
                blade_surface.fill(colorRGB['purple'])

                # Rotate the blade
                rotated_blade = pygame.transform.rotate(blade_surface, -blade_angle)

                # Get the new rect and reposition it
                blade_rect = rotated_blade.get_rect(center=(blade_x, blade_y))

                # Draw the rotated blade
                surface.blit(rotated_blade, blade_rect.topleft)


    def PW_useAbility(self):
        if self.PW_cooldownTimer > 0:
            return

        if not self.PW_abilityActive:
            print("Phantom Whirl Activated!")
            self.PW_abilityActive = True
            self.PW_abilityTimer = self.PW_abilityMaxDuration
            self.PW_rotationAngle = 0  
            
            # Speed multiplier
            self.speed *= self.PW_speedMultiplier

            self.PW_cooldownTimer = self.PW_cooldownMax

    def PW_updateAbility(self):
        if self.PW_abilityActive:
            self.PW_abilityTimer -= 1
            self.PW_rotationAngle += self.PW_rotationSpeed # Increase angle for rotation
            
            # Blade hitboxes
            centerX = self.x + self.size // 2
            centerY = self.y + self.size // 2

            blade1_x = centerX + math.cos(math.radians(self.PW_rotationAngle)) * (self.PW_orbitDistance + self.PW_bladeLength // 2)
            blade1_y = centerY + math.sin(math.radians(self.PW_rotationAngle)) * (self.PW_orbitDistance + self.PW_bladeLength // 2)

            blade2_x = centerX + math.cos(math.radians(self.PW_rotationAngle + 180)) * (self.PW_orbitDistance + self.PW_bladeLength // 2)
            blade2_y = centerY + math.sin(math.radians(self.PW_rotationAngle + 180)) * (self.PW_orbitDistance + self.PW_bladeLength // 2)

            # Calculate tilt angles
            blade1_angle = math.degrees(math.atan2(blade1_y - centerY, blade1_x - centerX))
            blade2_angle = math.degrees(math.atan2(blade2_y - centerY, blade2_x - centerX))

            # Store blade positions and angles
            self.PW_bladeList = [
                {"pos": (blade1_x, blade1_y), "angle": blade1_angle},
                {"pos": (blade2_x, blade2_y), "angle": blade2_angle}
            ]

            if self.PW_abilityTimer <= 0:
                self.PW_abilityActive = False
                self.speed /= self.PW_speedMultiplier # Reset speed
                self.PW_bladeList = [] # Reset list
                print("Phantom Whirl Ended!")

        if self.PW_cooldownTimer > 0:
            self.PW_cooldownTimer -= 1

    def drawPW_icon(self, surface, screen_width, screen_height):
        iconWidth, iconHeight = 50, 50

        # Bottom right
        iconX = screen_width - 20 - iconWidth - 20 - iconWidth
        iconY = screen_height - 20 - iconHeight - 20 - iconHeight

        font = pygame.font.Font(None, 30)

        if self.PW_cooldownTimer > 0:  
            pygame.draw.rect(surface, colorRGB['gray'], (iconX, iconY, iconWidth, iconHeight)) # Gray when on cooldown

            # Calculate remaining cooldown time
            cooldownTimeLeft = max(0, self.PW_cooldownTimer // 60) # Convert frames to seconds

            # Render "Q" and cooldown time
            cooldownText = font.render(f"{cooldownTimeLeft}", True, colorRGB['white']) # White text
            surface.blit(cooldownText, (iconX + 15, iconY + 10)) # Centered text
        else:
            pygame.draw.rect(surface, colorRGB['green'], (iconX, iconY, iconWidth, iconHeight)) # Green when ready
            ready_text = font.render("Q", True, colorRGB['black']) # Black text
            surface.blit(ready_text, (iconX + 15, iconY + 10))


    def move(self, keys):
        if keys[pygame.K_a]:
            self.vx -= self.acceleration
        if keys[pygame.K_d]:
            self.vx += self.acceleration
        if keys[pygame.K_w]:
            self.vy -= self.acceleration
        if keys[pygame.K_s]:
            self.vy += self.acceleration

        # Set max speed limit
        self.vx = max(-self.speed, min(self.vx, self.speed))
        self.vy = max(-self.speed, min(self.vy, self.speed))

        # Decelerates when no keys are pressed
        if not (keys[pygame.K_a] or keys[pygame.K_d]):
            self.vx *= self.friction
        if not (keys[pygame.K_w] or keys[pygame.K_s]):
            self.vy *= self.friction

        # If velocity too small - Stop movement (Avoid inifinite sliding)
        if abs(self.vx) < 0.1:
            self.vx = 0
        if abs(self.vy) < 0.1:
            self.vy = 0

        # Update position based on velocity
        self.x += self.vx
        self.y += self.vy

    def checkBoundary(self, screen_width, screen_height):
        if self.x < 0:
            self.x = 0
            self.vx = 0
        if self.y < 0:
            self.y = 0
            self.vy = 0

        if self.x + self.size > screen_width:
            self.x = screen_width - self.size
            self.vx = 0
        if self.y + self.size > screen_height:
            self.y = screen_height - self.size
            self.vy = 0

    def getRect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)
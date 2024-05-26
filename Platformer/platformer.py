import pygame
import math

pygame.init()
clock = pygame.time.Clock()
screenWidth = 800
screenHeight = int(screenWidth * 0.8)

screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("Platformer")

background = pygame.image.load('imgs/world/background.jpg').convert()
background = pygame.transform.scale(background, (screenWidth, screenHeight))
backgroundWidth = background.get_width()

scale = 0.4


class Combatant(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('imgs/player/mainPlayer.png')
        self.image = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 5
        self.jumpSpeed = 20
        self.gravity = 1.7
        self.velY = 0
        self.jumpsLeft = 2
        self.maxJumps = 2

        self.fixedLeftPosition = screenWidth * 0.3  # Player position fixed at 40% of the screen width from the left
        self.fixedRightPosition = screenWidth * 0.5  # Player position fixed at 40% of the screen width from the left
        self.orientationLeft = self.image
        self.orientationRight = pygame.transform.flip(self.image, True, False)

    def draw(self):
        # Blit the current image to the screen at the current position
        screen.blit(self.image, self.rect.topleft)
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)


    def move(self, direction):
        if direction == 'left':  # Check to make sure the player does not go off the left side
            self.image = self.orientationLeft
            if self.rect.x > self.fixedLeftPosition:
                self.rect.x -= self.speed
            return -self.speed  # Scroll background right
        elif direction == 'right':
            self.image = self.orientationRight
            # Keep the player fixed when moving right and scroll the background
            if self.rect.x < self.fixedRightPosition:
                self.rect.x += self.speed
            return self.speed  # Scroll background left
        return 0

    def jump(self):
        # Handle jumping only if jumps are left
        if self.jumpsLeft > 0:
            self.velY = -self.jumpSpeed
            self.jumpsLeft -= 1

    def update(self):
        # Apply gravity
        self.velY += self.gravity
        self.rect.y += self.velY

        # Check if on ground
        if self.rect.bottom > screenHeight * 0.95:
            self.rect.bottom = screenHeight * 0.95
            self.jumpsLeft = self.maxJumps  # Reset jump counter when on ground
        for platform in platforms:
            if platform.rect.colliderect(self.rect):
                if self.velY > 0:  # Falling down
                    if self.rect.bottom <= platform.rect.bottom:
                        self.rect.bottom = platform.rect.top
                        self.velY = 0
                        self.jumpsLeft = self.maxJumps
                elif self.velY < 0:  # Moving up
                    if self.rect.top >= platform.rect.top:
                        self.rect.top = platform.rect.bottom
                        self.velY = 0

    def attack(self):
        pass  # Filler for attack logic


def drawBackground(scroll):
    # Draw background with seamless tiling
    relX = scroll % backgroundWidth
    screen.blit(background, (relX - backgroundWidth, 0))
    if relX < screenWidth:
        screen.blit(background, (relX, 0))


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('imgs/world/platform.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (width, height)) 
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.fixed_x = x  

    def draw(self):
        self.rect.x = self.fixed_x + scroll
        screen.blit(self.image, self.rect.topleft)
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)
        

scroll = 0

# Create the main player
player = Combatant(int(screenWidth * .4), screenHeight * 0.89, scale)

# Create the platforms
platforms = [
    Platform(200, 500, 200, 20),
    Platform(400, 500, 100, 20),
    Platform(600, 400, 100, 20)
]
running = True
while running:
    clock.tick(50)
    screen.fill((0, 0, 0))  # Clear the screen with black before drawing background
    drawBackground(scroll)

    scrollChange = 0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        scrollChange = player.move('left')
    if keys[pygame.K_RIGHT]:
        scrollChange = player.move('right')
    if keys[pygame.K_UP]:
        player.jump()  # Activate jump on up arrow press

    if scrollChange != 0:
        scroll -= scrollChange  # Update scroll based on player movement

    player.update()
    player.draw()

    for platform in platforms:
        platform.draw()
    pygame.display.update()

pygame.quit()

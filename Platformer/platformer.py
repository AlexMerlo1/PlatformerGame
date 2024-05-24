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

        self.fixedRightPosition = screenWidth * 0.4  # Player position fixed at 20% of the screen width from the left
        self.orientationLeft = self.image
        self.orientationRight = pygame.transform.flip(self.image, True, False)

    def draw(self):
        # Blit the current image to the screen at the current position
        screen.blit(self.image, self.rect.topleft)

    def move(self, direction):
        if direction == 'left' and self.rect.left > 0:  # Check to make sure the player does not go off the left side
            self.image = self.orientationLeft
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

    def attack(self):
        pass  # Filler for attack logic


def drawBackground(scroll):
    # Draw background with seamless tiling
    relX = scroll % backgroundWidth
    screen.blit(background, (relX - backgroundWidth, 0))
    if relX < screenWidth:
        screen.blit(background, (relX, 0))


scroll = 0
player = Combatant(200, screenHeight * 0.89, scale)

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
    pygame.display.update()

pygame.quit()

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
ground_height = 50


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((10, 5))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 10
        self.direction = direction


    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.right < 0 or self.rect.left > screenWidth:
            self.kill()


class Combatant(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('imgs/player/mainPlayer_Edit.png')
        self.image = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 6
        self.jumpSpeed = 20
        self.gravity = 1.7
        self.velY = 0
        self.jumpsLeft = 2
        self.maxJumps = 2

        self.fixedLeftPosition = screenWidth * 0.425
        self.fixedRightPosition = screenWidth * 0.425
        self.orientationLeft = self.image
        self.orientationRight = pygame.transform.flip(self.image, True, False)

        self.direction = 1

        self.bullets = pygame.sprite.Group()
        self.shootCooldown = 500
        self.lastShot = pygame.time.get_ticks()


    def draw(self):
        # Blit the current image to the screen at the current position
        screen.blit(self.image, self.rect.topleft)
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)
        self.bullets.draw(screen)

    def move(self, direction):
        if direction == 'left':  # Check to make sure the player does not go off the left side
            self.image = self.orientationLeft
            self.direction = -1
            if self.rect.x > self.fixedLeftPosition:
                self.rect.x -= self.speed
            return -self.speed  # Scroll background right
        elif direction == 'right':
            self.image = self.orientationRight
            self.direction = 1
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
        for platform in platforms:
            if platform.rect.colliderect(self.rect):
                if self.velY > 0:  # Falling down
                    if self.rect.bottom <= platform.rect.bottom:
                        self.rect.bottom = platform.rect.top
                        self.velY = 0
                        self.jumpsLeft = self.maxJumps
                elif self.velY < 0:  # Moving up
                    if self.rect.top > platform.rect.top:
                        self.rect.top = platform.rect.bottom
                        self.velY = 0
        for ground in ground_segments:
            if ground.collidepoint(self.rect.midbottom):
                # Check if the player is over a hole
                in_hole = False
                for hole in holes:
                    hole_rect = pygame.Rect(hole[0] + scroll, screenHeight - ground_height, hole[1], ground_height)
                    if hole_rect.collidepoint(self.rect.midbottom):
                        in_hole = True
                        break

                if not in_hole and self.velY > 0:  # Falling down
                    if self.rect.bottom <= ground.bottom:
                        self.rect.bottom = ground.top
                        self.velY = 0
                        self.jumpsLeft = self.maxJumps
                        break

        self.bullets.update()

    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.lastShot > self.shootCooldown:
            bullet = Bullet(self.rect.centerx, self.rect.centery, self.direction)
            self.bullets.add(bullet)
            self.lastShot = current_time


    def attack(self):
        self.shoot()  # Filler for attack logic


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


# Define ground and holes


# Load ground image
groundImg = pygame.image.load('imgs/world/ground.jpg').convert_alpha()
groundImg = pygame.transform.scale(groundImg, (50, ground_height))  # Adjust as needed


def create_ground_segments(total_length, holes, ground_height):
    segments = []
    current_x = 0

    for hole in holes:
        hole_start, hole_width = hole
        if current_x < hole_start:
            segment_length = hole_start - current_x
            num_segments = math.ceil(segment_length / groundImg.get_width())
            for i in range(num_segments):
                x = current_x + i * groundImg.get_width()
                segments.append(pygame.Rect(x, screenHeight - ground_height, groundImg.get_width(), ground_height))
        current_x = hole_start + hole_width
    if current_x < total_length:
        segment_length = total_length - current_x
        num_segments = math.ceil(segment_length / groundImg.get_width())
        for i in range(num_segments):
            x = current_x + i * groundImg.get_width()
            segments.append(pygame.Rect(x, screenHeight - ground_height, groundImg.get_width(), ground_height))

    return segments


##### LEVEL CREATION #####

# Draw ground segments
def drawGround():
    for segment in ground_segments:
        screen.blit(groundImg, (segment.x + scroll, segment.y))


def createPlatforms(currentLevel):
    level_platforms = []

    # LEVEL 1 PLATFORM CREATION
    if currentLevel == 1:
        platforms = [
            Platform(200, 450, 200, 20),
            Platform(400, 450, 100, 20),
            Platform(600, 450, 100, 20)
        ]

    # LEVEL 2 PLATFORM CREATION

    # APPEND ALL PLATFORMS
    for platform in platforms:
        level_platforms.append(platform)
    return level_platforms


def createHoles(currentLevel):
    level_holes = []

    # LEVEL 1 PLATFORM CREATION
    if currentLevel == 1:
        # Format (position, width)
        holes = [
            (500, 100),
            (800, 100),
            (1500, 100)
        ]

        # LEVEL 2 PLATFORM CREATION

    # APPEND ALL PLATFORMS
    for hole in holes:
        level_holes.append(hole)
    return level_holes


def getLength(currentLevel):
    # Create level lengths
    if currentLevel == 1:
        return 6000


currentLevel = 1

# Call all level creation methods
platforms = createPlatforms(currentLevel)
holes = createHoles(currentLevel)
currentLevelLength = getLength(currentLevel)
#enemies = createEnemies(currentLevel)

# Create the level ground


ground_segments = create_ground_segments(currentLevelLength, holes, ground_height)

# CREATE ENEMIES FOR LEVEL


##### END OF LEVEL CREATION #####


scroll = 0

# Create the main player
player = Combatant(int(screenWidth * .47), screenHeight * 0.89, scale)

# Create the platforms

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
    if keys[pygame.K_SPACE]:
        player.attack()

    if scrollChange != 0:
        scroll -= scrollChange  # Update scroll based on player movement

    player.update()
    player.draw()
    drawGround()
    for platform in platforms:
        platform.draw()
    pygame.display.update()

pygame.quit()

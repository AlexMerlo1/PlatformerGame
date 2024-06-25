import pygame
import math

pygame.init()
clock = pygame.time.Clock()
screenWidth = 800
screenHeight = int(screenWidth * 0.8)

screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("Platformer")

background = pygame.image.load('Platformer/imgs/world/background.jpg').convert()
background = pygame.transform.scale(background, (screenWidth, screenHeight))
backgroundWidth = background.get_width()

scale = 0.4
ground_height = 50

jump_sound = pygame.mixer.Sound("soundEffects/jump.mp3")
player_hit_sound = pygame.mixer.Sound("soundEffects/PlayerHit.mp3")
game_over_sound = pygame.mixer.Sound("soundEffects/gameOver.mp3")
bullet_sound = pygame.mixer.Sound("soundEffects/bullet.wav")
level_completed_sound = pygame.mixer.Sound("soundEffects/levelCompleted.mp3")


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((10, 5))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 10
        self.direction = direction
    def is_colliding_horizontally(self):
        # Check collision with raised ground segments
        for segment in raised_segments:
            segment_rect = pygame.Rect(segment[0] + scroll, segment[1], segment[2], ground_height)
            if self.rect.colliderect(segment_rect):
                return True
        return False

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.right < 0 or self.rect.left > screenWidth or self.is_colliding_horizontally():
            self.kill()

class Combatant(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, type):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('Platformer/imgs/player/mainPlayer_Edit.png')
        self.image = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 6
        self.jumpSpeed = 20
        self.gravity = 1.3
        self.velY = 0
        self.jumpsLeft = 2
        self.maxJumps = 2
        self.type = type
        self.health = 50
        self.fixedLeftPosition = screenWidth * 0.425
        self.fixedRightPosition = screenWidth * 0.425
        self.orientationLeft = self.image
        self.orientationRight = pygame.transform.flip(self.image, True, False)

        self.direction = 1

        self.bullets = pygame.sprite.Group()
        self.shootCooldown = 500
        self.lastShot = pygame.time.get_ticks()

    def getCords(self):
        return self.rect.centerx - scroll, self.rect.centery
    
    def draw(self):
        # Blit the current image to the screen at the current position
        screen.blit(self.image, self.rect.topleft)
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)
        self.bullets.draw(screen)

    def move(self, direction):
        if direction == 'left' and self.type == 'player':  # Check to make sure the player does not go off the left side
            self.image = self.orientationLeft
            self.direction = -1
            if self.rect.x > self.fixedLeftPosition:
                self.rect.x -= self.speed
            return -self.speed  # Scroll background right
        elif direction == 'right' and self.type == 'player':
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
            if self.type == "player":
                jump_sound.play()

    def update(self):
        # Apply gravity
        self.velY += self.gravity
        self.rect.y += self.velY

        on_ground = False
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
        if self.is_colliding_horizontally():
            self.rect.x -= -1 * self.speed
        on_ground = self.is_colliding_vertically()

        if on_ground:
            self.jumpsLeft = self.maxJumps
        if self.player_death():
            restart_level(player_died = True)
        self.check_bullet_collisions()
        self.bullets.update()

    def is_colliding_vertically(self):
        for segment in raised_segments:
            segment_rect = pygame.Rect(segment[0] + scroll, segment[1], segment[2], ground_height)
            if segment_rect.colliderect(self.rect):
                if self.velY > 0:  # Falling down
                    if self.rect.bottom <= segment_rect.bottom:
                        self.rect.bottom = segment_rect.top
                        self.velY = 0
                        self.jumpsLeft = self.maxJumps
                        return True
                elif self.velY < 0:  # Moving up
                    if self.rect.top > segment_rect.top:
                        self.rect.top = segment_rect.bottom
                        self.velY = 0
        return False
    def is_colliding_horizontally(self):
        # Check collision with raised ground segments
        for segment in raised_segments:
            segment_rect = pygame.Rect(segment[0] + scroll, segment[1], segment[2], ground_height)
            if self.rect.collidepoint(segment_rect.midleft) or self.rect.collidepoint(segment_rect.midright):
                return True
        return False


    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.lastShot > self.shootCooldown:
            bullet = Bullet(self.rect.centerx, self.rect.centery, self.direction)
            self.bullets.add(bullet)
            self.lastShot = current_time
            if self.type == "player":
                bullet_sound.play()

    def check_bullet_collisions(self):
        for enemy in enemies:
            enemy_bullets = enemy.bullets
            for bullet in enemy_bullets:
                if bullet.rect.colliderect(player.rect):
                    bullet.kill()
                    print(f'{self.type.capitalize()} hit!')
                    player_hit_sound.play()
                    self.health -= 10
                    print(f'Player Health {self.health}')

    def player_death(self):
        if self.health <= 0:
            self.kill()
            return True
        if self.rect.y >= screenHeight:
            self.kill()
            return True
        return False

    def attack(self):
        self.shoot()  # Filler for attack logic
        

# Create the enemy class
class Enemy(Combatant):
    def __init__(self, x, y, scale, type):
        super().__init__(x, y, scale, type)
        img = pygame.image.load('Platformer/imgs/player/mainPlayer_Edit.png')
        self.image = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.world_x = x
        self.world_y = y
        self.speed = 3.5
        self.direction = 1
        self.detectionRange = 500
        self.shootCooldown = 2000  # Same as player
        self.jumpsLeft = 2
        self.lastShot = pygame.time.get_ticks() 
        self.jumpCooldown = 1000
        self.last_jump_time = 0
        self.jumpSpeed = 22.5
        self.playerDetectedTimer = 0
        self.playerDetectedTimeLimit = 2000
        self.jumpDuration = 1000
        self.justJumped = False
        self.health = 30
    def update(self, player):

        # Check collision with raised segments
        if self.is_colliding_horizontally() or self.is_colliding_vertically():
            self.rect.x -= -1 * self.speed
        playerCordsX, playerCordsY = player.getCords()
        enemyCordsX, enemyCordsY = self.world_x, self.world_y
        distance = math.sqrt((playerCordsX - enemyCordsX) ** 2 + (playerCordsY - enemyCordsY) ** 2)
        if distance <= self.detectionRange:
            playerDetected = True
            self.playerDetectedTimer = self.playerDetectedTimeLimit
        else:
            if self.playerDetectedTimer > 0:
                playerDetected = True
                self.playerDetectedTimer -= clock.get_time()
            else: 
                playerDetected = False
        if playerDetected:
            self.speed = 3.5  # Set a speed for chasing
            # Calculate direction to player
            dirX = playerCordsX - enemyCordsX
            dirY = playerCordsY - enemyCordsY
            distance = math.sqrt(dirX**2 + dirY**2)
            dirX /= distance
            dirY /= distance
            if playerCordsX < enemyCordsX and playerDetected:
                self.direction = -1
            elif playerCordsX > enemyCordsX and playerDetected:
                self.direction = 1

            if abs(enemyCordsY - playerCordsY) <= 50:
                self.shoot()
            current_time = pygame.time.get_ticks()
            if self.isValidJump(self.world_x, self.world_y) and abs(enemyCordsY - playerCordsY) >= 50:
                if current_time - self.last_jump_time > self.jumpCooldown:
                    self.jump()
                    self.last_jump_time = current_time
                    self.justJumped = True
                    self.jumpStartTime = current_time

            if self.justJumped:
                if current_time - self.jumpStartTime < self.jumpDuration:
                    self.world_x += dirX * self.speed
                    self.rect.x = self.world_x
                else:
                    self.justJumped = False

            if not self.justJumped:

                if self.on_raised_segment():
                    self.chase_and_attack(dirX, enemyCordsX, enemyCordsY)
                    
                elif self.is_on_ground_left() and playerCordsX <= enemyCordsX:
                    self.chase_and_attack(dirX, enemyCordsX, enemyCordsY)

                elif self.is_on_ground_right() and playerCordsX >= enemyCordsX:
                    self.chase_and_attack(dirX, enemyCordsX, enemyCordsY)
    
        else:
            self.speed = 3.5
            # Ensure enemy stays within bounds or turn around
            on_ground_left = self.is_on_ground_left()
            on_ground_right = self.is_on_ground_right()

            if not on_ground_left:
                self.direction *= -1
            if not on_ground_right:
                self.direction *= -1

            self.world_x += self.speed * self.direction
            self.rect.x = self.world_x
            
        # Update the vertical position based on gravity and ground collisions
        self.velY += self.gravity
        self.world_y += self.velY
        self.rect.y = self.world_y
        for ground in ground_segments:
            if ground.collidepoint((self.world_x, self.rect.midbottom[1])):
                if self.velY > 0:  # Falling down
                    if self.rect.bottom <= ground.bottom:
                        self.rect.bottom = ground.top
                        self.velY = 0
                        self.jumpsLeft = self.maxJumps
                        self.world_y = self.rect.y
        for segment in raised_segments:
            segment_rect = pygame.Rect(segment[0], segment[1], segment[2], ground_height)
            if segment_rect.collidepoint((self.world_x, self.rect.bottom)):
                if self.velY > 0:  # Falling down
                    if self.rect.bottom <= segment_rect.bottom:
                        self.rect.bottom = segment_rect.top
                        self.velY = 0
                        self.jumpsLeft = self.maxJumps
                        self.world_y = self.rect.y
        on_ground = False
        if self.is_colliding_horizontally():
            self.rect.x -= -1 * self.speed

        if on_ground:
            self.jumpsLeft = self.maxJumps
        if self.enemy_defeated():
            enemies.remove(self)
        self.bullets.update()
        self.check_bullet_collisions()

    def on_raised_segment(self):
        for segment in raised_segments:
            segment_rect = pygame.Rect(segment[0], segment[1], segment[2], ground_height)
            if segment_rect.collidepoint((self.rect.bottomleft)) or segment_rect.collidepoint((self.rect.bottomright)):
                return True
        return False
    def chase_and_attack(self, dirX, enemyCordsY, playerCordsY):
        self.world_x += dirX * self.speed
        self.rect.x = self.world_x
        if abs(enemyCordsY - playerCordsY) <= 50:
            self.shoot()

    def isValidJump(self, world_x, world_y):
        jumpHeight = 100  
        hypotenuseDistance = 75

        # Check if there is a platform or raised segment directly above 
        rect_above = pygame.Rect(self.rect.x, self.rect.y - jumpHeight, self.rect.width, self.rect.height)

        for segment in raised_segments:
            segment_rect = pygame.Rect(segment[0], segment[1], segment[2], ground_height)
            if rect_above.colliderect(segment_rect):
                return False

        direction_multiplier = self.direction

        # Find the nearest obstacle distance
        nearest_obstacle_distance = float('inf')
        nearest_obstacle_rect = None

        # Check for raised segments in the direction of movement
        if direction_multiplier == 1:
            # Moving to the right
            for segment in raised_segments:
                distance = segment[0] - (world_x + self.rect.width)
                if 0 <= distance < nearest_obstacle_distance:
                    nearest_obstacle_distance = distance
                    nearest_obstacle_rect = pygame.Rect(segment[0], segment[1], segment[2], ground_height)
        elif direction_multiplier == -1:
            # Moving to the left
            for segment in raised_segments:
                distance = world_x - (segment[0] + segment[2])
                if 0 <= distance < nearest_obstacle_distance:
                    nearest_obstacle_distance = distance
                    nearest_obstacle_rect = pygame.Rect(segment[0], segment[1], segment[2], ground_height)

        # Check if the enemy is close enough to jump
        if nearest_obstacle_distance <= hypotenuseDistance and nearest_obstacle_rect:
            playerCordsX, playerCordsY = player.getCords()
            if playerCordsY <= world_y:
                # Check if there are any obstacles between the enemy and raised segment
                enemy_rect = pygame.Rect(world_x, world_y, self.rect.width, self.rect.height)
                if not enemy_rect.colliderect(nearest_obstacle_rect):
                    # Ensure the enemy is to the obstacle 
                    if abs(self.rect.y - nearest_obstacle_rect.top) <= jumpHeight:
                        return True

        return False

    def check_bullet_collisions(self):
        player_bullets = get_all_player_bullets(player)
        for bullet in player_bullets:
            bullet_rect_with_scroll = bullet.rect.copy()
            bullet_rect_with_scroll.x -= scroll
            if bullet_rect_with_scroll.colliderect(self.rect):
                bullet.kill()
                self.health -= 10
                print(f'Enemy Health {self.health}')
    
    def enemy_defeated(self):
        if self.health <= 0:
            self.kill()
            return True
        return False

    def is_on_ground_left(self):
        on_ground_left = False
        left_x = self.world_x - 10  # Check slightly to the left of the enemy's current position
        for ground in ground_segments:
            if ground.collidepoint((left_x, self.rect.bottom)):
                on_ground_left = True
        for segment in raised_segments:
            segment_rect = pygame.Rect(segment[0], segment[1], segment[2], ground_height)
            if segment_rect.collidepoint((left_x, self.rect.bottom)):
                on_ground_left = True
        return on_ground_left

    def is_on_ground_right(self):
        on_ground_right = False
        right_x = self.world_x + self.rect.width  # Check slightly to the right of the enemy's current position
        for ground in ground_segments:
            if ground.collidepoint((right_x, self.rect.bottom)):
                on_ground_right = True
        for segment in raised_segments:
            segment_rect = pygame.Rect(segment[0], segment[1], segment[2], ground_height)
            if segment_rect.collidepoint((right_x, self.rect.bottom)):
                on_ground_right = True
        return on_ground_right

    def draw(self):
        # Adjust the enemy's position relative to the scroll value
        screen.blit(self.image, (self.world_x + scroll, self.rect.y))
        pygame.draw.rect(screen, (255, 0, 0), (self.world_x + scroll, self.rect.y, self.rect.width, self.rect.height), 2)
        if self.direction == -1:
            self.image = self.orientationLeft
        else:
            self.image = self.orientationRight
        self.bullets.draw(screen)
    def is_colliding_vertically(self):
        for segment in raised_segments:
            segment_rect = pygame.Rect(segment[0], segment[1], segment[2], ground_height)
            if segment_rect.colliderect(self.rect):
                if self.velY > 0:  # Falling down
                    if self.rect.bottom <= segment_rect.bottom:
                        self.rect.bottom = segment_rect.top + 10
                        self.velY = 0
                        self.jumpsLeft = self.maxJumps
                        self.world_y = self.rect.y - 10
                        return True
                elif self.velY < 0:  # Moving up
                    if self.rect.top > segment_rect.top:
                        self.rect.top = segment_rect.bottom
                        self.velY = 0
                        self.world_y = self.rect.y
                        
        return False
    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.lastShot > self.shootCooldown:
            bullet = Bullet(self.rect.centerx + scroll, self.rect.centery, self.direction)
            self.bullets.add(bullet)
            self.lastShot = current_time


def get_all_player_bullets(player):
    return list(player.bullets)

def drawBackground(scroll):
    # Draw background with seamless tiling
    relX = scroll % backgroundWidth
    screen.blit(background, (relX - backgroundWidth, 0))
    if relX < screenWidth:
        screen.blit(background, (relX, 0))


### START AND END GAME BEHAVIORS ###
def start_game():
    pass

def end_game():
    pass

def restart_level(player_died):
    if player_died == True:
        return False # End game if Player dies
    else:
        return True


### END OF GAME ENDING BEHAVIORS ###

# Define ground and holes
# Load ground image
groundImg = pygame.image.load('Platformer/imgs/world/ground.jpg').convert_alpha()
groundImg = pygame.transform.scale(groundImg, (50, ground_height))  # Adjust as needed


##### LEVEL CREATION #####

# Draw ground segments
def drawGround():
    for segment in ground_segments:
        screen.blit(groundImg, (segment.x + scroll, segment.y))
    for segment in raised_segments:
        x, y, width = segment
        num_segments = math.ceil(width / groundImg.get_width())
        for i in range(num_segments):
            screen.blit(groundImg, (x + i * groundImg.get_width() + scroll, y))

def createEnemies(currentLevel):
    level_enemies = []

    if currentLevel == 1:
        enemies = [
            Enemy(1200, screenHeight - ground_height - 50, scale, 'enemy'),
            Enemy(3200, screenHeight - ground_height - 50, scale, 'enemy'),
            Enemy(2200, screenHeight - ground_height - 50, scale, 'enemy'),
            Enemy(5000, screenHeight - ground_height - 50, scale, 'enemy')
        ]

    for enemy in enemies:
        level_enemies.append(enemy)
    return level_enemies

def createHoles(currentLevel):
    level_holes = []

    # LEVEL 1 Holes CREATION
    if currentLevel == 1:
        # Format (position, width)
        holes = [
            (500, 100),
            (800, 100),
            (1500, 100)
        ]

    # LEVEL 2 Holes CREATION

    # APPEND ALL HOLES
    for hole in holes:
        level_holes.append(hole)
    return level_holes

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

def createRaisedGroundSegments(currentLevel):
    raised_segments = []

    if currentLevel == 1:
        # (x, y, width)
        raised_segments = [
            (800, screenHeight - ground_height - 150, 300),
            (1500, screenHeight - ground_height - 150, 400),
            (2000, screenHeight - ground_height - 300, 200),
            (3000, screenHeight - ground_height - 150, 400),
            (3350, screenHeight - ground_height - 300, 200),
            (3600, screenHeight - ground_height - 450, 400),
            (5000, screenHeight - ground_height - 150, 200),
            (5400, screenHeight - ground_height - 250, 400)

        ]
        # Create raised segments from ground to top of screen
        num_segments = screenHeight // ground_height  

        for i in range(num_segments):
            x = 0
            y = i * ground_height
            raised_segments.append((x, y, ground_height))
    return raised_segments

def getLength(currentLevel):
    # Create level lengths
    if currentLevel == 1:
        return 6000

        
currentLevel = 1

# Call all level creation methods
holes = createHoles(currentLevel)
currentLevelLength = getLength(currentLevel)

# CREATE ENEMIES FOR LEVEL
enemies = createEnemies(currentLevel)

# Create the level ground
ground_segments = create_ground_segments(currentLevelLength, holes, ground_height)
raised_segments = createRaisedGroundSegments(currentLevel)



##### END OF LEVEL CREATION #####


scroll = 0

# Create the main player
player = Combatant(int(screenWidth * .47), screenHeight * 0.89, scale, 'player')
enemy_bullets = pygame.sprite.Group()
running = True
game_frozen = False
game_completed = False
game_over = False


while running:
    clock.tick(50)
    screen.fill((0, 0, 0)) 
    drawBackground(scroll)

    scrollChange = 0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # Check if player is within the level bounds
    if game_frozen == False:
        if keys[pygame.K_LEFT]:
            scrollChange = player.move('left')
        if keys[pygame.K_RIGHT]:
            scrollChange = player.move('right')
        if keys[pygame.K_UP]:
            player.jump()
        if keys[pygame.K_SPACE]:
            player.attack()
            
            

    if player.rect.x - scroll >= currentLevelLength:
        game_frozen = True
        if game_completed == False:
            print('Game over, you won!')
            level_completed_sound.play()
        game_completed = True

    if player.health <= 0 or player.rect.y >= screenHeight:
        game_frozen = True
        if game_over == False:
            print('Game over, you lost')
            game_over_sound.play()
        game_over = True    
        


    # Update scroll based on player movement if not beyond the level length
    if scrollChange != 0 and not player.is_colliding_horizontally() and player.rect.x <= currentLevelLength:
        scroll -= scrollChange

    player.update()
    player.draw()
    drawGround()

    for enemy in enemies:
        if game_frozen == False:  
            enemy.update(player)
        enemy.draw()

    pygame.display.update()

pygame.quit()

import pygame

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Platformer")

scale = 0.4

class Combatant(pygame.sprite.Sprite):
  def __init__(self, x, y, scale):
    pygame.sprite.Sprite.__init__(self)
    img = pygame.image.load('imgs/player/mainPlayer.png')
    self.image = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
    self.rect = self.image.get_rect()
    self.rect.center = (x, y)
    self.speed = 5
    self.jump_speed = 10
    self.gravity = 0.3
    self.vel_y = 0
    self.jumps_left = 2
    self.max_jumps = 2

    self.orientationLeft = self.image
    self.orientationRight = pygame.transform.flip(self.image, True, False)

  def draw(self):
    screen.blit(self.image, self.rect)

  def move(self, direction):
    if direction == 'left':
      if self.rect.left > 0:  # Check to make sure the player does not go off the left side
        self.image = self.orientationLeft
        self.rect.x -= self.speed
    if direction == 'right':
      if self.rect.right < SCREEN_WIDTH:  # Check to make sure the player does not go off the right side
        self.image = self.orientationRight
        self.rect.x += self.speed
    if direction == 'jump' and self.jumps_left > 0:
      self.vel_y = -self.jump_speed
      self.jumps_left -= 1

  def update(self):
    # Apply gravity
    self.vel_y += self.gravity
    self.rect.y += self.vel_y

    # Check if on ground
    if self.rect.bottom > SCREEN_HEIGHT * 0.95:
      self.rect.bottom = SCREEN_HEIGHT * 0.95
      self.jumps_left = self.max_jumps

  def attack(self):
    pass  # Filler for attack logic

def draw_background():
  background = pygame.image.load('imgs/world/background.jpg')
  background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
  screen.blit(background, (0, 0))
  pygame.draw.line(screen, (255, 0, 0), (0, SCREEN_HEIGHT * 0.95), (SCREEN_WIDTH, SCREEN_HEIGHT * 0.95))

player = Combatant(200, SCREEN_HEIGHT * 0.89, scale)

running = True
while running:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False

  draw_background()

  keys = pygame.key.get_pressed()
  if keys[pygame.K_LEFT]:
    player.move('left')
  if keys[pygame.K_RIGHT]:
    player.move('right')
  if keys[pygame.K_UP]:
    player.move('jump')
  if keys[pygame.K_SPACE]:
    player.attack()

  player.update()
  player.draw()
  pygame.display.update()

pygame.quit()

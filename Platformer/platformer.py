import pygame

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * .8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Platformer")

scale = .4
# Create class that will be used for the player and enemies
class combatant(pygame.sprite.Sprite):
  def __init__(self, x, y, scale):
    pygame.sprite.Sprite.__init__(self) # Inherit properties from sprite class
    img = pygame.image.load('imgs/player/mainPlayer.png')
    self.image = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
    self.rect = self.image.get_rect()
    self.rect.center = (x, y)
    self.speed = 1
    self.gravity = 3
    self.isJumping = False

    self.orientationLeft = self.image
    self.orientationRight = pygame.transform.flip(self.image, True, False)
  
  def draw(self):
    screen.blit(self.image, self.rect) # Places player on the screen

  def move(self, direction):
    if direction == 'left':
      self.image = self.orientationLeft
      self.rect.x -= self.speed
    if direction == 'right':
      self.image = self.orientationRight
      self.rect.x += self.speed
    


  def attack(self):
    pass # filler text

class platform(pygame.sprite.Sprite):
  def __init__(self, x, y, scale):
    img = pygame.image.load('imgs/world/ground.png')
    self.image = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
    self.rect = self.image.get_rect()
    self.rect.center = (x, y)
  def draw(self):
    screen.blit(self.image, self.rect)


def draw_background():
  # Draw the background image onto the screen
  background = pygame.image.load('imgs/world/background.jpg')
  background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
  screen.blit(background, (0, 0))

  # Create a line and draw on screen
  lineColor = (255, 0, 0)
  ground_line = pygame.draw.line(screen, lineColor, (0, SCREEN_HEIGHT * 0.95), (SCREEN_WIDTH, SCREEN_HEIGHT * 0.95))
  # Update the display


# Create the main player of the game
player = combatant(200,(SCREEN_HEIGHT * 0.89),scale)



# Main game loop
running = True
while running:
  for event in pygame.event.get():
    # Close game when exit button is pressed
    if event.type == pygame.QUIT:
      running = False
    
  draw_background()
  
  # Check for key presses
  keys = pygame.key.get_pressed()

  if keys[pygame.K_LEFT]:
      player.move('left')
  if keys[pygame.K_RIGHT]:
      player.move('right')
  if keys[pygame.K_UP]:
      player.move('jump')
  if keys[pygame.K_SPACE]:
      player.attack()
  player.draw()

  pygame.display.update()


pygame.quit()
import pygame

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * .8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Platformer")

scale = .5

# Create class that will be used for the player and enemies
class combatant(pygame.sprite.Sprite):
  def __init__(self, x, y, scale):
    pygame.sprite.Sprite.__init__(self) # Inherit properties from sprite class
    img = pygame.image.load('imgs/player/mainPlayer.png')
    self.image = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
    self.rect = self.image.get_rect()
    self.rect.center = (x, y)
    self.moveSpeed = 1

    self.orientationLeft = self.image
    self.orientationRight = pygame.transform.flip(self.image, True, False)
  
  def draw(self):
    screen.blit(self.image, self.rect) # Places player on the screen

  def move(self, direction):
    if direction == 'left':
      self.image = self.orientationLeft
    elif direction == 'right':
      self.image = self.orientationRight


  def attack(self):
    pass # filler text


class world:
  def __init__(self):
    pass # filler text

def draw_background():
  background = pygame.image.load('imgs/world/background.jpg')
  background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
  
  # Draw the background image onto the screen
  screen.blit(background, (0, 0))

# Create the main player of the game
player = combatant(200,200,scale)


# Main game loop
running = True
while running:
  draw_background()
  for event in pygame.event.get():
    # Close game when exit button is pressed
    if event.type == pygame.QUIT:
      running = False
    
  # Check for key presses
  keys = pygame.key.get_pressed()

  if keys[pygame.K_LEFT]:
      player.move('left')
  elif keys[pygame.K_RIGHT]:
      player.move('right')
  elif keys[pygame.K_UP]:
      player.move('jump')
  elif keys[pygame.K_SPACE]:
      player.attack()
    
  player.draw()
  
  pygame.display.update()


pygame.quit()
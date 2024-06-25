import pygame
import math

# Set screen dimensions
WIDTH = 800
HEIGHT = int(WIDTH * 0.8)

# Define a function to load and scale images
def load_image(path):
    return pygame.image.load(path)

# Initialize the video system
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Game Intro")

# Load and scale images
background_image = load_image('Platformer/imgs/startscreen/background.png')
game_logo = load_image("Platformer/imgs/startscreen/game_logo.png")
start_button = load_image("Platformer/imgs/startscreen/start_button.png")
options_button = load_image("Platformer/imgs/startscreen/options_button.png")
back_button = load_image("Platformer/imgs/startscreen/back_button.png")
brightness_button = load_image("Platformer/imgs/startscreen/brightness_button.png")
dim_button = load_image("Platformer/imgs/startscreen/dim_button.png")

# Set scaling factors for images
logo_reduction_factor = 0.04
scaled_logo_width = int(game_logo.get_width() * logo_reduction_factor)
scaled_logo_height = int(game_logo.get_height() * logo_reduction_factor)
logo_x = (WIDTH - scaled_logo_width) // 2
logo_y = 20

button_reduction_factor = 0.4
scaled_start_button_width = int(start_button.get_width() * button_reduction_factor)
scaled_start_button_height = int(start_button.get_height() * button_reduction_factor)
scaled_options_button_width = int(options_button.get_width() * button_reduction_factor)
scaled_options_button_height = int(options_button.get_height() * button_reduction_factor)

button_x_start = (WIDTH - (scaled_start_button_width + scaled_options_button_width + 45.5)) // 1
button_y = HEIGHT - scaled_start_button_height - 175

scaled_options_button_width *= 0.3
scaled_options_button_height *= 0.3
button_x_options = WIDTH - scaled_options_button_width - 5
button_y_options = HEIGHT - scaled_options_button_height - 5

back_button_reduction_factor = 0.3
scaled_back_button_width = int(back_button.get_width() * back_button_reduction_factor)
scaled_back_button_height = int(back_button.get_height() * back_button_reduction_factor)
button_x_back = 5
button_y_back = HEIGHT - scaled_back_button_height - 5

brightness_button_reduction_factor = 0.2
scaled_brightness_button_width = int(brightness_button.get_width() * brightness_button_reduction_factor)
scaled_brightness_button_height = int(brightness_button.get_height() * brightness_button_reduction_factor)

dim_button_reduction_factor = 0.12
scaled_dim_button_width = int(dim_button.get_width() * dim_button_reduction_factor)
scaled_dim_button_height = int(dim_button.get_height() * dim_button_reduction_factor)

# Center the brightness and dim buttons side by side
button_x_brightness = (WIDTH - scaled_brightness_button_width - scaled_dim_button_width - 10) // 2
button_x_dim = button_x_brightness + scaled_brightness_button_width + 10
button_y_brightness = HEIGHT - scaled_brightness_button_height - 200
button_y_dim = button_y_brightness

base_scroll_speed = 0.5
clock = pygame.time.Clock()

# Initialize the mixer module to play music in the background
pygame.mixer.init()
pygame.mixer.music.load('Platformer/music/background_music.mp3')
pygame.mixer.music.play(-1)

running = True
background_offset = 0
second_page_active = False
brightness_level = 1.0  # Initialize brightness level

# Function to adjust brightness
def apply_brightness(surface, level):
    print(level)
    if level > 1:
        brightness_surface = pygame.Surface(surface.get_size()).convert_alpha()
        brightness_surface.fill((255, 255, 255, int(255 * (level - 1))))
        surface.blit(brightness_surface, (0, 0))

# Define a function for the logo on the second page
def draw_second_page_logo():
    logo_path = 'Platformer\imgs\startscreen\your_logo.png' 
    logo_image = load_image(logo_path)
    logo_reduction_factor = 0.7
    scaled_logo_width = int(logo_image.get_width() * logo_reduction_factor)
    scaled_logo_height = int(logo_image.get_height() * logo_reduction_factor)
    logo_x = (WIDTH - scaled_logo_width) // 2
    logo_y = 50
    screen.blit(pygame.transform.scale(logo_image, (scaled_logo_width, scaled_logo_height)), (logo_x, logo_y))

    screen.blit(pygame.transform.scale(back_button, (scaled_back_button_width, scaled_back_button_height)), (button_x_back, button_y_back))
    screen.blit(pygame.transform.scale(brightness_button, (scaled_brightness_button_width, scaled_brightness_button_height)), (button_x_brightness, button_y_brightness))
    screen.blit(pygame.transform.scale(dim_button, (scaled_dim_button_width, scaled_dim_button_height)), (button_x_dim, button_y_dim))

def start_screen():
    global running, second_page_active, brightness_level, background_offset  # Declare global variables
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if not second_page_active:
                    if button_x_start <= mouse_pos[0] <= button_x_start + scaled_start_button_width and button_y <= mouse_pos[1] <= button_y + scaled_start_button_height:
                        print("Start Button Clicked!")
                        pygame.mixer.music.stop()
                        return True  # Start the game
                    elif button_x_options <= mouse_pos[0] <= button_x_options + scaled_options_button_width and button_y_options <= mouse_pos[1] <= button_y_options + scaled_options_button_height:
                        second_page_active = True
                elif second_page_active:
                    if button_x_back <= mouse_pos[0] <= button_x_back + scaled_back_button_width and button_y_back <= mouse_pos[1] <= button_y_back + scaled_back_button_height:
                        second_page_active = False
                        print("Back Button Clicked! Go back to the previous page")
                    elif button_x_brightness <= mouse_pos[0] <= button_x_brightness + scaled_brightness_button_width and button_y_brightness <= mouse_pos[1] <= button_y_brightness + scaled_brightness_button_height:
                        print("Brightness Button Clicked!")
                        brightness_level = min(1.2, brightness_level + 0.01)
                    elif button_x_dim <= mouse_pos[0] <= button_x_dim + scaled_dim_button_width and button_y_dim <= mouse_pos[1] <= button_y_dim + scaled_dim_button_height:
                        print("Dim Button Clicked!")
                        if max(0.0, brightness_level - 0.01) > 1:
                            brightness_level = max(0.0, brightness_level - 0.01)

        dt = clock.tick(60)

        scroll_speed = base_scroll_speed * (dt / 8)
        background_offset += scroll_speed
        background_offset %= background_image.get_width()

        num_tiles = int(math.ceil(WIDTH / background_image.get_width())) + 1

        background_surface = pygame.Surface((WIDTH, HEIGHT))

        for y in range(math.ceil(HEIGHT / background_image.get_height())):
            for i in range(num_tiles):
                background_surface.blit(background_image, (i * background_image.get_width() - background_offset, y * background_image.get_height()))

        screen.blit(background_surface, (0, 0))

        if not second_page_active:
            screen.blit(pygame.transform.scale(game_logo, (scaled_logo_width, scaled_logo_height)), (logo_x, logo_y))
            screen.blit(pygame.transform.scale(start_button, (scaled_start_button_width, scaled_start_button_height)), (button_x_start, button_y))
            screen.blit(pygame.transform.scale(options_button, (scaled_options_button_width, scaled_options_button_height)), (button_x_options, button_y_options))
        else:
            draw_second_page_logo()

        apply_brightness(screen, brightness_level)

        pygame.display.flip()
    pygame.mixer.music.stop()
    pygame.mixer.quit()
    return False

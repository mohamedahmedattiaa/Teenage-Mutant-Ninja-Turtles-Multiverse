import pygame
from player import Player  # Import the Player class from player.py

# Initialize
pygame.init()

# Set up the screen
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Meta venv \\ Miky Level")

# Load background and sprite images
bg_index = pygame.image.load('images/floor.jpg')
walk = pygame.image.load('images/walk.png').convert_alpha()
light_attack = pygame.image.load('images/LA.png').convert_alpha()
leg_attack = pygame.image.load('images/legAttack.png').convert_alpha()
ult_attack = pygame.image.load('images/ult.png').convert_alpha()  # Load ult attack sprite
shield = pygame.image.load('images/safe.png')  # Shield image (one frame)

# Create Player object
player = Player(100, 500, walk, light_attack, leg_attack, ult_attack, shield)


running = True
while running:
    screen.blit(bg_index, (0, 0))
    # Update and draw player
    player.update()
    player.draw(screen)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update the display
    pygame.display.update()

# Quit Pygame
pygame.quit()

import pygame
from player import Player
from sprits import Spritesheet

# Initialize Pygamed
pygame.init()

# Set up the screen
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Leo Level")

# Load background and sprite images
bg_index = pygame.image.load('images/background.png')
walk = pygame.image.load('images/main.png').convert_alpha()
light_attack = pygame.image.load('images/ult.png').convert_alpha()
Jump_attack = pygame.image.load('images/PowerfullLegAttack.png').convert_alpha()
ult_attack = pygame.image.load('images/TornadoAttack.png').convert_alpha()  # Load ult attack sprite
shield = pygame.image.load('images/Safe.png')  # Shield image (one frame)






# Create Player object
player = Player(100, 500, walk, light_attack, Jump_attack, ult_attack, shield)

# Game loop
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
import pygame
import os
from player import Player

# Initialize
pygame.init()
pygame.mixer.init()

# Screen setup
WIDTH, HEIGHT = 1200, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Leonardo Game")

# Load background
background = pygame.image.load('images/background.png')

# Load player animations
combo1 = pygame.image.load('images/combo1.png').convert_alpha()
damaging = pygame.image.load('images/damaging.png').convert_alpha()

# Create player
player = Player(100, 500)

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw
    screen.blit(background, (0, 0))
    player.update(1/60)  # example delta time
    player.draw(screen)

    pygame.display.flip()

pygame.quit()

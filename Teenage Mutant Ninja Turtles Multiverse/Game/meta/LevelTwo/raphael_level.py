import pygame
from player import Player  # Import the Player class from player.py
from enemy import Enemy, spawn_enemy  # Import Enemy class and spawn function

# Initialize Pygame
pygame.init()

# Set up the screen
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Meta venv \\ Raphael Level")

# Load background and sprite images
bg_index = pygame.image.load('images/bg1.jpg')
# Update sprite image paths to file paths
player_images = {
    "walk": 'images/walk.png',
    "light_attack": 'images/La.png',
    "leg_attack": 'images/legA.png',
    "ult_attack": 'images/ult.png',
    "shield": 'images/safe.png'
}

# Load enemy sprites
enemy_images = {
    "Ewalk": 'images/Ewalk.png',
    "Eatt": 'images/Eatt.png',
    "Edmg": 'images/Edmg.png',
    "Edead": 'images/Edead.png'
}

# Create Player object
player = Player(
    100, 500,
    player_images["walk"],
    player_images["light_attack"],
    player_images["leg_attack"],
    player_images["ult_attack"],
    player_images["shield"]
)

# Create list of enemies
enemy_list = []
enemy_list.append(spawn_enemy(1100, 500, player))  # First enemy

# Clock to control FPS
clock = pygame.time.Clock()

# Game loop
running = True
while running:
    clock.tick(60)  # 60 FPS
    screen.blit(bg_index, (0, 0))

    # Update and draw player
    player.update()
    player.draw(screen)

    # Update and draw enemies
    for enemy in enemy_list:
        enemy.update()
        enemy.draw(screen)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update the display
    pygame.display.update()

# Quit Pygame
pygame.quit()

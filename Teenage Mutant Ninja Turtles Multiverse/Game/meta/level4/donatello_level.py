import pgzrun
import pygame

WIDTH = 1280
HEIGHT = 720

don_frames = []
for i in range(1, 3):
    image = pygame.image.load(f"images/catch{i}.png").convert_alpha()
    don_frames.append(image)

fall_frames = []
for i in range(1, 3):
    image = pygame.image.load(f"images/die{i}.png").convert_alpha()
    fall_frames.append(image)

enemy_frames = []
for i in range(1, 17):
    image = pygame.image.load(f"images/Attack{i}.png").convert_alpha()
    enemy_frames.append(image)

background_image = pygame.image.load("images/world3.png").convert()
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
background_width = background_image.get_width()

x = 300
y = 300
frame_index = 0
frame_timer = 0
frame_speed = 0.15
animation_started = False
on_ground = True
facing_right = True
donatello_dead = False
fall_frame_index = 0

enemy_x = 600
enemy_y = 300
enemy_frame_index = 0
enemy_frame_timer = 0
enemy_speed = 2

speed = 5
jump_speed = 10
gravity = 0.5
y_velocity = 0
bottom_limit = y

background_offset = 0

def update():
    global frame_index, frame_timer, x, y, animation_started
    global y_velocity, on_ground, background_offset, facing_right
    global enemy_frame_index, enemy_frame_timer, enemy_x, enemy_speed
    global donatello_dead, fall_frame_index

    if donatello_dead:
        fall_frame_index += 1
        if fall_frame_index >= len(fall_frames):
            fall_frame_index = len(fall_frames) - 1
        return

    if animation_started:
        if keyboard.left or keyboard.right or keyboard.space:
            frame_timer += frame_speed
            if frame_timer >= 1:
                frame_timer = 0
                frame_index = (frame_index + 1) % len(don_frames)
        else:
            frame_index = 0

    if keyboard.right:
        background_offset -= speed
        facing_right = True
    elif keyboard.left:
        background_offset += speed
        facing_right = False

    if background_offset <= -background_width:
        background_offset = 0
    if background_offset >= background_width:
        background_offset = 0

    if keyboard.space and on_ground:
        y_velocity = -jump_speed
        on_ground = False

    if not on_ground:
        y_velocity += gravity
        y += y_velocity

    if y >= bottom_limit:
        y = bottom_limit
        y_velocity = 0
        on_ground = True

    enemy_frame_timer += frame_speed
    if enemy_frame_timer >= 1:
        enemy_frame_timer = 0
        enemy_frame_index = (enemy_frame_index + 1) % len(enemy_frames)

    if enemy_x > x:
        enemy_x -= enemy_speed
    elif enemy_x < x:
        enemy_x += enemy_speed

    if abs(enemy_x - x) < 50 and abs(enemy_y - y) < 50:
        donatello_dead = True
        print("دوناتيلو مات!")

def draw():
    screen.fill((0, 0, 0))

    screen.blit(background_image, (background_offset, 0))
    screen.blit(background_image, (background_offset + background_width, 0))
    screen.blit(background_image, (background_offset - background_width, 0))

    if not donatello_dead:
        current_frame = don_frames[frame_index]
        if facing_right:
            screen.blit(current_frame, (x, y))
        else:
            flipped = pygame.transform.flip(current_frame, True, False)
            screen.blit(flipped, (x, y))
    else:
        fall_frame = fall_frames[fall_frame_index]
        screen.blit(fall_frame, (x, y))

    enemy_frame = enemy_frames[enemy_frame_index]
    if enemy_x < x:
        screen.blit(enemy_frame, (enemy_x, enemy_y))
    else:
        flipped_enemy = pygame.transform.flip(enemy_frame, True, False)
        screen.blit(flipped_enemy, (enemy_x, enemy_y))

    if donatello_dead:
        screen.draw.text("Game Over", center=(WIDTH / 2, HEIGHT / 2), fontsize=80, color="red")

def on_key_down():
    global animation_started
    animation_started = True

def on_key_up():
    global animation_started
    animation_started = False

pgzrun.go()

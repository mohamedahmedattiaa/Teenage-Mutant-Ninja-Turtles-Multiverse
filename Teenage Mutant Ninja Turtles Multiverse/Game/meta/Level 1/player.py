import pygame
from sprits import Spritesheet

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite_image, attack_image, leg_attack_image, ult_image, shield_image):
        super().__init__()
        self.al = []  # Walk frames
        self.attack_frames = []  # Light attack frames
        self.leg_attack_frames = []  # Leg attack frames
        self.ult_frames = []  # Ult frames
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_cooldown = 150
        self.turtle_x = x
        self.turtle_y = y
        self.speed = 0.5  # Normal speed
        self.facing_right = True

        # Load sprite sheets
        sprite_sheet = Spritesheet(sprite_image)
        attack_sheet = Spritesheet(attack_image)
        leg_attack_sheet = Spritesheet(leg_attack_image)
        ult_sheet = Spritesheet(ult_image)
        shield_sheet = Spritesheet(shield_image)

        # Load walking frames (5 frames)
        for i in range(5):
            self.al.append(sprite_sheet.get_image(i, 54, 78, 2, (0, 0, 0)))

        # Load light attack frames (3 frames)
        for i in range(3):
            self.attack_frames.append(attack_sheet.get_image(i, 60, 74, 2, (0, 0, 0)))

        # Load leg attack frames (4 frames)
        for i in range(5):
            self.leg_attack_frames.append(leg_attack_sheet.get_image(i, 57, 114, 2, (0, 0, 0)))

        # Load ult frames (4 frames)
        for i in range(3):
            self.ult_frames.append(ult_sheet.get_image(i, 53, 100, 2, (0, 0, 0)))

        # Load shield image (only one frame, scaled by 2)
        self.shield_image = shield_sheet.get_image(0, 50, 87, 2, (0, 0, 0))

        self.image = self.al[self.frame]
        self.frame_width = self.image.get_width()

        self.is_attacking = False
        self.is_leg_attacking = False
        self.is_ulting = False
        self.is_shielding = False

    def update(self):
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()

        moving = False
        attacking = False
        leg_attacking = False
        ulting = False
        shielding = False

        # Movement controls
        move_speed = self.speed
        if mouse_buttons[2]:  # Right-click for shield
            shielding = True
            move_speed = 0.2  # Slower while shielding
        else:
            shielding = False

        if keys[pygame.K_d]:  # Right
            self.turtle_x += move_speed
            self.facing_right = True
            moving = True
            if self.turtle_x + self.frame_width > 1280:
                self.turtle_x = 1280 - self.frame_width

        if keys[pygame.K_a]:  # Left
            self.turtle_x -= move_speed
            self.facing_right = False
            moving = True
            if self.turtle_x < 0:
                self.turtle_x = 0

        if keys[pygame.K_w]:  # Up
            if self.turtle_y > 400:
                self.turtle_y -= move_speed
            moving = True

        if keys[pygame.K_s]:  # Down
            self.turtle_y += move_speed
            moving = True
            if self.turtle_y + self.image.get_height() > 720:
                self.turtle_y = 720 - self.image.get_height()

        # Light attack
        if mouse_buttons[0] and not keys[pygame.K_LSHIFT]:
            attacking = True

        # Leg attack (Shift + Left click)
        if keys[pygame.K_LSHIFT] and mouse_buttons[0]:
            leg_attacking = True

        # Ult (press E)
        if keys[pygame.K_e]:
            ulting = True

        self.is_attacking = attacking
        self.is_leg_attacking = leg_attacking
        self.is_ulting = ulting
        self.is_shielding = shielding

        # Animation logic
        current_time = pygame.time.get_ticks()

        if self.is_shielding:
            self.image = self.shield_image  # Just show shield image (static)
        elif self.is_ulting:
            if current_time - self.last_update >= self.animation_cooldown:
                self.frame += 1
                self.last_update = current_time
                if self.frame >= len(self.ult_frames):
                    self.frame = 0
            self.image = self.ult_frames[self.frame]
        elif self.is_leg_attacking:
            if current_time - self.last_update >= self.animation_cooldown:
                self.frame += 1
                self.last_update = current_time
                if self.frame >= len(self.leg_attack_frames):
                    self.frame = 0
            self.image = self.leg_attack_frames[self.frame]
        elif self.is_attacking:
            if current_time - self.last_update >= self.animation_cooldown:
                self.frame += 1
                self.last_update = current_time
                if self.frame >= len(self.attack_frames):
                    self.frame = 0
            self.image = self.attack_frames[self.frame]
        elif moving:
            if current_time - self.last_update >= self.animation_cooldown:
                self.frame += 1
                self.last_update = current_time
                if self.frame >= len(self.al):
                    self.frame = 0
            self.image = self.al[self.frame]
        else:
            self.frame = 0
            self.image = self.al[self.frame]

    def draw(self, surface):
        if self.facing_right:
            surface.blit(self.image, (self.turtle_x, self.turtle_y))
        else:
            flipped_image = pygame.transform.flip(self.image, True, False)
            flipped_image.set_colorkey((0, 0, 0))
            surface.blit(flipped_image, (self.turtle_x, self.turtle_y))

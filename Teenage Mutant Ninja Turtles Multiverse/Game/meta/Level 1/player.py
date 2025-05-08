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
        self.animation_cooldown = 80  # Reduced for faster animations
        self.turtle_x = x
        self.turtle_y = y
        self.speed = 0.5  # Normal speed
        self.facing_right = True

        # Flying - flight variables and properties
        self.is_flying = False
        self.fly_speed = 0.4  # Base flying speed
        self.max_fly_speed = 0.8  # Maximum flying speed
        self.min_fly_speed = 0.2  # Minimum flying speed
        self.fly_acceleration = 0.01  # Flying acceleration
        self.current_fly_speed = self.fly_speed  # Current flying speed
        self.gravity = 0.015  # Very low gravity as if in space
        self.vertical_velocity = 0  # Current vertical velocity
        self.max_altitude = 50  # Maximum flying altitude from ground

        # Jumping - jump variables and properties
        self.is_jumping = False
        self.jump_count = 0
        self.jump_cooldown = 500  # Time between jumps (milliseconds)
        self.last_jump_time = 0
        self.jump_power = 1.8  # Low jump power for space-like effect

        # Load sprite sheets
        sprite_sheet = Spritesheet(sprite_image)
        attack_sheet = Spritesheet(attack_image)
        leg_attack_sheet = Spritesheet(leg_attack_image)
        ult_sheet = Spritesheet(ult_image)
        shield_sheet = Spritesheet(shield_image)

        # Load walking frames (3 frames) - Fixed transparency
        for i in range(3):
            img = sprite_sheet.get_image(i, 283, 367, 0.75, (0, 0, 0))
            img = img.convert_alpha()  # Convert for alpha transparency
            self.al.append(img)

        # Load light attack frames (3 frames) - Fixed transparency
        for i in range(3):
            img = attack_sheet.get_image(i, 376, 378, 0.75, (0, 0, 0))
            img = img.convert_alpha()
            self.attack_frames.append(img)

        # Load leg attack frames (2 frames) - Fixed transparency
        for i in range(2):
            img = leg_attack_sheet.get_image(i, 400, 372, 0.75, (0, 0, 0))
            img = img.convert_alpha()
            self.leg_attack_frames.append(img)

        # Load ult frames (4 frames) - Fixed transparency
        for i in range(6):
            img = ult_sheet.get_image(i, 326, 361, 0.75, (0, 0, 0))
            img = img.convert_alpha()
            self.ult_frames.append(img)

        # Load shield image (only one frame, scaled by 2) - Fixed transparency
        self.shield_image = shield_sheet.get_image(0, 268, 362, 0.75, (0, 0, 0))
        self.shield_image = self.shield_image.convert_alpha()

        self.image = self.al[self.frame]
        self.frame_width = self.image.get_width()
        self.frame_height = self.image.get_height()

        # Set ground level based on screen height and character height
        self.ground_level = 720 - self.frame_height

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

        # Shield control
        if mouse_buttons[2]:  # Right-click for shield
            shielding = True
            move_speed = 0.2  # Slower while shielding
        else:
            move_speed = self.speed
            shielding = False

        # Flying control - Space key
        current_time = pygame.time.get_ticks()
        if keys[pygame.K_SPACE]:
            self.is_flying = True
            # Gradual acceleration when flying
            if self.current_fly_speed < self.max_fly_speed:
                self.current_fly_speed += self.fly_acceleration
        else:
            self.is_flying = False
            # Gradual deceleration when not flying
            if self.current_fly_speed > self.min_fly_speed:
                self.current_fly_speed -= self.fly_acceleration
            else:
                self.current_fly_speed = self.fly_speed

        # Horizontal movement control
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

        # Vertical movement control
        if self.is_flying:
            # Fly up
            if keys[pygame.K_w]:
                self.vertical_velocity = -self.current_fly_speed
                moving = True
            # Fly down
            elif keys[pygame.K_s]:
                self.vertical_velocity = self.current_fly_speed
                moving = True
            else:
                # Floating effect while flying without pressing any key
                # Slight floating effect as if in space
                self.vertical_velocity = self.vertical_velocity * 0.98  # Gradually reduce speed for floating
        else:
            # Apply very light gravity (space-like)
            self.vertical_velocity += self.gravity

            # Slow "space-like" jump
            if keys[pygame.K_w] and not self.is_jumping and current_time - self.last_jump_time > self.jump_cooldown:
                self.is_jumping = True
                self.vertical_velocity = -self.jump_power  # Low jump power
                self.last_jump_time = current_time
                moving = True

            # Add slow effect for movement in the air
            if self.is_jumping or self.turtle_y < self.ground_level:
                # Reduce horizontal movement speed in air for space-like effect
                if keys[pygame.K_a] or keys[pygame.K_d]:
                    move_speed = move_speed * 0.9

        # Apply vertical velocity to position (at a slower rate for space-like effect)
        self.turtle_y += self.vertical_velocity

        # Check for ground collision
        if self.turtle_y > self.ground_level:
            self.turtle_y = self.ground_level
            self.is_jumping = False
            # Slight bounce when touching ground (low gravity effect)
            if abs(self.vertical_velocity) > 0.5:
                self.vertical_velocity = -self.vertical_velocity * 0.3  # 30% bounce
            else:
                self.vertical_velocity = 0

        # Check for top screen boundary
        if self.turtle_y < 0:
            self.turtle_y = 0
            self.vertical_velocity = 0

        # Attack controls
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
        elif moving or self.is_flying or self.is_jumping:
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
        # Ensure transparency is properly set for the current image
        self.image.set_colorkey((0, 0, 0))

        if self.facing_right:
            surface.blit(self.image, (self.turtle_x, self.turtle_y))
        else:
            flipped_image = pygame.transform.flip(self.image, True, False)
            flipped_image.set_colorkey((0, 0, 0))
            surface.blit(flipped_image, (self.turtle_x, self.turtle_y))
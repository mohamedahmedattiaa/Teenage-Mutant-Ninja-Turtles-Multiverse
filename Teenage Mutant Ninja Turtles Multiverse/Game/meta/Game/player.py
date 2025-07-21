import pygame
from spritesheet import Spritesheet
from pygame import mixer

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite_image, attack_image, leg_attack_image, ult_image, shield_image, death_image):
        super().__init__()
        self.al = []
        self.attack_frames = []
        self.leg_attack_frames = []
        self.ult_frames = []
        self.death_frames = []

        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_cooldown = 150
        self.turtle_x = x
        self.turtle_y = y
        self.speed = 2
        self.facing_right = True
        self.health = 100
        self.max_health = 100
        self.stamina = 100
        self.max_stamina = 100

        # Sound initialization
        try:
            self.sword_sound = mixer.Sound("sounds2/sword.wav")
            self.damaged_sound = mixer.Sound("sounds2/damged.wav")
            self.killed_sound = mixer.Sound("sounds2/killed.mp3")
            self.sword_sound.set_volume(0.3)
            self.damaged_sound.set_volume(0.5)
            self.killed_sound.set_volume(0.5)
        except Exception as e:
            print(f"Error loading sounds: {e}")
            # Create dummy sound objects if loading fails
            self.sword_sound = mixer.Sound(buffer=bytearray(100))
            self.damaged_sound = mixer.Sound(buffer=bytearray(100))
            self.killed_sound = mixer.Sound(buffer=bytearray(100))

        sprite_sheet = Spritesheet(sprite_image)
        attack_sheet = Spritesheet(attack_image)
        leg_attack_sheet = Spritesheet(leg_attack_image)
        ult_sheet = Spritesheet(ult_image)
        shield_sheet = Spritesheet(shield_image)
        death_sheet = Spritesheet(death_image)

        for i in range(5):
            self.al.append(sprite_sheet.get_image(i, 70, 78, 2))

        for i in range(3):
            self.attack_frames.append(attack_sheet.get_image(i, 82, 74, 2))

        for i in range(4):
            self.leg_attack_frames.append(leg_attack_sheet.get_image(i, 85, 114, 2))

        for i in range(4):
            self.ult_frames.append(ult_sheet.get_image(i, 106, 100, 2))

        self.shield_image = shield_sheet.get_image(0, 160, 193, 2)

        for i in range(1):
            self.death_frames.append(death_sheet.get_image(i, 107, 80, 2))

        self.image = self.al[self.frame]
        self.frame_width = self.image.get_width()

        # States
        self.is_attacking = False
        self.is_leg_attacking = False
        self.is_ulting = False
        self.is_shielding = False
        self.is_dead = False
        self.death_finished = False

        # Damage flashing
        self.is_damaged = False
        self.damage_start_time = 0
        self.damage_flash_duration = 150

        self.invincible = False
        self.invincible_start_time = 0
        self.invincible_duration = 1000
        self.visible = True
        self.flash_interval = 150
        self.last_flash_time = 0

    def take_damage(self, amount):
        if self.is_dead or self.invincible:
            return

        if self.is_shielding and self.stamina > 0:
            stamina_loss = amount * 1.5  # adjust multiplier if you want
            self.stamina -= stamina_loss
            if self.stamina < 0:
                self.stamina = 0
                # Optional: shield broken effect here
            print(f"Shield blocked the attack. Stamina now {self.stamina}")
            # Damage absorbed, so no health lost
            return

        # Not shielding or no stamina → take health damage
        self.health -= amount
        print(f"Player took {amount} damage! Health now {self.health}")
        self.damaged_sound.play()
        self.is_damaged = True
        self.damage_start_time = pygame.time.get_ticks()
        self.invincible = True
        self.invincible_start_time = pygame.time.get_ticks()
        self.last_flash_time = pygame.time.get_ticks()
        self.visible = True

        if self.health <= 0:
            self.health = 0
            self.die()

    def die(self):
        print("Player died!")
        self.killed_sound.play()
        self.is_dead = True
        self.frame = 0
        self.last_update = pygame.time.get_ticks()

    def update(self):
        current_time = pygame.time.get_ticks()

        if self.invincible:
            if current_time - self.last_flash_time >= self.flash_interval:
                self.visible = not self.visible
                self.last_flash_time = current_time
            if current_time - self.invincible_start_time >= self.invincible_duration:
                self.invincible = False
                self.visible = True

        if self.is_dead:
            if not self.death_finished and current_time - self.last_update >= self.animation_cooldown:
                self.frame += 1
                self.last_update = current_time
                if self.frame >= len(self.death_frames):
                    self.frame = len(self.death_frames) - 1
                    self.death_finished = True
                self.image = self.death_frames[self.frame]
            self.rect = self.image.get_rect(topleft=(self.turtle_x, self.turtle_y))
            return

        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()

        moving = False
        move_speed = self.speed

        # Shield input, NO stamina drain just for holding shield
        if mouse_buttons[2] and self.stamina > 0:
            self.is_shielding = True
            move_speed = 0.2
        else:
            self.is_shielding = False
            # Recover stamina when not shielding
            self.stamina += 0.3
            if self.stamina > self.max_stamina:
                self.stamina = self.max_stamina

        # Movement
        if keys[pygame.K_d]:
            self.turtle_x += move_speed
            self.facing_right = True
            moving = True
            if self.turtle_x + self.frame_width > 1280:
                self.turtle_x = 1280 - self.frame_width

        if keys[pygame.K_a]:
            self.turtle_x -= move_speed
            self.facing_right = False
            moving = True
            if self.turtle_x < 0:
                self.turtle_x = 0

        if keys[pygame.K_w] and self.turtle_y > 400:
            self.turtle_y -= move_speed
            moving = True

        if keys[pygame.K_s] and self.turtle_y + self.image.get_height() < 720:
            self.turtle_y += move_speed
            moving = True

        # Play attack sounds when attacking starts
        if mouse_buttons[0] and not self.is_attacking and not keys[pygame.K_LSHIFT]:
            self.sword_sound.play()

        if keys[pygame.K_LSHIFT] and mouse_buttons[0] and not self.is_leg_attacking:
            self.sword_sound.play()

        self.is_attacking = mouse_buttons[0] and not keys[pygame.K_LSHIFT]
        self.is_leg_attacking = keys[pygame.K_LSHIFT] and mouse_buttons[0]
        self.is_ulting = keys[pygame.K_e]

        if current_time - self.last_update >= self.animation_cooldown:
            self.frame += 1
            self.last_update = current_time

            if self.is_shielding:
                self.frame = 0
                self.image = self.shield_image

            elif self.is_ulting:
                if self.frame >= len(self.ult_frames):
                    self.frame = 0
                self.image = self.ult_frames[self.frame]

            elif self.is_leg_attacking:
                if self.frame >= len(self.leg_attack_frames):
                    self.frame = 0
                self.image = self.leg_attack_frames[self.frame]

            elif self.is_attacking:
                if self.frame >= len(self.attack_frames):
                    self.frame = 0
                self.image = self.attack_frames[self.frame]

            elif moving:
                if self.frame >= len(self.al):
                    self.frame = 0
                self.image = self.al[self.frame]

            else:
                self.frame = 0
                self.image = self.al[self.frame]

        self.rect = self.image.get_rect(topleft=(self.turtle_x, self.turtle_y))

    def draw(self, surface):
        if not self.visible:
            return

        if self.health/self.max_health <= 0.4:
            tinted_image = self.image.copy()
            tinted_image.fill((255, 0, 0, 100), special_flags=pygame.BLEND_RGBA_MULT)
            image_to_draw = tinted_image
        else:
            image_to_draw = self.image

        if self.facing_right:
            surface.blit(image_to_draw, (self.turtle_x, self.turtle_y))
        else:
            flipped_image = pygame.transform.flip(image_to_draw, True, False)
            surface.blit(flipped_image, (self.turtle_x, self.turtle_y))
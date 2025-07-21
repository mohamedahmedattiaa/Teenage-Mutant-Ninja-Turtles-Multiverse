import pygame
import random
import math

try:
    from sprits import Spritesheet
except ImportError as e:
    print(f"Error importing Spritesheet: {e}. Using single-frame images instead.")
    Spritesheet = None


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, walk_image, attack_image, damage_image, dead_image, idle_image, player):
        super().__init__()
        self.walk_frames = []
        self.attack_frames = []
        self.damage_frames = []
        self.dead_frames = []
        self.idle_frames = []
        self.using_fallback = False

        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_cooldown = 100

        self.x = x
        self.y = 500
        self.speed = 3.5
        self.health = 150
        self.max_health = self.health
        self.dead = False
        self.finished_dying = False
        self.facing_right = False
        self.attacking = False
        self.was_attacking = False
        self.player = player
        self.attack_range = 100
        self.attack_damage = 0.5
        self.last_attack_time = 0
        self.attack_cooldown = 400

        self.is_damaged = False
        self.damage_start_time = 0
        self.damage_duration = 600
        self.invincible = False
        self.invincible_start_time = 0
        self.invincible_duration = 200
        self.visible = True
        self.flash_interval = 150
        self.last_flash_time = 0
        self.idle_after_block = False
        self.idle_start_time = 0
        self.idle_duration = 800
        self.holding_last_idle_frame = False
        self.last_idle_frame_hold_time = 0
        self.idle_freeze_duration = 1000

        def scale_image(image):
            try:
                return pygame.transform.scale(image, (image.get_width() * 2, image.get_height() * 2))
            except Exception as e:
                print(f"Error scaling image: {e}")
                return image

        if Spritesheet:
            try:
                walk_sheet = Spritesheet(walk_image)
                attack_sheet = Spritesheet(attack_image)
                damage_sheet = Spritesheet(damage_image)
                dead_sheet = Spritesheet(dead_image)
                idle_sheet = Spritesheet(idle_image)

                for i in range(4):
                    img = walk_sheet.get_image(i, 70, 88, 4)
                    self.walk_frames.append(img)

                for i in range(5):
                    img = attack_sheet.get_image(i, 90, 84, 4)
                    self.attack_frames.append(img)

                for i in range(2):
                    img = damage_sheet.get_image(i, 73, 90, 4)
                    self.damage_frames.append(img)

                for i in range(1):
                    img = dead_sheet.get_image(i, 129, 60, 4)
                    self.dead_frames.append(img)

                for i in range(4):
                    img = idle_sheet.get_image(i, 79, 79, 4)
                    self.idle_frames.append(img)

                if not all([self.walk_frames, self.attack_frames, self.damage_frames, self.dead_frames, self.idle_frames]):
                    raise Exception("Failed to load one or more frame sets")

            except Exception as e:
                print(f"Critical: All sprite loading failed: {e}. Falling back to single-frame images.")
                self.using_fallback = True

        if not self.walk_frames or self.using_fallback:
            print("Using single-frame images for enemy animations.")
            self.using_fallback = True
            try:
                self.walk_frames = [scale_image(walk_image)]
                self.attack_frames = [scale_image(attack_image)]
                self.damage_frames = [scale_image(damage_image)]
                self.dead_frames = [scale_image(dead_image)]
                self.idle_frames = [scale_image(idle_image)]
            except Exception as e:
                print(f"Critical: Failed to load single-frame images: {e}. Using fallback sprites.")
                self.using_fallback = True
                placeholder = pygame.Surface((100, 100), pygame.SRCALPHA)
                placeholder.fill((255, 0, 0, 200))
                font = pygame.font.SysFont('Arial', 16)
                text = font.render("Enemy Fallback", True, (255, 255, 255))
                placeholder.blit(text, (10, 40))
                self.walk_frames = [placeholder]
                self.attack_frames = [placeholder]
                self.damage_frames = [placeholder]
                self.dead_frames = [placeholder]
                self.idle_frames = [placeholder]

        self.image = self.walk_frames[0]
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.mask = pygame.mask.from_surface(self.image)

    def take_damage(self, amount):
        if self.dead or self.invincible:
            return
        self.health -= amount
        self.is_damaged = True
        self.damage_start_time = pygame.time.get_ticks()
        self.frame = 0
        self.invincible = True
        self.invincible_start_time = pygame.time.get_ticks()
        self.visible = True
        if self.health <= 0:
            self.health = 0
            self.die()

    def die(self):
        self.dead = True
        self.frame = 0
        self.last_update = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()

        if self.invincible:
            if now - self.last_flash_time >= self.flash_interval:
                self.last_flash_time = now
                self.visible = not self.visible
            if now - self.invincible_start_time >= self.invincible_duration:
                self.invincible = False
                self.visible = True
        else:
            self.visible = True

        if self.is_damaged:
            if now - self.last_update >= self.animation_cooldown:
                self.last_update = now
                self.frame += 1
                if self.frame >= len(self.damage_frames):
                    self.frame = 0
                self.image = self.damage_frames[self.frame]
            if now - self.damage_start_time >= self.damage_duration:
                self.is_damaged = False
                self.frame = 0
            self.rect.topleft = (self.x, self.y)
            self.mask = pygame.mask.from_surface(self.image)
            return

        if self.dead:
            if not self.finished_dying and now - self.last_update >= self.animation_cooldown:
                self.last_update = now
                self.frame += 1
                if self.frame >= len(self.dead_frames):
                    self.finished_dying = True
                    self.frame = len(self.dead_frames) - 1
                self.image = self.dead_frames[self.frame]
            self.rect.topleft = (self.x, self.y)
            self.mask = pygame.mask.from_surface(self.image)
            return

        if self.idle_after_block:
            if now - self.idle_start_time >= self.idle_duration:
                self.idle_after_block = False
                self.frame = 0
                self.holding_last_idle_frame = False
            else:
                if self.holding_last_idle_frame:
                    if now - self.last_idle_frame_hold_time >= self.idle_freeze_duration:
                        self.holding_last_idle_frame = False
                        self.frame = 0
                elif now - self.last_update >= self.animation_cooldown:
                    self.last_update = now
                    self.frame += 1
                    if self.frame >= len(self.idle_frames):
                        self.frame = len(self.idle_frames) - 1
                        self.holding_last_idle_frame = True
                        self.last_idle_frame_hold_time = now
                    self.image = self.idle_frames[self.frame]
                self.rect.topleft = (self.x, self.y)
                self.mask = pygame.mask.from_surface(self.image)
                return

        dx = self.player.rect.centerx - self.rect.centerx
        distance = abs(dx)
        self.facing_right = dx > 0

        was_attacking = self.attacking
        self.attacking = distance <= self.attack_range

        if self.attacking:
            if not was_attacking:
                self.frame = 0
                self.last_update = now

            if self.frame == 0 and now - self.last_attack_time > self.attack_cooldown:
                lunge_speed = 2.0
                self.x += (1 if self.facing_right else -1) * lunge_speed
                if not self.player.is_shielding:
                    self.player.health -= self.attack_damage
                else:
                    self.idle_after_block = True
                    self.idle_start_time = now
                    self.frame = 0
                    self.holding_last_idle_frame = False
                self.last_attack_time = now

            if now - self.last_update >= self.animation_cooldown:
                self.last_update = now
                self.frame += 1
                if self.frame >= len(self.attack_frames):
                    self.frame = 0
                self.image = self.attack_frames[self.frame]

        else:
            if distance > self.attack_range + 10:
                direction_x = dx / distance if distance != 0 else 0
                self.x += direction_x * self.speed

            if now - self.last_update >= self.animation_cooldown:
                self.last_update = now
                self.frame += 1
                if self.frame >= len(self.walk_frames):
                    self.frame = 0
                self.image = self.walk_frames[self.frame]

        self.was_attacking = self.attacking
        self.rect.topleft = (self.x, self.y)
        self.rect.clamp_ip(pygame.Rect(0, 0, 1280, 720))
        self.x = self.rect.left
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, surface):
        if self.visible:
            try:
                img = self.image
                if not self.facing_right:
                    img = pygame.transform.flip(self.image, True, False)
                surface.blit(img, self.rect)
            except Exception as e:
                print(f"Error drawing enemy: {e}")
                pygame.draw.rect(surface, (255, 0, 0), self.rect)

    def draw_clean(self, surface):
        if self.visible:
            try:
                img = pygame.transform.flip(self.image, not self.facing_right, False)
                surface.blit(img, self.rect)
                pygame.draw.circle(surface, (255, 0, 0), self.rect.center, self.attack_range, 1)
            except Exception as e:
                print(f"Error in draw_clean: {e}")
                pygame.draw.rect(surface, (255, 0, 0), self.rect)

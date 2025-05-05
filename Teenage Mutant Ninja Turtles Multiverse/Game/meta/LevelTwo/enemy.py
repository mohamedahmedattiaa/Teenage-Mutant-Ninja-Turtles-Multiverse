import pygame
from spritesheet import Spritesheet

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, walk_image, attack_image, damage_image, dead_image, player):
        super().__init__()
        self.walk_frames = []
        self.attack_frames = []
        self.damage_frames = []
        self.dead_frames = []
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.cooldown = 150

        self.x = x
        self.y = y
        self.speed = 1.5
        self.health = 100
        self.facing_right = False
        self.attacking = False
        self.player = player
        self.attack_range = 50
        self.attack_damage = 0.2

        # Load sprite sheets
        walk_sheet = Spritesheet(walk_image)
        attack_sheet = Spritesheet(attack_image)
        damage_sheet = Spritesheet(damage_image)
        dead_sheet = Spritesheet(dead_image)

        # Load frames (with transparency preserved)
        for i in range(3):
            self.walk_frames.append(walk_sheet.get_image(i, 79, 78, 2, None))
        for i in range(4):
            self.attack_frames.append(attack_sheet.get_image(i, 85, 80, 2, None))
        for i in range(2):
            self.damage_frames.append(damage_sheet.get_image(i, 76, 74, 2, None))
        for i in range(3):
            self.dead_frames.append(dead_sheet.get_image(i, 76, 74, 2, None))

        self.image = self.walk_frames[self.frame]
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def update(self):
        now = pygame.time.get_ticks()
        player_rect = pygame.Rect(self.player.turtle_x, self.player.turtle_y,
                                  self.player.image.get_width(), self.player.image.get_height())

        # Face the player
        self.facing_right = self.player.turtle_x > self.x

        # Calculate distance
        dx = self.player.turtle_x - self.x
        dy = self.player.turtle_y - self.y
        distance = (dx**2 + dy**2)**0.5

        if distance > self.attack_range:
            self.attacking = False
            # Normalize direction
            direction_x = dx / distance if distance != 0 else 0
            direction_y = dy / distance if distance != 0 else 0
            self.x += direction_x * self.speed
            self.y += direction_y * self.speed
        else:
            self.attacking = True
            self.player.turtle_x -= self.attack_damage  # Damage logic

        # Animation update
        if now - self.last_update >= self.cooldown:
            self.last_update = now
            self.frame += 1

            if self.attacking:
                if self.frame >= len(self.attack_frames):
                    self.frame = 0
                self.image = self.attack_frames[self.frame]
            else:
                if self.frame >= len(self.walk_frames):
                    self.frame = 0
                self.image = self.walk_frames[self.frame]

        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        if self.facing_right:
            surface.blit(self.image, (self.x, self.y))
        else:
            flipped_image = pygame.transform.flip(self.image, True, False)
            surface.blit(flipped_image, (self.x, self.y))

def spawn_enemy(x, y, player):
    return Enemy(
        x, y,
        'images/Ewalk.png',
        'images/Eatt.png',
        'images/Edmg.png',
        'images/Edead.png',
        player
    )

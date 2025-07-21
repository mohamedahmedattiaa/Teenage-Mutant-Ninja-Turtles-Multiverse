import pygame
from spritesheet import Spritesheet

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, walk_image, attack_image, damage_image, dead_image, idle_image, player, strong=False):
        super().__init__()
        self.walk_frames = []
        self.attack_frames = []
        self.damage_frames = []
        self.dead_frames = []
        self.idle_frames = []
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.cooldown = 150

        self.x = x
        self.y = y
        self.speed = 1.5
        self.health = 100
        self.dead = False
        self.finished_dying = False
        self.facing_right = False
        self.attacking = False
        self.player = player
        self.attack_range = 50
        self.attack_damage = 5
        self.attack_cooldown = 1000  # ms
        self.extended_cooldown = 0
        self.last_attack_time = 0

        self.idle_after_block = False
        self.idle_start_time = 0
        self.idle_duration = 800

        self.last_idle_frame_hold_time = 0
        self.idle_freeze_duration = 1000
        self.holding_last_idle_frame = False

        self.is_damaged = False
        self.damage_start_time = 0
        self.damage_duration = 300

        self.invincible = False
        self.invincible_start_time = 0
        self.invincible_duration = 200

        self.visible = True
        self.flash_interval = 150
        self.last_flash_time = 0

        # --- Strong Enemy Enhancements ---
        if strong:
            self.health = 150
            self.attack_damage = 10
            self.attack_cooldown = 500
            self.scale_multiplier = 1.4
        else:
            self.scale_multiplier = 1.0

        # Add max_health attribute for health ratio calculations
        self.max_health = self.health

        # Load sprites
        walk_sheet = Spritesheet(walk_image)
        attack_sheet = Spritesheet(attack_image)
        damage_sheet = Spritesheet(damage_image)
        dead_sheet = Spritesheet(dead_image)
        idle_sheet = Spritesheet(idle_image)

        for i in range(3):
            self.walk_frames.append(self.scale_image(walk_sheet.get_image(i, 79, 80, 2, None)))
        for i in range(4):
            self.attack_frames.append(self.scale_image(attack_sheet.get_image(i, 85, 80, 2, None)))
        for i in range(2):
            self.damage_frames.append(self.scale_image(damage_sheet.get_image(i, 80, 85, 2, None)))
        for i in range(2):
            self.dead_frames.append(self.scale_image(dead_sheet.get_image(i, 106, 68, 2, None)))
        for i in range(4):
            self.idle_frames.append(self.scale_image(idle_sheet.get_image(i, 79, 78, 2, None)))

        self.image = self.walk_frames[self.frame]
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def scale_image(self, image):
        width = int(image.get_width() * self.scale_multiplier)
        height = int(image.get_height() * self.scale_multiplier)
        return pygame.transform.scale(image, (width, height))

    def take_damage(self, amount):
        if self.dead or self.invincible:
            return
        self.health -= amount
        print(f"Enemy takes {amount} damage, health now {self.health}")
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
        print("Enemy died!")
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
            if now - self.last_update >= self.cooldown:
                self.last_update = now
                self.frame += 1
                if self.frame >= len(self.damage_frames):
                    self.frame = len(self.damage_frames) - 1
                self.image = self.damage_frames[self.frame]
            if now - self.damage_start_time >= self.damage_duration:
                self.is_damaged = False
                self.frame = 0
            self.rect.topleft = (self.x, self.y)
            return

        if self.dead:
            if not self.finished_dying and now - self.last_update >= self.cooldown:
                self.last_update = now
                self.frame += 1
                if self.frame >= len(self.dead_frames):
                    self.finished_dying = True
                    self.frame = len(self.dead_frames) - 1
                self.image = self.dead_frames[self.frame]
            self.rect.topleft = (self.x, self.y)
            return

        if self.player.is_dead:
            self.attacking = False
            self.x -= self.speed
            self.rect.topleft = (self.x, self.y)
            return

        dx = self.player.turtle_x - self.x
        dy = self.player.turtle_y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        self.facing_right = dx > 0

        if self.idle_after_block:
            if now - self.idle_start_time >= self.idle_duration:
                self.idle_after_block = False
                self.extended_cooldown = 0
                self.frame = 0
                self.holding_last_idle_frame = False
            else:
                if self.holding_last_idle_frame:
                    if now - self.last_idle_frame_hold_time >= self.idle_freeze_duration:
                        self.holding_last_idle_frame = False
                        self.frame = 0
                elif now - self.last_update >= self.cooldown:
                    self.last_update = now
                    self.frame += 1
                    if self.frame >= len(self.idle_frames):
                        self.frame = len(self.idle_frames) - 1
                        self.holding_last_idle_frame = True
                        self.last_idle_frame_hold_time = now
                    self.image = self.idle_frames[self.frame]
                self.rect.topleft = (self.x, self.y)
                return

        if distance > self.attack_range:
            self.attacking = False
            direction_x = dx / distance if distance != 0 else 0
            direction_y = dy / distance if distance != 0 else 0
            self.x += direction_x * self.speed
            self.y += direction_y * self.speed
        else:
            self.attacking = True
            if now - self.last_attack_time >= (self.attack_cooldown + self.extended_cooldown):
                self.last_attack_time = now
                if hasattr(self.player, 'take_damage'):
                    if not self.player.is_shielding:
                        self.extended_cooldown = 0
                        self.player.take_damage(self.attack_damage)
                    else:
                        print("Player shielded the attack!")
                        self.extended_cooldown = 1500
                        self.idle_after_block = True
                        self.idle_start_time = now
                        self.frame = 0
                        self.holding_last_idle_frame = False

        if now - self.last_update >= self.cooldown and not self.idle_after_block:
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
        if self.visible:
            img = self.image
            if not self.facing_right:
                img = pygame.transform.flip(self.image, True, False)
            surface.blit(img, (self.x, self.y))

    # New method: check if hit by player attack hitbox and take damage
    def check_hit(self, attack_rect, damage_amount):
        if self.dead:
            return
        if self.rect.colliderect(attack_rect):
            self.take_damage(damage_amount)


def spawn_enemy(x, y, player, strong=False):
    return Enemy(
        x, y,
        'images2/Ewalk.png',
        'images2/Eatt.png',
        'images2/Edmg.png',
        'images2/Edead.png',
        'images2/Eidle.png',
        player,
        strong
    )


def spawn_enemies(stage, player):
    enemies.empty()
    if stage == 0:
        enemy = spawn_enemy(400, 300, player, strong=False)
        enemies.add(enemy)
    elif stage == 1:
        enemy1 = spawn_enemy(350, 300, player, strong=False)
        enemy2 = spawn_enemy(450, 300, player, strong=False)
        enemies.add(enemy1, enemy2)
    elif stage == 2:
        big_enemy = spawn_enemy(400, 300, player, strong=True)
        enemies.add(big_enemy)



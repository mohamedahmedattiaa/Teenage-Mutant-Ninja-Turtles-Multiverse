import pygame
import os
import random
import sys
import math
from pygame.locals import *
from alien import Enemy
from space_turtle_player import SpaceTurtlePlayer


class Mars:
    def __init__(self):
        pygame.init()
        pygame.display.set_mode((1280, 720), pygame.DOUBLEBUF | pygame.HWSURFACE)
        pygame.mixer.init()
        self.level_completed = False
        # Screen setup
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("Mars Adventure")
        self.clock = pygame.time.Clock()
        self.running = True

        # Physics
        self.gravity = 0.38  # Mars gravity (38% of Earth's)

        # Load assets
        self.background = self.load_background()
        self.player = self.create_player()
        self.enemy = self.create_enemy()

        # Environment effects
        self.dust_particles = self.create_dust_particles(200)
        self.font = pygame.font.SysFont('Arial', 24, bold=True)

        # Game state
        self.game_over = False
        self.victory = False
        self.victory_message_shown = False
        self.exit_reason = "normal"  # Track the reason for exiting the level

        # Pause menu
        self.paused = False
        self.sound_on = True
        self.font_large = pygame.font.SysFont('Arial', 48)
        self.font_medium = pygame.font.SysFont('Arial', 36)
        self.font_small = pygame.font.SysFont('Arial', 24)

        # Sound effects
        self.load_sounds()

        # Debug
        self.debug_mode = False
        self.fps_font = pygame.font.SysFont('Arial', 20)

    def load_background(self):
        try:
            bg = pygame.image.load(os.path.join('images', 'Mars_background.png')).convert()
            return pygame.transform.scale(bg, (1280, 720))
        except Exception as e:
            print(f"Error loading background: {e}")
            bg = pygame.Surface((1280, 720))
            for y in range(720):
                color = (
                    int(150 * (1 - y / 1440)),
                    int(70 * (1 - y / 1440)),
                    int(40 * (1 - y / 1440))
                )
                pygame.draw.line(bg, color, (0, y), (1280, y))
            return bg

    def create_player(self):
        try:
            class SimpleAssetLoader:
                def __init__(self, mars_instance):
                    self.mars_instance = mars_instance
                    self.sprites = {}

                def load_sprites(self):
                    self.sprites['walk'] = self.mars_instance.load_image('main.png')
                    self.sprites['light_attack'] = self.mars_instance.load_image('ult.png')
                    self.sprites['jump_attack'] = self.mars_instance.load_image('LegAttack.png')
                    self.sprites['ult_attack'] = self.mars_instance.load_image('TornadoAttack.png')
                    self.sprites['shield'] = self.mars_instance.load_image('Safe.png')
                    try:
                        self.sprites['helmet'] = self.mars_instance.load_image('helmet.png')
                    except:
                        helmet = pygame.Surface((300, 300), pygame.SRCALPHA)
                        glass_color = (173, 216, 230, 180)
                        frame_color = (200, 200, 200, 255)
                        pygame.draw.circle(helmet, frame_color, (150, 150), 120, 20)
                        pygame.draw.circle(helmet, glass_color, (150, 150), 100)
                        pygame.draw.rect(helmet, frame_color, (145, 240, 10, 30))
                        pygame.draw.circle(helmet, frame_color, (150, 270), 15)
                        pygame.draw.arc(helmet, (255, 255, 255, 100), (70, 70, 160, 160), 0.7, 2.5, 5)
                        self.sprites['helmet'] = helmet

                def get_sprite(self, name):
                    return self.sprites.get(name)

            asset_loader = SimpleAssetLoader(self)
            asset_loader.load_sprites()

            player = SpaceTurtlePlayer(
                100, 500,
                asset_loader.get_sprite('walk'),
                asset_loader.get_sprite('light_attack'),
                asset_loader.get_sprite('jump_attack'),
                asset_loader.get_sprite('ult_attack'),
                asset_loader.get_sprite('shield'),
                asset_loader.get_sprite('helmet')
            )
            player.gravity = self.gravity
            player.reset_to_ground()
            return player
        except Exception as e:
            print(f"Error loading player sprites: {e}")
            fallback = pygame.Surface((80, 100), pygame.SRCALPHA)
            fallback.fill((0, 255, 0, 200))
            player = SpaceTurtlePlayer(
                100, 500,
                fallback, fallback, fallback, fallback, fallback, fallback
            )
            player.gravity = self.gravity
            player.reset_to_ground()
            return player

    def create_enemy(self):
        try:
            images = {
                'move': self.load_image('alien_move.png'),
                'attack': self.load_image('alien_attack.png'),
                'damage': self.load_image('alien_damge.png'),
                'died': self.load_image('alien_dead.png'),
                'idle': self.load_image('alien_idle.png')
            }
            for key, img in images.items():
                if img is None or not isinstance(img, pygame.Surface):
                    raise ValueError(f"Failed to load image for {key}")
            print("All enemy images loaded successfully")
            enemy = Enemy(
                800, 500,
                images['move'],
                images['attack'],
                images['damage'],
                images['died'],
                images['idle'],
                self.player
            )
            print("Enemy created successfully")
            return enemy
        except Exception as e:
            print(f"Error creating enemy: {e}")
            surf = pygame.Surface((60, 60), pygame.SRCALPHA)
            surf.fill((255, 0, 0, 200))
            print("Using fallback enemy sprite")
            return Enemy(
                800, 500,
                surf, surf, surf, surf, surf, self.player
            )

    def load_image(self, filename):
        try:
            path = os.path.join('images', filename)
            if not os.path.exists(path):
                raise FileNotFoundError(f"Image not found: {path}")
            image = pygame.image.load(path).convert_alpha()
            print(f"Successfully loaded: {filename}")
            return image
        except Exception as e:
            print(f"Error loading image {filename}: {e}")
            surf = pygame.Surface((100, 100), pygame.SRCALPHA)
            color = (
                random.randint(50, 255),
                random.randint(50, 255),
                random.randint(50, 255),
                200
            )
            surf.fill(color)
            pygame.draw.rect(surf, (255, 255, 255), (0, 0, 100, 100), 2)
            font = pygame.font.SysFont('Arial', 16)
            text = font.render(filename.split('.')[0], True, (255, 255, 255))
            surf.blit(text, (10, 40))
            return surf

    def load_sounds(self):
        self.sounds = {}
        sound_dir = os.path.join('sounds', 'sounds')
        try:
            self.sounds['collect'] = pygame.mixer.Sound(os.path.join(sound_dir, 'collect.mp3'))
            self.sounds['damaged'] = pygame.mixer.Sound(os.path.join(sound_dir, 'damged.wav'))
            self.sounds['fight'] = pygame.mixer.Sound(os.path.join(sound_dir, 'fight_sound.mp3'))
            self.sounds['game_over'] = pygame.mixer.Sound(os.path.join(sound_dir, 'game_over.mp3'))
            self.sounds['intro'] = pygame.mixer.Sound(os.path.join(sound_dir, 'intro.mp3'))
            self.sounds['killed'] = pygame.mixer.Sound(os.path.join(sound_dir, 'killed.mp3'))
            self.sounds['launch_rocket'] = pygame.mixer.Sound(os.path.join(sound_dir, 'lunch_rocket.mp3'))
            self.sounds['open_sword'] = pygame.mixer.Sound(os.path.join(sound_dir, 'open_sword.mp3'))
            self.sounds['sword'] = pygame.mixer.Sound(os.path.join(sound_dir, 'sword.wav'))
            for sound in self.sounds.values():
                sound.set_volume(0.7)
            print("Successfully loaded all sound effects")
        except Exception as e:
            print(f"Error loading sounds: {e}")
            self.sounds = {
                'collect': None, 'damaged': None, 'fight': None, 'game_over': None,
                'intro': None, 'killed': None, 'launch_rocket': None, 'open_sword': None, 'sword': None
            }

    def create_dust_particles(self, count):
        particles = []
        for _ in range(count):
            particles.append([
                random.randint(0, 1280),
                random.randint(0, 720),
                random.uniform(0.5, 3.0),
                random.uniform(0.1, 0.5),
                random.uniform(0, 360)
            ])
        return particles

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.exit_reason = "quit"  # Player closed the window
                self.running = False
            elif event.type == KEYDOWN:
                if event.key == K_h:
                    self.player.toggle_helmet()
                elif event.key == K_s:
                    self.player.toggle_space_suit()
                elif event.key == K_ESCAPE:
                    self.paused = not self.paused  # Toggle pause state
                elif event.key == K_F1:
                    self.debug_mode = not self.debug_mode

            # Handle pause menu interactions
            if self.paused and event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                sound_button, exit_button = self.draw_pause_menu()

                if sound_button.collidepoint(mouse_pos):
                    self.sound_on = not self.sound_on
                    # Toggle sound
                    for sound in self.sounds.values():
                        if sound:
                            sound.set_volume(0.7 if self.sound_on else 0.0)

                if exit_button.collidepoint(mouse_pos):
                    self.exit_reason = "exit_to_main"  # Player clicked exit button in pause menu
                    self.running = False

    def update(self):
        if self.game_over:
            self.exit_reason = "game_over"  # Set exit reason to game_over
            self.level_completed = False  # Player lost, return to Leonardo level
            self.running = False
            return

        if self.victory:
            if not self.victory_message_shown:
                self.show_victory_message()
                self.victory_message_shown = True
                self.level_completed = True  # Player won, return to main menu
                self.exit_reason = "victory"  # Player won the level
                self.running = False
            return

        # Skip updates if game is paused
        if self.paused:
            return

        self.player.update()
        if hasattr(self, 'enemy') and self.enemy:
            self.enemy.update()
            if pygame.sprite.collide_mask(self.player, self.enemy):
                if self.player.is_attacking or self.player.is_leg_attacking:
                    self.enemy.take_damage(15)
                    if self.sounds['sword']:
                        self.sounds['sword'].play()
                elif not self.player.is_shielding:
                    self.player.health -= 0.5
                    if self.sounds['damaged']:
                        self.sounds['damaged'].play()
                if self.enemy.health <= 0:
                    self.victory = True
                    if self.sounds['killed']:
                        self.sounds['killed'].play()
                if self.player.health <= 0:
                    self.game_over = True
                    if self.sounds['game_over']:
                        self.sounds['game_over'].play()
            # Rest of the existing particle updates...
            for p in self.dust_particles:
                p[0] += p[3] * 0.5
                p[1] += p[3] * 0.2
                p[4] += random.uniform(-2, 2)
                if p[0] > 1280 + 50:
                    p[0] = -50
                if p[0] < -50:
                    p[0] = 1280 + 50
                if p[1] > 720 + 50:
                    p[1] = -50
                if p[1] < -50:
                    p[1] = 720 + 50

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.background, (0, 0))
        for p in self.dust_particles:
            pygame.draw.circle(self.screen, (193, 154, 107, 100), (int(p[0]), int(p[1])), int(p[2]))
        self.player.draw_clean(self.screen)
        if hasattr(self, 'enemy') and self.enemy:
            self.enemy.draw_clean(self.screen)
        self.draw_ui()

        # Draw pause menu if game is paused
        if self.paused:
            self.draw_pause_menu()

        pygame.display.flip()

    def draw_ui(self):
        status_bar_width = 1000
        status_bar_height = 30
        status_bar_x = (1280 - status_bar_width) // 2
        status_bar_y = 20
        pygame.draw.rect(self.screen, (50, 50, 50), (status_bar_x, status_bar_y, status_bar_width, status_bar_height))
        pygame.draw.rect(self.screen, (200, 200, 200), (status_bar_x, status_bar_y, status_bar_width, status_bar_height), 2)
        boss_fight_mode = hasattr(self, 'enemy') and self.enemy and self.enemy.health > 0
        if boss_fight_mode:
            player_health_width = int((status_bar_width * 0.45) * (self.player.health / self.player.max_health))
            pygame.draw.rect(self.screen, (0, 200, 0), (status_bar_x, status_bar_y, player_health_width, status_bar_height))
            enemy_health_width = int((status_bar_width * 0.45) * (self.enemy.health / self.enemy.max_health))
            pygame.draw.rect(self.screen, (200, 0, 0),
                            (status_bar_x + status_bar_width - enemy_health_width, status_bar_y,
                             enemy_health_width, status_bar_height))
            player_label = self.font.render("PLAYER", True, (255, 255, 255))
            enemy_label = self.font.render("ENEMY", True, (255, 255, 255))
            self.screen.blit(player_label, (status_bar_x + 10, status_bar_y - 25))
            self.screen.blit(enemy_label, (status_bar_x + status_bar_width - 100, status_bar_y - 25))
            vs_font = pygame.font.SysFont('Arial', 24, bold=True)
            vs_text = vs_font.render("VS", True, (255, 255, 0))
            self.screen.blit(vs_text, (status_bar_x + status_bar_width // 2 - 15, status_bar_y))
        else:
            health_width = int((status_bar_width * 0.5) * (self.player.health / self.player.max_health))
            pygame.draw.rect(self.screen, (255, 0, 0), (status_bar_x, status_bar_y, health_width, status_bar_height))
            oxygen_width = int((status_bar_width * 0.5) * (self.player.oxygen_level / 100))
            pygame.draw.rect(self.screen, (0, 191, 255), (status_bar_x + status_bar_width // 2, status_bar_y, oxygen_width, status_bar_height))
            health_label = self.font.render("HEALTH", True, (255, 255, 255))
            oxygen_label = self.font.render("OXYGEN", True, (255, 255, 255))
            self.screen.blit(health_label, (status_bar_x + 10, status_bar_y - 25))
            self.screen.blit(oxygen_label, (status_bar_x + status_bar_width // 2 + 10, status_bar_y - 25))

    def draw_pause_menu(self):
        """Draw a custom pause menu with sound toggle and exit options"""
        # Semi-transparent overlay
        overlay = pygame.Surface((1280, 720), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Dark semi-transparent layer
        self.screen.blit(overlay, (0, 0))

        # Draw pause menu panel
        panel_width, panel_height = 400, 300
        panel_x, panel_y = (1280 - panel_width) // 2, (720 - panel_height) // 2
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel, (50, 50, 50, 200), (0, 0, panel_width, panel_height), border_radius=20)
        self.screen.blit(panel, (panel_x, panel_y))

        # Pause menu title
        title = self.font_large.render("Pause Menu", True, (255, 255, 255))
        title_shadow = self.font_large.render("Pause Menu", True, (0, 0, 0))
        self.screen.blit(title_shadow, (panel_x + 102, panel_y + 32))
        self.screen.blit(title, (panel_x + 100, panel_y + 30))

        # Get mouse position for hover effects
        mouse_pos = pygame.mouse.get_pos()

        # Sound button
        sound_button = pygame.Rect(panel_x + 100, panel_y + 100, 200, 60)
        sound_color = (180, 120, 180) if sound_button.collidepoint(mouse_pos) else (100, 100, 100)
        pygame.draw.rect(self.screen, sound_color, sound_button, border_radius=10)
        sound_text = "Sound: ON" if self.sound_on else "Sound: OFF"
        sound_label = self.font_medium.render(sound_text, True, (255, 255, 255))
        sound_label_shadow = self.font_medium.render(sound_text, True, (0, 0, 0))
        self.screen.blit(sound_label_shadow, (panel_x + 122, panel_y + 112))
        self.screen.blit(sound_label, (panel_x + 120, panel_y + 110))

        # Exit button
        exit_button = pygame.Rect(panel_x + 100, panel_y + 180, 200, 60)
        exit_color = (180, 120, 180) if exit_button.collidepoint(mouse_pos) else (100, 100, 100)
        pygame.draw.rect(self.screen, exit_color, exit_button, border_radius=10)
        exit_text = "Exit to Main Menu"
        exit_label = self.font_medium.render(exit_text, True, (255, 255, 255))
        exit_label_shadow = self.font_medium.render(exit_text, True, (0, 0, 0))
        self.screen.blit(exit_label_shadow, (panel_x + 102, panel_y + 192))
        self.screen.blit(exit_label, (panel_x + 100, panel_y + 190))

        return sound_button, exit_button

    def draw_status_bar(self, x, y, width, height, ratio, color, label):
        pygame.draw.rect(self.screen, (50, 50, 50), (x, y, width, height))
        fill_width = max(0, min(width, int(width * ratio)))
        pygame.draw.rect(self.screen, color, (x, y, fill_width, height))
        pygame.draw.rect(self.screen, (200, 200, 200), (x, y, width, height), 2)
        label_surf = self.font.render(label, True, (255, 255, 255))
        self.screen.blit(label_surf, (x + 5, y - 25))

    def draw_boss_health_bar(self, rect, ratio, color, label):
        for i in range(rect.height):
            darkness = 30 + int(20 * (i / rect.height))
            pygame.draw.line(self.screen, (darkness, darkness, darkness),
                            (rect.x, rect.y + i), (rect.x + rect.width, rect.y + i))
        fill_width = max(0, min(rect.width, int(rect.width * ratio)))
        for i in range(rect.height):
            r, g, b = color
            intensity = 0.7 + 0.3 * (1 - (i / rect.height))
            bar_color = (min(255, int(r * intensity)), min(255, int(g * intensity)), min(255, int(b * intensity)))
            pygame.draw.line(self.screen, bar_color, (rect.x, rect.y + i), (rect.x + fill_width, rect.y + i))
        segment_width = rect.width / 10
        for i in range(1, 10):
            segment_x = rect.x + (i * segment_width)
            pygame.draw.line(self.screen, (20, 20, 20), (segment_x, rect.y), (segment_x, rect.y + rect.height), 1)
        pygame.draw.rect(self.screen, (200, 200, 200), rect, 2)
        pygame.draw.line(self.screen, (220, 220, 220), (rect.x + 1, rect.y + 1), (rect.x + rect.width - 1, rect.y + 1), 1)
        large_font = pygame.font.SysFont('Arial', 28, bold=True)
        shadow_label = large_font.render(label, True, (0, 0, 0))
        self.screen.blit(shadow_label, (rect.x + 12, rect.y - 35))
        text_label = large_font.render(label, True, (255, 255, 255))
        self.screen.blit(text_label, (rect.x + 10, rect.y - 37))
        percentage = f"{int(ratio * 100)}%"
        percent_font = pygame.font.SysFont('Arial', 20, bold=True)
        percent_text = percent_font.render(percentage, True, (255, 255, 255))
        self.screen.blit(percent_text, (rect.x + rect.width - 50, rect.y - 30))

    def show_launch_screen(self):
        launch_font = pygame.font.SysFont('Arial', 50, bold=True)
        launch_text = launch_font.render("Launching to Mars...", True, (255, 255, 255))
        text_rect = launch_text.get_rect(center=(1280 // 2, 720 // 2))
        if self.sounds['intro']:
            self.sounds['intro'].play()
        start_time = pygame.time.get_ticks()
        duration = 3000
        while pygame.time.get_ticks() - start_time < duration:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.exit_reason = "quit"  # Player closed the window
                    self.running = False
                    if self.sounds['intro']:
                        self.sounds['intro'].stop()
                    return False
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.exit_reason = "exit_to_main"  # Player pressed ESC during launch screen
                        self.running = False
                        if self.sounds['intro']:
                            self.sounds['intro'].stop()
                        return False
            self.screen.fill((10, 10, 30))
            self.screen.blit(launch_text, text_rect)
            pygame.display.flip()
            self.clock.tick(60)
        return True

    def show_vs_animation(self):
        try:
            player_img = pygame.image.load(os.path.join('images', 'player.png')).convert_alpha()
            enemy_img = pygame.image.load(os.path.join('images', 'enemy.png')).convert_alpha()
            vs_img = pygame.image.load(os.path.join('images', 'Vs.png')).convert_alpha()
        except Exception as e:
            print(f"Error loading VS animation images: {e}")
            player_img = pygame.Surface((200, 300), pygame.SRCALPHA)
            player_img.fill((0, 255, 0, 200))
            pygame.draw.rect(player_img, (255, 255, 255), (0, 0, 200, 300), 2)
            enemy_img = pygame.Surface((200, 300), pygame.SRCALPHA)
            enemy_img.fill((255, 0, 0, 200))
            pygame.draw.rect(enemy_img, (255, 255, 255), (0, 0, 200, 300), 2)
            vs_img = pygame.Surface((150, 150), pygame.SRCALPHA)
            vs_font = pygame.font.SysFont('Arial', 50, bold=True)
            vs_text = vs_font.render("VS", True, (255, 255, 255))
            vs_img.blit(vs_text, (25, 25))
        player_img = pygame.transform.scale(player_img, (300, 400))
        enemy_img = pygame.transform.scale(enemy_img, (300, 400))
        vs_img = pygame.transform.scale(vs_img, (200, 200))
        if self.sounds['open_sword']:
            self.sounds['open_sword'].play()
        pygame.time.set_timer(pygame.USEREVENT, 1000)
        fight_sound_played = False
        start_time = pygame.time.get_ticks()
        animation_duration = 5000
        player_start_pos = (-300, 160)
        player_end_pos = (300, 160)
        enemy_start_pos = (1280 + 300, 160)
        enemy_end_pos = (980, 160)
        vs_pos = (640, 360)
        vs_scale = 0.1
        player_health_rect = pygame.Rect(200, 600, 300, 40)
        enemy_health_rect = pygame.Rect(780, 600, 300, 40)
        while pygame.time.get_ticks() - start_time < animation_duration:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.exit_reason = "quit"  # Player closed the window
                    self.running = False
                    return False
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.exit_reason = "exit_to_main"  # Player pressed ESC during VS animation
                        self.running = False
                        return False
                    if event.key in (K_SPACE, K_RETURN):
                        return True
                if event.type == pygame.USEREVENT and not fight_sound_played:
                    if self.sounds['fight']:
                        self.sounds['fight'].play()
                    fight_sound_played = True
            elapsed = pygame.time.get_ticks() - start_time
            progress = min(1.0, elapsed / animation_duration)
            self.screen.fill((10, 10, 30))
            for _ in range(100):
                x = random.randint(0, 1280)
                y = random.randint(0, 720)
                size = random.randint(1, 3)
                brightness = random.randint(150, 255)
                pygame.draw.circle(self.screen, (brightness, brightness, brightness), (x, y), size)
            if progress < 0.4:
                slide_progress = progress / 0.4
                player_x = player_start_pos[0] + (player_end_pos[0] - player_start_pos[0]) * slide_progress
                player_y = player_start_pos[1]
                enemy_x = enemy_start_pos[0] + (enemy_end_pos[0] - enemy_start_pos[0]) * slide_progress
                enemy_y = enemy_start_pos[1]
                current_vs_scale = vs_scale + (1.0 - vs_scale) * slide_progress
                vs_width = int(vs_img.get_width() * current_vs_scale)
                vs_height = int(vs_img.get_height() * current_vs_scale)
                scaled_vs = pygame.transform.scale(vs_img, (vs_width, vs_height))
                vs_rect = scaled_vs.get_rect(center=vs_pos)
                self.screen.blit(player_img, (player_x, player_y))
                self.screen.blit(enemy_img, (enemy_x, enemy_y))
                self.screen.blit(scaled_vs, vs_rect)
            elif progress < 0.7:
                self.screen.blit(player_img, player_end_pos)
                self.screen.blit(enemy_img, enemy_end_pos)
                pulse = 1.0 + 0.1 * math.sin((progress - 0.4) * 20)
                vs_width = int(vs_img.get_width() * pulse)
                vs_height = int(vs_img.get_height() * pulse)
                scaled_vs = pygame.transform.scale(vs_img, (vs_width, vs_height))
                vs_rect = scaled_vs.get_rect(center=vs_pos)
                self.screen.blit(scaled_vs, vs_rect)
                health_progress = (progress - 0.4) / 0.3
                pygame.draw.rect(self.screen, (50, 50, 50), player_health_rect)
                fill_width = int(player_health_rect.width * health_progress)
                pygame.draw.rect(self.screen, (0, 200, 0),
                                 (player_health_rect.x, player_health_rect.y, fill_width, player_health_rect.height))
                pygame.draw.rect(self.screen, (255, 255, 255), player_health_rect, 2)
                pygame.draw.rect(self.screen, (50, 50, 50), enemy_health_rect)
                fill_width = int(enemy_health_rect.width * health_progress)
                pygame.draw.rect(self.screen, (200, 0, 0),
                                 (enemy_health_rect.x, enemy_health_rect.y, fill_width, enemy_health_rect.height))
                pygame.draw.rect(self.screen, (255, 255, 255), enemy_health_rect, 2)
                player_label = self.font.render("PLAYER", True, (255, 255, 255))
                enemy_label = self.font.render("ENEMY", True, (255, 255, 255))
                self.screen.blit(player_label, (player_health_rect.x + 10, player_health_rect.y - 30))
                self.screen.blit(enemy_label, (enemy_health_rect.x + 10, player_health_rect.y - 30))
            else:
                fade_progress = 1.0 - ((progress - 0.7) / 0.3)
                player_img.set_alpha(int(255 * fade_progress))
                enemy_img.set_alpha(int(255 * fade_progress))
                vs_img.set_alpha(int(255 * fade_progress))
                self.screen.blit(player_img, player_end_pos)
                self.screen.blit(enemy_img, enemy_end_pos)
                self.screen.blit(vs_img, vs_img.get_rect(center=vs_pos))
                pygame.draw.rect(self.screen, (50, 50, 50, int(255 * fade_progress)), player_health_rect)
                pygame.draw.rect(self.screen, (0, 200, 0, int(255 * fade_progress)), player_health_rect)
                pygame.draw.rect(self.screen, (255, 255, 255, int(255 * fade_progress)), player_health_rect, 2)
                pygame.draw.rect(self.screen, (50, 50, 50, int(255 * fade_progress)), enemy_health_rect)
                pygame.draw.rect(self.screen, (200, 0, 0, int(255 * fade_progress)), enemy_health_rect)
                pygame.draw.rect(self.screen, (255, 255, 255, int(255 * fade_progress)), enemy_health_rect, 2)
                player_label = self.font.render("PLAYER", True, (255, 255, 255, int(255 * fade_progress)))
                enemy_label = self.font.render("ENEMY", True, (255, 255, 255, int(255 * fade_progress)))
                self.screen.blit(player_label, (player_health_rect.x + 10, player_health_rect.y - 30))
                self.screen.blit(enemy_label, (enemy_health_rect.x + 10, player_health_rect.y - 30))
                bg_alpha = int(255 * (1.0 - fade_progress))
                bg_copy = self.background.copy()
                bg_copy.set_alpha(bg_alpha)
                self.screen.blit(bg_copy, (0, 0))
            pygame.display.flip()
            self.clock.tick(60)
        return True

    def show_victory_message(self):
        team_img = None
        try:
            team_img_path = os.path.join('images', 'Team.jpg')
            if os.path.exists(team_img_path):
                team_img = pygame.image.load(team_img_path).convert()
                img_ratio = team_img.get_height() / team_img.get_width()
                new_width = 800
                new_height = int(new_width * img_ratio)
                team_img = pygame.transform.scale(team_img, (new_width, new_height))
        except Exception as e:
            print(f"Error loading Team.jpg: {e}")
        dream_bg = pygame.Surface((1280, 720), pygame.SRCALPHA)
        for y in range(0, 720, 2):
            alpha = 150 + int(50 * math.sin(y / 30))
            color = (20, 20, 60, alpha)
            pygame.draw.line(dream_bg, color, (0, y), (1280, y), 2)
        leonardo_text = "Leonardo said: It's not the end guys..."
        boss_text = "Boss: You will never get what you want! Hahahaa!"
        start_time = pygame.time.get_ticks()
        animation_duration = 10000
        running = True
        while running and pygame.time.get_ticks() - start_time < animation_duration:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                if event.type == KEYDOWN:
                    if event.key in (K_ESCAPE, K_SPACE, K_RETURN):
                        running = False
            progress = min(1.0, (pygame.time.get_ticks() - start_time) / animation_duration)
            self.screen.fill((0, 0, 0))
            self.screen.blit(dream_bg, (0, 0))
            if team_img:
                team_img.set_alpha(int(255 * min(1.0, progress * 2)))
                img_rect = team_img.get_rect(center=(640, 300))
                self.screen.blit(team_img, img_rect)
            if progress > 0.3:
                text_progress = min(1.0, (progress - 0.3) * 2)
                leo_font = pygame.font.SysFont('Arial', 28, bold=True)
                leo_chars = int(len(leonardo_text) * text_progress)
                leo_display = leonardo_text[:leo_chars]
                leo_surf = leo_font.render(leo_display, True, (200, 200, 255))
                self.screen.blit(leo_surf, (320, 500))
                if progress > 0.6:
                    boss_text_progress = min(1.0, (progress - 0.6) * 2.5)
                    boss_chars = int(len(boss_text) * boss_text_progress)
                    boss_display = boss_text[:boss_chars]
                    boss_font = pygame.font.SysFont('Arial', 28, bold=True)
                    boss_surf = boss_font.render(boss_display, True, (255, 100, 100))
                    self.screen.blit(boss_surf, (320, 550))
            if progress > 0.8:
                if int(pygame.time.get_ticks() / 500) % 2 == 0:
                    continue_font = pygame.font.SysFont('Arial', 20)
                    continue_surf = continue_font.render("Press any key to continue...", True, (255, 255, 255))
                    self.screen.blit(continue_surf, (500, 650))
            pygame.display.flip()
            self.clock.tick(60)
        fade_duration = 1000
        fade_start = pygame.time.get_ticks()
        while pygame.time.get_ticks() - fade_start < fade_duration:
            fade_progress = (pygame.time.get_ticks() - fade_start) / fade_duration
            fade_surface = pygame.Surface((1280, 720))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(int(255 * fade_progress))
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.flip()
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                    break
        return True

    def show_thanks_message(self):
        large_font = pygame.font.SysFont('Arial', 48, bold=True)
        medium_font = pygame.font.SysFont('Arial', 36)
        small_font = pygame.font.SysFont('Arial', 24)
        title_text = large_font.render("Thanks for playing", True, (255, 255, 255))
        subtitle_text = large_font.render("Teenage Mutant Ninja Turtles Metaverse", True, (0, 255, 0))
        title_rect = title_text.get_rect(center=(640, 200))
        subtitle_rect = subtitle_text.get_rect(center=(640, 280))
        start_time = pygame.time.get_ticks()
        animation_duration = 10000
        running = True
        while running:
            current_time = pygame.time.get_ticks()
            progress = min(1.0, (current_time - start_time) / animation_duration)
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.exit_reason = "quit"  # Player closed the window
                    self.running = False
                    return
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
            self.screen.fill((0, 0, 0))
            for y in range(0, 720, 4):
                color_value = int(128 + 127 * math.sin((y / 100) + (current_time / 1000)))
                color = (0, color_value, 0)
                pygame.draw.line(self.screen, color, (0, y), (1280, y), 4)
            for _ in range(200):
                x = (random.randint(0, 1280) + (current_time / 20)) % 1280
                y = (random.randint(0, 720) + (current_time / 30)) % 720
                size = random.randint(1, 3)
                brightness = random.randint(200, 255)
                pygame.draw.circle(self.screen, (brightness, brightness, brightness), (int(x), int(y)), size)
            glow_size = int(20 + 10 * math.sin(current_time / 200))
            for i in range(glow_size, 0, -5):
                alpha = int(255 * (1 - i / glow_size))
                glow_surf = title_text.copy()
                glow_surf.set_alpha(alpha)
                glow_rect = glow_surf.get_rect(center=(640, 200))
                self.screen.blit(glow_surf, (glow_rect.x - i//2, glow_rect.y - i//2))
            self.screen.blit(title_text, title_rect)
            self.screen.blit(subtitle_text, subtitle_rect)
            if progress > 0.3:
                character_y = 450
                character_spacing = 250
                character_colors = [(0, 0, 255), (200, 0, 0), (150, 0, 150), (255, 165, 0)]
                character_names = ["Leonardo", "Raphael", "Donatello", "Michelangelo"]
                for i in range(4):
                    if progress > 0.3 + (i * 0.1):
                        x_pos = 240 + (i * character_spacing)
                        pygame.draw.circle(self.screen, character_colors[i], (x_pos, character_y), 50)
                        name_text = small_font.render(character_names[i], True, (255, 255, 255))
                        name_rect = name_text.get_rect(center=(x_pos, character_y + 70))
                        self.screen.blit(name_text, name_rect)
            if progress > 0.8 or current_time - start_time > 5000:
                if int(current_time / 500) % 2 == 0:
                    exit_text = small_font.render("Press ESC to exit", True, (200, 200, 200))
                    exit_rect = exit_text.get_rect(center=(640, 650))
                    self.screen.blit(exit_text, exit_rect)
            pygame.display.flip()
            self.clock.tick(60)

    def run(self):
        if not self.show_launch_screen():
            return False
        if not self.show_vs_animation():
            return False

        while self.running:
            self.clock.tick(60)
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()

        # Return True only if victory was achieved
        return self.level_completed

def run_mars_level():
    """
    Run the Mars level by instantiating the Mars class and calling its run method.
    Returns True if the level is completed successfu-lly (player won),
    False otherwise (player lost or quit).
    """
    try:
        game = Mars()
        result = game.run()
        # Return True only if victory was achieved
        return game.level_completed
    except Exception as e:
        print(f"Error running Mars level: {e}")
        return False

if __name__ == '__main__':
    try:
        game = Mars()
        game.run()
    except Exception as e:
        print(f"S❌ Error: {e}")
        import traceback
        traceback.print_exc()
        if pygame.get_init():
            pygame.quit()
        sys.exit(1)

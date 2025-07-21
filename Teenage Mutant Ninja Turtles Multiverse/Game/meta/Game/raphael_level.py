import pygame
import av
import numpy as np
import random
from spritesheet import Spritesheet
from player import Player
from enemy import Enemy, spawn_enemy

class RaphaelLevel:
    def __init__(self, screen_width=1280, screen_height=720):
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Meta venv \\ Raphael Level")

        # Level state variables
        self.level_complete = False
        self.level_failed = False
        self.running = True

        # Initialize game elements
        self._initialize_game_objects()
        self._initialize_conversation_states()

    def _initialize_game_objects(self):
        # Background setup
        self.bg_image = pygame.image.load('images2/bg1.jpg')
        self.bg_index = pygame.transform.scale(self.bg_image, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

        # Audio setup
        pygame.mixer.music.load("sounds2/atari.mp3")
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(-1)

        # NPC setup
        self.npc1 = Spritesheet('images2/npc.png')
        try:
            self.frame0 = self.npc1.get_image(frame=0, width=500, height=500, scale=0.3, color=None)
        except Exception as e:
            print("Error loading NPC frame:", e)
            self.frame0 = None

        self.npc_pos = pygame.Rect(300, 370, 64 * 4, 64 * 4)
        self.npc_visible = True

        # Player setup
        player_images = {
            "walk": 'images2/walk.png',
            "light_attack": 'images2/La.png',
            "leg_attack": 'images2/legA.png',
            "ult_attack": 'images2/ult.png',
            "shield": 'images2/safe.png',
            "death_sheet": 'images2/dead.png'
        }

        self.player = Player(
            100, 500,
            player_images["walk"],
            player_images["light_attack"],
            player_images["leg_attack"],
            player_images["ult_attack"],
            player_images["shield"],
            player_images["death_sheet"]
        )

        # Font setup
        self.font = pygame.font.SysFont('Arial', 26)

        # Video setup
        self.video_path = "videos/tiktok.mp4"
        try:
            self.tikok_sound = pygame.mixer.Sound("sounds2/tiktok.mp3")
            self.tikok_sound.set_volume(0.5)
        except Exception as e:
            print("Error loading sound:", e)
            self.tikok_sound = None

        # Enemy setup
        self.enemies = []
        self.enemies_to_spawn = [
            (1000, 400, False),
            (1050, 400, False),
            (1100, 400, True),
        ]
        self.current_spawn_index = 0

        # Game timing
        self.SURVIVAL_TIME_MS = 60000
        self.start_time = pygame.time.get_ticks()

        # UI/UX states
        self.pause_menu_active = False
        self.sound_on = True

    def _initialize_conversation_states(self):
        # Conversation states
        self.STATE_INTRO = 0
        self.STATE_KID_HAPPY = 1
        self.STATE_RAPHAEL_ASKS = 2
        self.STATE_KID_EXPLAINS = 3
        self.STATE_RAPHAEL_WAIT_1 = 4
        self.STATE_SHOW_VIDEO = 5
        self.STATE_RAPHAEL_WAIT_2 = 6
        self.STATE_END = 7

        self.conversation_state = None
        self.show_conversation = False
        self.video_showing = False

        self.dialogues = {
            self.STATE_INTRO: "Raphael: what the shell ? where am i?",
            self.STATE_KID_HAPPY: "Kid: finally you are here! i know you",
            self.STATE_RAPHAEL_ASKS: "Raphael: do i know you pal?",
            self.STATE_KID_EXPLAINS: "Kid: your tiktoks are viral all over the multiverses see",
            self.STATE_RAPHAEL_WAIT_1: "Raphael: Wait! what video what mutlti u said?",
            self.STATE_RAPHAEL_WAIT_2: "Kid: Sorry i need to go now i have things to do",
            self.STATE_SHOW_VIDEO: "Raphael: Wait! i want answers"
        }

        self.video_start_time = 0
        self.last_frame_time = 0

    def scale_to_fit(self, surface, max_width, max_height):
        width, height = surface.get_size()
        scale = min(max_width / width, max_height / height)
        new_size = (int(width * scale), int(height * scale))
        return pygame.transform.scale(surface, new_size)

    def draw_rounded_rect(self, surface, rect, color, radius=10):
        pygame.draw.rect(surface, color, rect, border_radius=radius)

    def draw_health_stamina_bar(self, surface, x, y, width, height, ratio, bar_color, bg_color, radius=8, label=""):
        if label:
            label_surf = self.font.render(label, True, (0, 0, 0))
            label_rect = label_surf.get_rect(center=(x + width // 2, y - 18))
            surface.blit(label_surf, label_rect)

        bg_rect = pygame.Rect(x, y, width, height)
        self.draw_rounded_rect(surface, bg_rect, bg_color, radius)
        fill_width = int(width * ratio)
        fill_rect = pygame.Rect(x, y, fill_width, height)
        self.draw_rounded_rect(surface, fill_rect, bar_color, radius)
        pygame.draw.rect(surface, (0, 0, 0), bg_rect, 2, border_radius=radius)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False

            if self.pause_menu_active:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    menu_rect = pygame.Rect(self.SCREEN_WIDTH//2 - 150, self.SCREEN_HEIGHT//2 - 150, 300, 300)
                    sound_rect = pygame.Rect(menu_rect.x + 50, menu_rect.y + 60, 200, 50)
                    exit_rect = pygame.Rect(menu_rect.x + 50, menu_rect.y + 140, 200, 50)

                    if sound_rect.collidepoint(event.pos):
                        self.sound_on = not self.sound_on
                        pygame.mixer.music.set_volume(1.0 if self.sound_on else 0.0)
                        if self.tikok_sound:
                            self.tikok_sound.set_volume(0.5 if self.sound_on else 0.0)
                    elif exit_rect.collidepoint(event.pos):
                        self.running = False
                        return False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.pause_menu_active = False
                    pygame.mixer.music.unpause()
                    pygame.mouse.set_visible(False)
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.pause_menu_active = True
                        pygame.mixer.music.pause()
                        pygame.mouse.set_visible(True)
                    if event.key == pygame.K_t and self.conversation_state is None:
                        if self.player.rect.colliderect(self.npc_pos.inflate(50, 50)):
                            self.conversation_state = self.STATE_INTRO
                            self.show_conversation = True
                    elif event.key == pygame.K_RETURN and self.show_conversation:
                        self.advance_conversation()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_attack()

        return True

    def advance_conversation(self):
        if self.conversation_state == self.STATE_INTRO:
            self.conversation_state = self.STATE_KID_HAPPY
        elif self.conversation_state == self.STATE_KID_HAPPY:
            self.conversation_state = self.STATE_RAPHAEL_ASKS
        elif self.conversation_state == self.STATE_RAPHAEL_ASKS:
            self.conversation_state = self.STATE_KID_EXPLAINS
        elif self.conversation_state == self.STATE_KID_EXPLAINS:
            self.conversation_state = self.STATE_RAPHAEL_WAIT_1
        elif self.conversation_state == self.STATE_RAPHAEL_WAIT_1:
            self.conversation_state = self.STATE_SHOW_VIDEO
            self.video_showing = True
            self.video_start_time = pygame.time.get_ticks()
            self.last_frame_time = self.video_start_time
            if self.tikok_sound:
                self.tikok_sound.set_volume(1.0 if self.sound_on else 0.0)
                self.tikok_sound.play()
        elif self.conversation_state == self.STATE_SHOW_VIDEO:
            self.video_showing = False
            if self.tikok_sound:
                self.tikok_sound.stop()
            self.conversation_state = self.STATE_RAPHAEL_WAIT_2
        elif self.conversation_state == self.STATE_RAPHAEL_WAIT_2:
            self.conversation_state = self.STATE_END
            self.show_conversation = False
        elif self.conversation_state == self.STATE_END:
            self.conversation_state = None
            self.show_conversation = False

    def handle_attack(self):
        attack_range = 60
        damage = 10

        if not self.player.is_shielding:
            for enemy in self.enemies:
                if enemy.health <= 0:
                    continue
                dx = enemy.x - self.player.turtle_x
                dy = enemy.y - self.player.turtle_y
                distance = (dx ** 2 + dy ** 2) ** 0.5

                # Optional direction check
                facing_right = getattr(self.player, "facing_right", True)
                in_front = (facing_right and dx >= 0) or (not facing_right and dx <= 0)

                if distance <= attack_range and in_front:
                    enemy.take_damage(damage)
        else:
            if self.player.stamina > 0:
                self.player.stamina = max(0, self.player.stamina - 10)
            else:
                self.player.stamina = 20

    def update_game_state(self):
        current_time = pygame.time.get_ticks()
        time_passed = current_time - self.start_time
        time_left_ms = max(0, self.SURVIVAL_TIME_MS - time_passed)

        # Check level completion conditions
        alive_enemies = [e for e in self.enemies if e.health > 0]
        if len(alive_enemies) == 0 and self.current_spawn_index >= len(self.enemies_to_spawn):
            if self.conversation_state is None or self.conversation_state == self.STATE_END:
                self.level_complete = True
                self.running = False

        # Check level failure conditions
        if self.player.health <= 0:
            self.level_failed = True
            self.running = False

        # Update game objects
        if not self.pause_menu_active:
            self.player.update()
            if not self.show_conversation and not self.video_showing:
                for enemy in self.enemies:
                    enemy.update()

            # Spawn enemies if needed
            if len(alive_enemies) == 0 and self.current_spawn_index < len(self.enemies_to_spawn):
                spawn_x, spawn_y, is_strong = self.enemies_to_spawn[self.current_spawn_index]
                new_enemy = spawn_enemy(spawn_x, spawn_y, self.player, strong=is_strong)
                self.enemies.append(new_enemy)
                self.current_spawn_index += 1

        # Handle video playback
        if self.video_showing:
            self.handle_video_playback(current_time)

    def handle_video_playback(self, current_time):
        if current_time - self.last_frame_time >= self.frame_duration:
            self.last_frame_time = current_time
            try:
                frame = next(self.container.decode(self.video_stream))
                frame_np = frame.to_ndarray(format='rgb24')
                frame_surface = pygame.surfarray.make_surface(np.flipud(np.rot90(frame_np)))
                self.frame_surface = self.scale_to_fit(frame_surface, 800, 720)
                self.frame_rect = self.frame_surface.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2))
            except (StopIteration, av.AVError):
                self.video_showing = False
                if self.tikok_sound:
                    self.tikok_sound.stop()
                self.conversation_state = self.STATE_RAPHAEL_WAIT_2
            except Exception as e:
                print("Video error:", e)
                self.video_showing = False
                if self.tikok_sound:
                    self.tikok_sound.stop()
                self.conversation_state = self.STATE_RAPHAEL_WAIT_2

        if current_time - self.video_start_time > 51000:
            self.video_showing = False
            if self.tikok_sound:
                self.tikok_sound.stop()
            self.conversation_state = self.STATE_RAPHAEL_WAIT_2

    def render(self):
        # Draw background
        self.screen.blit(self.bg_index, (0, 0))

        # Draw NPC
        if self.npc_visible and self.frame0:
            self.screen.blit(self.frame0, (self.npc_pos.x, self.npc_pos.y))

        # Draw "Press T to Talk" prompt
        if self.player.rect.colliderect(self.npc_pos.inflate(100, 100)) and not self.show_conversation:
            talk_prompt_font = pygame.font.SysFont('Arial', 24, bold=True)
            prompt_text = talk_prompt_font.render("Press T to Talk", True, (255, 255, 255))
            prompt_rect = prompt_text.get_rect(center=(self.npc_pos.centerx, self.npc_pos.top - 20))
            self.screen.blit(prompt_text, prompt_rect)

        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)
            if enemy.health > 0:
                health_bar_width = 50
                health_ratio = enemy.health / enemy.max_health
                health_bar_rect = pygame.Rect(enemy.x, enemy.y - 10, int(health_bar_width * health_ratio), 5)
                health_bar_border = pygame.Rect(enemy.x, enemy.y - 10, health_bar_width, 5)
                pygame.draw.rect(self.screen, (255, 0, 0), health_bar_border)
                pygame.draw.rect(self.screen, (0, 255, 0), health_bar_rect)

        # Draw player
        self.player.image.set_alpha(120 if self.player.health / self.player.max_health < 0.1 else 255)
        self.player.draw(self.screen)

        # Draw UI elements
        self.draw_ui()

        # Draw conversation box if needed
        if self.show_conversation and self.conversation_state is not None:
            self.draw_conversation_box()

        # Draw video if playing
        if self.video_showing and hasattr(self, 'frame_surface'):
            self.screen.blit(self.frame_surface, self.frame_rect)

        # Draw pause menu if active
        if self.pause_menu_active:
            self.draw_pause_menu()

        pygame.display.update()

    def draw_ui(self):
        player_health_ratio = self.player.health / self.player.max_health
        player_stamina_ratio = self.player.stamina / self.player.max_stamina

        self.draw_health_stamina_bar(self.screen, 60, 60, 250, 20, player_health_ratio,
                                     (0, 255, 0), (255, 0, 0), radius=10, label="HP")
        self.draw_health_stamina_bar(self.screen, 60, 110, 200, 20, player_stamina_ratio,
                                     (0, 200, 255), (100, 100, 100), radius=10, label="ST")

        current_time = pygame.time.get_ticks()
        time_passed = current_time - self.start_time
        time_left_ms = max(0, self.SURVIVAL_TIME_MS - time_passed)
        timer_text = self.font.render(f"{time_left_ms // 1000}s", True, (0, 0, 0))
        self.screen.blit(timer_text, (20, 20))

    def draw_conversation_box(self):
        lines = []
        full_text = self.dialogues.get(self.conversation_state, "")
        max_chars_per_line = 50
        while len(full_text) > 0:
            lines.append(full_text[:max_chars_per_line])
            full_text = full_text[max_chars_per_line:]

        box_rect = pygame.Rect(50, self.SCREEN_HEIGHT - 150, self.SCREEN_WIDTH - 100, 120)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), box_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), box_rect, 3)

        for i, line in enumerate(lines):
            text_surf = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(text_surf, (box_rect.x + 20, box_rect.y + 20 + i * 30))

    def draw_pause_menu(self):
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        menu_rect = pygame.Rect(self.SCREEN_WIDTH//2 - 150, self.SCREEN_HEIGHT//2 - 150, 300, 300)
        self.draw_rounded_rect(self.screen, menu_rect, (50, 50, 50), radius=20)

        sound_text = "Sound On" if self.sound_on else "Sound Off"
        sound_surf = self.font.render(sound_text, True, (0, 0, 0))
        sound_button_rect = pygame.Rect(menu_rect.x + 50, menu_rect.y + 60, 200, 50)
        self.draw_rounded_rect(self.screen, sound_button_rect, (180, 180, 180), radius=15)
        self.screen.blit(sound_surf, sound_surf.get_rect(center=sound_button_rect.center))

        exit_surf = self.font.render("Exit Game", True, (0, 0, 0))
        exit_button_rect = pygame.Rect(menu_rect.x + 50, menu_rect.y + 140, 200, 50)
        self.draw_rounded_rect(self.screen, exit_button_rect, (180, 180, 180), radius=15)
        self.screen.blit(exit_surf, exit_surf.get_rect(center=exit_button_rect.center))

    def run(self):
        # Initialize video container
        self.container = av.open(self.video_path)
        self.video_stream = next(s for s in self.container.streams if s.type == 'video')
        self.frame_rate = float(self.video_stream.average_rate)
        self.frame_duration = (1000 / self.frame_rate) * 0.9

        clock = pygame.time.Clock()

        while self.running:
            dt = clock.tick(60)

            if not self.handle_events():
                break

            self.update_game_state()
            self.render()

        # Clean up
        self.cleanup()
        return self.level_complete

    def cleanup(self):
        if hasattr(self, 'container'):
            self.container.close()
        if self.tikok_sound:
            self.tikok_sound.stop()
        pygame.mixer.music.stop()


def run_raphael_level():
    level = RaphaelLevel()
    return level.run()


if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    run_raphael_level()
    pygame.quit()
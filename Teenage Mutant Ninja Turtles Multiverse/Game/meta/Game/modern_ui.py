# modern_ui.py
import pygame
import math
from constants import UIState, UI_COLORS


class ModernUI:
    """Modern UI system for the game"""

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.state = UIState.MAIN
        self.COLORS = UI_COLORS

        # Fonts
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_large = pygame.font.Font(None, 48)
        self.font_title = pygame.font.Font(None, 64)

        # Animation variables
        self.pulse_anim = 0
        self.shake_offset = 0
        self.anim_timer = 0
        self.muted = False

        # Player stats
        self.health = 100
        self.oxygen = 100
        self.stamina = 100

        # Message system
        self.message = None
        self.message_timer = 0

        # Initialize UI elements
        self._setup_ui_elements()

    def _setup_ui_elements(self):
        """Initialize all UI element positions"""
        # Top bar elements
        self.health_rect = pygame.Rect(20, 20, 200, 30)
        self.oxygen_rect = pygame.Rect(20, 60, 200, 30)
        self.stamina_rect = pygame.Rect(20, 100, 200, 30)

        # Control buttons
        self.settings_btn = pygame.Rect(self.screen_width - 60, 20, 40, 40)
        self.inventory_btn = pygame.Rect(self.screen_width - 120, 20, 40, 40)

        # Menu elements
        self.menu_rect = pygame.Rect(
            self.screen_width // 2 - 150,
            self.screen_height // 2 - 150,
            300, 300
        )
        self.resume_btn = pygame.Rect(
            self.menu_rect.x + 50, self.menu_rect.y + 80, 200, 50
        )
        self.sound_btn = pygame.Rect(
            self.menu_rect.x + 50, self.menu_rect.y + 140, 200, 50
        )
        self.exit_btn = pygame.Rect(
            self.menu_rect.x + 50, self.menu_rect.y + 200, 200, 50
        )

        # Inventory elements
        self.inventory_rect = pygame.Rect(
            self.screen_width // 2 - 250,
            self.screen_height // 2 - 250,
            500, 500
        )

        # Boss warning
        self.boss_warning_rect = pygame.Rect(
            0, self.screen_height // 2 - 100,
            self.screen_width, 200
        )

    def update(self, dt):
        self.anim_timer += dt
        self.pulse_anim = (math.sin(self.anim_timer * 3) * 0.1 + 1)
        self.shake_offset = math.sin(self.anim_timer * 10) * 3 if self.health < 30 else 0

        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = None

    def show_message(self, text, duration=2):
        self.message = text
        self.message_timer = duration

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.state in [UIState.MAIN, UIState.PAUSED, UIState.INVENTORY]:
                    self.state = UIState.PAUSED if self.state == UIState.MAIN else UIState.MAIN
            elif event.key == pygame.K_i:
                self.state = UIState.INVENTORY if self.state == UIState.MAIN else UIState.MAIN

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.state == UIState.PAUSED:
                if self.resume_btn.collidepoint(event.pos):
                    self.state = UIState.MAIN
                elif self.sound_btn.collidepoint(event.pos):
                    self.muted = not self.muted
                elif self.exit_btn.collidepoint(event.pos):
                    return "exit"
            elif self.state == UIState.MAIN:
                if self.settings_btn.collidepoint(event.pos):
                    self.state = UIState.PAUSED
                elif self.inventory_btn.collidepoint(event.pos):
                    self.state = UIState.INVENTORY
        return None

    def _draw_stat_bar(self, screen, rect, value, color, label):
        pygame.draw.rect(screen, self.COLORS['background'][:3], rect.inflate(4, 4), border_radius=8)
        fill_width = int((value / 100) * (rect.width - 10))
        fill_rect = pygame.Rect(rect.x + 5, rect.y + 5, max(10, fill_width), rect.height - 10)
        pygame.draw.rect(screen, color, fill_rect, border_radius=6)
        label_text = self.font_small.render(f"{label}: {int(value)}%", True, self.COLORS['text'])
        screen.blit(label_text, (rect.x + 10, rect.y + (rect.height // 2 - label_text.get_height() // 2)))

    def _draw_main_ui(self, screen):
        top_bar = pygame.Surface((self.screen_width, 140), pygame.SRCALPHA)
        top_bar.fill((*self.COLORS['background'][:3], 180))
        screen.blit(top_bar, (0, 0))

        self._draw_stat_bar(screen, self.health_rect, self.health, self.COLORS['health'], "HEALTH")
        self._draw_stat_bar(screen, self.oxygen_rect, self.oxygen, self.COLORS['oxygen'], "OXYGEN")
        self._draw_stat_bar(screen, self.stamina_rect, self.stamina, self.COLORS['stamina'], "STAMINA")

        hint_text = self.font_small.render("H: Helmet | I: Inventory | ESC: Menu", True, self.COLORS['text'])
        screen.blit(hint_text, (20, self.screen_height - 30))

    def _draw_pause_menu(self, screen):
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        pygame.draw.rect(screen, self.COLORS['background'], self.menu_rect, border_radius=12)
        pygame.draw.rect(screen, self.COLORS['primary'], self.menu_rect, border_radius=12, width=3)

        title = self.font_title.render("PAUSED", True, self.COLORS['primary'])
        screen.blit(title, (self.menu_rect.centerx - title.get_width() // 2, self.menu_rect.y + 30))

        self._draw_button(screen, self.resume_btn, "RESUME", self.COLORS['primary'])
        sound_text = "SOUND ON" if not self.muted else "SOUND OFF"
        self._draw_button(screen, self.sound_btn, sound_text, self.COLORS['primary'])
        self._draw_button(screen, self.exit_btn, "EXIT", self.COLORS['danger'])

    def _draw_button(self, screen, rect, text, color):
        pygame.draw.rect(screen, color, rect, border_radius=8)
        button_text = self.font_medium.render(text, True, self.COLORS['text_dark'])
        text_rect = button_text.get_rect(center=rect.center)
        screen.blit(button_text, text_rect)

    def _draw_inventory(self, screen):
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        pygame.draw.rect(screen, self.COLORS['background'], self.inventory_rect, border_radius=12)
        pygame.draw.rect(screen, self.COLORS['primary'], self.inventory_rect, border_radius=12, width=3)

        title = self.font_title.render("INVENTORY", True, self.COLORS['primary'])
        screen.blit(title, (self.inventory_rect.centerx - title.get_width() // 2, self.inventory_rect.y + 30))

    def _draw_boss_warning(self, screen):
        pulse = (math.sin(self.anim_timer * 5) * 0.2 + 0.8)
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((255, 50, 50, int(100 * pulse)))
        screen.blit(overlay, (0, 0))

        pygame.draw.rect(screen, self.COLORS['danger'], self.boss_warning_rect, border_radius=12)
        pygame.draw.rect(screen, self.COLORS['text'], self.boss_warning_rect, border_radius=12, width=3)

        warning = self.font_large.render("WARNING!", True, self.COLORS['text'])
        screen.blit(warning, (self.boss_warning_rect.centerx - warning.get_width() // 2,
                              self.boss_warning_rect.y + 30))

        message = self.font_medium.render("All spacecraft parts collected!", True, self.COLORS['text'])
        screen.blit(message, (self.boss_warning_rect.centerx - message.get_width() // 2,
                              self.boss_warning_rect.y + 80))

        action = self.font_medium.render("Press T to teleport to boss", True, self.COLORS['warning'])
        screen.blit(action, (self.boss_warning_rect.centerx - action.get_width() // 2,
                             self.boss_warning_rect.y + 130))

    def _draw_game_over(self, screen):
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (0, 0))

        game_over = self.font_title.render("GAME OVER", True, self.COLORS['danger'])
        screen.blit(game_over, (self.screen_width // 2 - game_over.get_width() // 2,
                                self.screen_height // 2 - 100))

        restart = self.font_medium.render("Press R to restart", True, self.COLORS['primary'])
        screen.blit(restart, (self.screen_width // 2 - restart.get_width() // 2,
                              self.screen_height // 2 + 180))

    def draw(self, screen):
        if self.state == UIState.MAIN:
            self._draw_main_ui(screen)
        elif self.state == UIState.PAUSED:
            self._draw_main_ui(screen)
            self._draw_pause_menu(screen)
        elif self.state == UIState.INVENTORY:
            self._draw_main_ui(screen)
            self._draw_inventory(screen)
        elif self.state == UIState.BOSS_WARNING:
            self._draw_main_ui(screen)
            self._draw_boss_warning(screen)
        elif self.state == UIState.GAME_OVER:
            self._draw_game_over(screen)

        if self.message:
            msg_surf = self.font_medium.render(self.message, True, self.COLORS['warning'])
            msg_rect = msg_surf.get_rect(center=(self.screen_width // 2, self.screen_height - 50))
            screen.blit(msg_surf, msg_rect)

    def set_stats(self, health=None, oxygen=None, stamina=None):
        if health is not None:
            self.health = health
        if oxygen is not None:
            self.oxygen = oxygen
        if stamina is not None:
            self.stamina = stamina

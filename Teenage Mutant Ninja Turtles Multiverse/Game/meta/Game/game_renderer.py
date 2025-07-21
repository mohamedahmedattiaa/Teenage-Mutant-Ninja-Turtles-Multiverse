# game_renderer.py
import pygame
import random
from constants import GameState, SCREEN_WIDTH, SCREEN_HEIGHT


class GameRenderer:
    """Handles all game rendering operations"""

    def __init__(self, screen):
        self.screen = screen

    def add_space_particles(self):
        """Add animated space particle effects"""
        for _ in range(5):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.randint(1, 3)
            pygame.draw.circle(self.screen, (255, 255, 255), (x, y), size)

    def render_character_selection(self, selector=None):
        """Render character selection screen"""
        self.screen.fill((10, 10, 30))  # Dark space background

        # For now, just show a placeholder
        font = pygame.font.Font(None, 48)
        text = font.render("CHARACTER SELECTION", True, (255, 255, 255))
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text, text_rect)

        # Note: selector.draw() would go here when implemented

    def render_gameplay(self, game_state, player, inventory, ui, bg_manager, level_manager):
        """Render main gameplay elements"""
        # Clear screen with dark space background
        self.screen.fill((0, 0, 40))

        # Draw level-specific background
        bg_manager.draw(self.screen)

        # Add space particle effects
        self.add_space_particles()

        # Draw player
        player.draw(self.screen)

        # Draw inventory
        inventory.render(self.screen)

        # Draw UI overlay
        ui.draw(self.screen)

        # Draw level indicator
        level_info = level_manager.get_level_info()
        level_text = ui.font_medium.render(
            f"Level {level_info['current_level']}",
            True, ui.COLORS['primary']
        )
        self.screen.blit(level_text, (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 50))

    def render_game_over(self, ui):
        """Render game over screen"""
        self.screen.fill((20, 20, 40))
        ui.draw(self.screen)

    def clear_screen(self, color=(0, 0, 0)):
        """Clear screen with specified color"""
        self.screen.fill(color)

    def flip_display(self):
        """Update the display"""
        pygame.display.flip()
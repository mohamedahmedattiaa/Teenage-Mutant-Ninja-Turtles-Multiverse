# event_handler.py
import pygame
from constants import GameState, UIState


class EventHandler:
    """Centralized event handling system"""

    def __init__(self):
        pass

    def handle_character_selection_events(self, event, selector):
        """Handle events during character selection"""
        # Note: selector needs to be implemented
        # selector.handle_event(event)

        # For now, skip character selection
        return "skip_selection"

    def handle_gameplay_events(self, event, game_state, ui, player, level_manager):
        """Handle events during gameplay"""
        result = {}

        # Handle UI events first
        ui_result = ui.handle_event(event)
        if ui_result == "exit":
            result['action'] = 'exit'
            return result

        # Handle keyboard events
        if event.type == pygame.KEYDOWN:
            # Helmet toggle
            if event.key == pygame.K_h:
                player.toggle_helmet()
                result['helmet_toggled'] = True

            # Level progression
            elif event.key == pygame.K_n:
                result['next_level_requested'] = True

            # Boss teleport
            elif event.key == pygame.K_t and level_manager.boss_fight_unlocked:
                result['boss_teleport'] = True
                print("Teleporting to boss fight!")

            # Restart game
            elif event.key == pygame.K_r and ui.state == UIState.GAME_OVER:
                result['restart_requested'] = True

        return result

    def handle_quit_event(self, event):
        """Handle pygame quit events"""
        if event.type == pygame.QUIT:
            return True
        return False
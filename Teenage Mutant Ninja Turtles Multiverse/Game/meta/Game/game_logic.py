# game_logic.py
from constants import GameState, UIState


class GameLogic:
    """Handles core game logic and state management"""

    def __init__(self):
        pass

    def update_gameplay(self, player, inventory, ui, level_manager, bg_manager, dt):
        """Update gameplay elements"""
        # Only update if game is not paused
        if ui.state == UIState.MAIN:
            player.update()

            # Check level completion
            if level_manager.check_level_completion(inventory):
                level_info = level_manager.get_level_info()
                if level_info['game_state'] == GameState.LEVEL_ONE:
                    print("Level 1 complete! Press N to advance to Level 2")
                elif level_info['game_state'] == GameState.LEVEL_TWO:
                    print("Level 2 complete! Press N to advance to Boss Level")
                elif level_info['game_state'] == GameState.LEVEL_THREE:
                    # Handle boss unlock
                    boss_status = level_manager.handle_level_three_boss_unlock(inventory, bg_manager)
                    if boss_status == "boss_warning":
                        ui.state = UIState.BOSS_WARNING

        # Update background and UI
        bg_manager.update(dt)

        # Update UI with player stats
        stats = player.get_stats()
        ui.set_stats(
            health=stats['health'],  # Changed to lowercase to match get_stats()
            oxygen=stats.get('oxygen', 100),  # Using correct lowercase key
            stamina=stats.get('stamina', 100)  # Using correct lowercase key
        )
        ui.update(dt)

        # Check game over condition
        if player.health <= 0:
            ui.state = UIState.GAME_OVER

    def handle_level_progression(self, level_manager, inventory):
        """Handle advancing to next level"""
        level_info = level_manager.get_level_info()

        # Check if player can advance
        if level_manager.check_level_completion(inventory):
            if level_manager.transition_to_next_level():
                return "level_advanced"
        else:
            print("Collect all spacecraft parts before advancing!")
            return "parts_needed"

        return "no_change"

    def handle_restart(self, level_manager, ui):
        """Handle game restart"""
        level_info = level_manager.get_level_info()
        current_level = level_info['current_level']

        # Reset UI state
        ui.state = UIState.MAIN

        return "restart_level", current_level

    def check_win_condition(self, level_manager, inventory):
        """Check if player has won the game"""
        level_info = level_manager.get_level_info()

        if (level_info['game_state'] == GameState.LEVEL_THREE and
                level_info['boss_fight_unlocked'] and
                level_manager.check_level_completion(inventory)):
            return True
        return False
# level_manager.py
from constants import GameState
from inventory import InventoryItem


class LevelManager:
    """Manages level progression and content"""

    def __init__(self):
        self.current_level = 1
        self.game_state = GameState.CHARACTER_SELECTION
        self.boss_fight_unlocked = False
        self.mars_transition_triggered = False

    def get_level_spacecraft_parts(self, level_num):
        """Get spacecraft parts for specific level"""
        if level_num == 1:
            return [
                InventoryItem("Engine Component", "images/part1.png", "Needed for propulsion", True),
                InventoryItem("Navigation System", "images/part2.png", "Required for travel", True),
            ]
        elif level_num == 2:
            return [
                InventoryItem("Power Core", "images/part3.png", "Main energy source", True),
                InventoryItem("Advanced Scanner", "images/part5.png", "Enhanced detection", True),
            ]
        elif level_num == 3:
            return [
                InventoryItem("Teleporter", "images/part4.png", "Final boss piece", True),
                InventoryItem("Ultimate Weapon", "images/part6.png", "Boss destroyer", True),
            ]
        return []

    def initialize_level_content(self, level_num, player_creator_func):
        """Initialize content specific to the current level"""
        # Create player instance
        player = player_creator_func()

        # Get level-specific spacecraft parts
        spacecraft_parts = self.get_level_spacecraft_parts(level_num)

        print(f"Initialized Level {level_num}")
        return player, spacecraft_parts

    def can_advance_level(self, inventory, level_num):
        """Check if player can advance to next level"""
        required_parts = len(self.get_level_spacecraft_parts(level_num))
        collected_parts = inventory.get_spacecraft_parts_count()
        return collected_parts >= required_parts

    def transition_to_next_level(self):
        """Handle transition between levels"""
        if self.current_level < 3:
            self.current_level += 1

            if self.current_level == 2:
                self.game_state = GameState.LEVEL_TWO
                print("Transitioning to Level 2 - Mars Surface")

            elif self.current_level == 3:
                self.game_state = GameState.LEVEL_THREE
                self.boss_fight_unlocked = True
                print("Transitioning to Level 3 - Boss Arena")

            # Reset transition flags
            self.mars_transition_triggered = False
            return True
        return False

    def check_level_completion(self, inventory):
        """Check if current level is complete"""
        if self.game_state == GameState.LEVEL_ONE:
            return self.can_advance_level(inventory, 1)
        elif self.game_state == GameState.LEVEL_TWO:
            return self.can_advance_level(inventory, 2)
        elif self.game_state == GameState.LEVEL_THREE:
            return self.can_advance_level(inventory, 3)
        return False

    def handle_level_three_boss_unlock(self, inventory, bg_manager):
        """Handle boss fight unlock in level 3"""
        if self.game_state == GameState.LEVEL_THREE:
            if self.can_advance_level(inventory, 3):
                self.boss_fight_unlocked = True

                # Start Mars transition for boss fight
                if not self.mars_transition_triggered:
                    bg_manager.start_mars_transition()
                    self.mars_transition_triggered = True

                return "boss_warning"
        return None

    def get_level_info(self):
        """Get current level information"""
        return {
            'current_level': self.current_level,
            'game_state': self.game_state,
            'boss_fight_unlocked': self.boss_fight_unlocked,
            'mars_transition_triggered': self.mars_transition_triggered
        }
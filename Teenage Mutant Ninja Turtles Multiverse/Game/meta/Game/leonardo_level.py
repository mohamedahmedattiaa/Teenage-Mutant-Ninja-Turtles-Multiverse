import random
import pygame
import sys
import os
import math

# Add project paths
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'LevelOne'))
sys.path.append(os.path.join(project_root, 'LevelTwo'))
sys.path.append(os.path.join(project_root, 'LevelThree'))
sys.path.append(os.path.join(project_root, 'UI'))

# Import game modules
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, GameState
from asset_loader import AssetLoader
from space_turtle_player import SpaceTurtlePlayer
from modern_ui import ModernUI
from level_manager import LevelManager
from event_handler import EventHandler
from game_renderer import GameRenderer
from game_logic import GameLogic

# Import existing modules
from inventory import Inventory
from BackgroundSystem import BackgroundManager
from SpacecraftParts import SpacecraftPartsManager
from mars import Mars, run_mars_level


def run_leonardo_level():
    """
    Run the Leonardo level by instantiating the SpaceGameMain class and calling its run method.
    Returns True if the level is completed successfully, False otherwise.
    """
    try:
        game = SpaceGameMain()
        return game.run()
    except Exception as e:
        print(f"Error running Leonardo level: {e}")
        return False


class SpaceGameMain:
    """Main game class that orchestrates all systems with enhanced spacecraft mechanics"""

    def __init__(self):
        # Initialize Pygame
        pygame.init()

        # Set up screen
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Leo's Space Adventure - Spacecraft Collection")
        self.clock = pygame.time.Clock()
        self.level_completed = False
        self.asset_loader = AssetLoader()
        self.bg_manager = BackgroundManager(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.ui = ModernUI(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.level_manager = LevelManager()
        self.event_handler = EventHandler()
        self.renderer = GameRenderer(self.screen)
        self.game_logic = GameLogic()

        # Spacecraft system
        self.parts_manager = None
        self.spacecraft_ready = False
        self.parts_collected = 0
        self.required_parts = 4

        # Pause menu
        self.paused = False
        self.sound_on = True
        self.font_large = pygame.font.SysFont('Arial', 48)
        self.font_medium = pygame.font.SysFont('Arial', 36)
        self.font_small = pygame.font.SysFont('Arial', 24)

        # Game state variables
        self.running = True
        self.selected_character = None
        self.player = None
        self.inventory = None
        self.exit_reason = "normal"  # Track the reason for exiting the level

        # Enhanced transition system
        self.transition_active = False
        self.transition_timer = 0
        self.transition_duration = 4.0
        self.transition_phase = "countdown"  # countdown, launch, travel, arrival

        # Performance tracking
        self.fps = 60
        self.delta_accumulator = 0

        # Load assets
        if not self.asset_loader.load_all_assets():
            print("❌ Failed to load assets!")
            pygame.quit()
            exit()

        print("✅ Space Game initialized successfully!")

    def create_player(self):
        """Create player instance with loaded assets"""
        return SpaceTurtlePlayer(
            100, 500,
            self.asset_loader.get_sprite('walk'),
            self.asset_loader.get_sprite('light_attack'),
            self.asset_loader.get_sprite('jump_attack'),
            self.asset_loader.get_sprite('ult_attack'),
            self.asset_loader.get_sprite('shield'),
            self.asset_loader.get_sprite('helmet')
        )

    def initialize_level_content(self, level_num):
        """Initialize content for specific level with enhanced spacecraft system"""
        print(f"🌟 Initializing Level {level_num}")

        # Initialize level content
        self.player, _ = self.level_manager.initialize_level_content(
            level_num, self.create_player
        )
        self.inventory = Inventory()

        # Enhanced spacecraft system for Level 1 (Moon)
        if level_num == 1:
            self.parts_manager = SpacecraftPartsManager(SCREEN_WIDTH, SCREEN_HEIGHT)
            self.parts_manager.generate_parts()  # This will generate parts with default images
            self.spacecraft_ready = False
            self.parts_collected = 0

            print("🌙 Moon level initialized!")
            print(f"🔧 {self.required_parts} spacecraft parts scattered across the moon")
            print("🚀 Collect all parts to unlock Mars travel!")

        elif level_num == 2:
            print("🔴 Mars level initialized!")
            print("🏭 Explore the red planet and build your base!")
            self.parts_manager = None

        elif level_num == 3:
            print("🌌 Space station level initialized!")
            print("🛰 Navigate the cosmic frontier!")
            self.parts_manager = None

    def handle_character_selection(self):
        """Handle character selection phase"""
        self.selected_character = "Space Explorer Leo"
        self.level_manager.game_state = GameState.LEVEL_ONE
        self.initialize_level_content(1)
        print(f"👨‍🚀 Starting adventure with: {self.selected_character}")

    # In leonardo_level.py, update the handle_spacecraft_collection method

    def handle_spacecraft_collection(self, dt):
        """Enhanced spacecraft part collection system"""
        if not self.parts_manager or not self.player:
            return

        # Update parts manager
        self.parts_manager.update(dt)

        # Check for part collection with enhanced feedback
        keys = pygame.key.get_pressed()
        collected_parts = self.parts_manager.check_collection(
            self.player.rect, self.inventory, keys
        )

        # Process collected parts
        for part in collected_parts:
            # Make sure the part was added to inventory by checking inventory count
            if self.inventory.get_spacecraft_parts_count() > self.parts_collected:
                self.parts_collected = self.inventory.get_spacecraft_parts_count()
                print(f"✨ Collected: {part.part_name} ({self.parts_collected}/{self.required_parts})")

                # Play collect sound
                try:
                    sound_path = os.path.join(project_root, "sounds", "sounds", "collect.mp3")
                    if os.path.exists(sound_path):
                        collect_sound = pygame.mixer.Sound(sound_path)
                        collect_sound.play()
                except Exception as e:
                    print(f"🔊 Collect sound error: {e}")

                # Enhanced UI feedback
                self.ui.show_message(f"🔧 {part.part_name} acquired!", 2.5)

                # Check if spacecraft is ready
                if self.parts_collected >= self.required_parts:
                    self.spacecraft_ready = True
                    print("🚀 SPACECRAFT ASSEMBLY COMPLETE!")
                    print("💫 Mars launch sequence is now available!")
                    self.ui.show_message("🚀 Spacecraft Ready! Click Launch!", 4.0)

    def start_mars_transition(self):
        """Enhanced Mars transition with multiple phases"""
        print("🚀 INITIATING MARS LAUNCH SEQUENCE! 🚀")
        self.transition_active = True
        self.transition_timer = 0
        self.transition_phase = "countdown"
        self.transition_duration = 4.0  # Ensure this is set (4 seconds total transition)

        # Play enhanced launch effects
        try:
            sound_path = os.path.join(project_root, "sounds", "sounds", "lunch_rocket.mp3")
            if os.path.exists(sound_path):
                launch_sound = pygame.mixer.Sound(sound_path)
                launch_sound.play()
            else:
                print(f"🔊 Launch sound not found at {sound_path}")
        except Exception as e:
            print(f"🔊 Launch sound error: {e}")

    def update_transition(self, dt):
        """Enhanced transition system with multiple phases"""
        if not self.transition_active:
            return False

        self.transition_timer += dt
        progress = self.transition_timer / self.transition_duration

        # Phase management
        if progress < 0.3:
            self.transition_phase = "countdown"
        elif progress < 0.6:
            self.transition_phase = "launch"
        elif progress < 0.9:
            self.transition_phase = "travel"
        else:
            self.transition_phase = "arrival"

        # Complete transition
        if self.transition_timer >= self.transition_duration:
            self.transition_active = False
            self.level_manager.game_state = GameState.LEVEL_TWO

            # Launch Mars level - this should return control to main game loop
            print("🔴 Launching Mars level!")
            mars_completed = run_mars_level()  # Use the function instead of direct instantiation

            # After returning from Mars level
            if mars_completed:
                print("🔴 Successfully completed Mars level!")
                self.level_completed = True
                self.exit_reason = "victory"
                self.running = False
            else:
                print("🔴 Failed Mars level")
                # Initialize Level Two content
                self.initialize_level_content(2)

            return True

        return False

    def update_game(self, dt):
        """Enhanced game update with improved spacecraft system"""
        # Skip updates if game is paused
        if self.paused:
            return

        # Handle transition if active
        if self.transition_active:
            self.update_transition(dt)
            return  # Skip other updates during transition

        # Check for game over condition
        if self.player and self.player.health <= 0:
            self.exit_reason = "game_over"
            self.running = False
            return

        # Update player if it exists
        if self.player:
            self.player.update()

        # Level-specific updates
        if self.level_manager.game_state == GameState.LEVEL_ONE:
            self.handle_spacecraft_collection(dt)
            if hasattr(self.game_logic, 'update_gameplay'):
                self.game_logic.update_gameplay(
                    self.player, self.inventory, self.ui,
                    self.level_manager, self.bg_manager, dt
                )

        elif self.level_manager.game_state in [GameState.LEVEL_TWO, GameState.LEVEL_THREE]:
            if hasattr(self.game_logic, 'update_gameplay'):
                self.game_logic.update_gameplay(
                    self.player, self.inventory, self.ui,
                    self.level_manager, self.bg_manager, dt
                )


    def handle_gameplay_events(self, event):
        """Enhanced event handling for gameplay"""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.paused = not self.paused
            return

        if self.paused and event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            sound_button, exit_button = self.draw_pause_menu()

            if sound_button.collidepoint(mouse_pos):
                self.sound_on = not self.sound_on
                if self.sound_on:
                    pygame.mixer.music.set_volume(1.0)
                else:
                    pygame.mixer.music.set_volume(0.0)

            if exit_button.collidepoint(mouse_pos):
                self.exit_reason = "exit_to_main"
                self.running = False
                return True

        if self.paused:
            return

        result = self.event_handler.handle_gameplay_events(
            event, self.level_manager.game_state, self.ui,
            self.player, self.level_manager
        )

        if result.get('action') == 'exit':
            self.exit_reason = "exit_to_main"
            self.running = False
            return

        elif result.get('next_level_requested'):
            advancement = self.game_logic.handle_level_progression(
                self.level_manager, self.inventory
            )
            if advancement == "level_advanced":
                level_info = self.level_manager.get_level_info()
                self.initialize_level_content(level_info['current_level'])
                if level_info['current_level'] > 1:  # Completed Level 1
                    self.level_completed = True
                    self.exit_reason = "victory"
                    self.running = False

        elif result.get('restart_requested'):
            restart_result = self.game_logic.handle_restart(self.level_manager, self.ui)
            if restart_result[0] == "restart_level":
                self.initialize_level_content(restart_result[1])

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h and self.player:
                self.player.toggle_helmet()
                self.ui.show_message(f"Helmet {'ON' if self.player.helmet_on else 'OFF'}", 1.0)
            elif event.key == pygame.K_s and self.player and hasattr(self.player, 'toggle_space_suit'):
                self.player.toggle_space_suit()
                self.ui.show_message(f"Space Suit {'ON' if self.player.space_suit_on else 'OFF'}", 1.0)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.level_manager.game_state == GameState.LEVEL_ONE and self.parts_manager:
                mouse_pos = pygame.mouse.get_pos()
                if self.parts_manager.check_launch_button_click(mouse_pos, True):
                    self.start_mars_transition()


    def draw_enhanced_transition(self):
        """Enhanced transition effects with multiple phases"""
        if not self.transition_active:
            return

        # Base fade effect
        fade_alpha = min(255, int(255 * (self.transition_timer / self.transition_duration)))
        fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Phase-specific colors
        if self.transition_phase == "countdown":
            fade_surface.fill((20, 20, 60))  # Dark blue
        elif self.transition_phase == "launch":
            fade_surface.fill((60, 30, 0))  # Orange glow
        elif self.transition_phase == "travel":
            fade_surface.fill((0, 0, 40))  # Deep space
        else:  # arrival
            fade_surface.fill((60, 20, 20))  # Mars red

        fade_surface.set_alpha(fade_alpha)
        self.screen.blit(fade_surface, (0, 0))

        # Phase-specific text
        font_large = pygame.font.Font(None, 72)
        font_medium = pygame.font.Font(None, 48)

        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2

        if self.transition_phase == "countdown":
            countdown = max(1, int(4 - self.transition_timer * 3))
            main_text = font_large.render("🚀 LAUNCH SEQUENCE INITIATED 🚀", True, (255, 255, 255))
            countdown_text = font_large.render(str(countdown), True, (255, 100, 100))

        elif self.transition_phase == "launch":
            main_text = font_large.render("🔥 LIFTOFF! 🔥", True, (255, 200, 0))
            countdown_text = font_medium.render("Escaping Moon gravity...", True, (255, 255, 255))

        elif self.transition_phase == "travel":
            main_text = font_large.render("🌌 SPACE TRAVEL 🌌", True, (0, 255, 255))
            countdown_text = font_medium.render("Navigating to Mars...", True, (255, 255, 255))

        else:  # arrival
            main_text = font_large.render("🔴 MARS APPROACH 🔴", True, (255, 100, 100))
            countdown_text = font_medium.render("Preparing for landing...", True, (255, 200, 200))

        # Draw text
        main_rect = main_text.get_rect(center=(center_x, center_y - 50))
        countdown_rect = countdown_text.get_rect(center=(center_x, center_y + 20))

        self.screen.blit(main_text, main_rect)
        self.screen.blit(countdown_text, countdown_rect)

    def draw_pause_menu(self):
        """Draw a custom pause menu with sound toggle and exit options"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Dark semi-transparent layer
        self.screen.blit(overlay, (0, 0))

        # Draw pause menu panel
        panel_width, panel_height = 400, 300
        panel_x, panel_y = (SCREEN_WIDTH - panel_width) // 2, (SCREEN_HEIGHT - panel_height) // 2
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

    def draw_enhanced_spacecraft_info(self):
        """Enhanced spacecraft information display"""
        if (self.level_manager.game_state != GameState.LEVEL_ONE or
                not self.inventory or not self.parts_manager or self.transition_active):
            return

        # Use the parts manager's enhanced display
        self.parts_manager.draw_parts_status(self.screen)  # Removed self.inventory parameter

        # Additional enhancement info
        y_offset = 130
        font = pygame.font.Font(None, 28)

        # Mission objective
        objective_text = font.render("🎯 Mission: Explore Mars", True, (255, 255, 0))
        self.screen.blit(objective_text, (20, y_offset))

        # Spacecraft status
        if self.spacecraft_ready:
            status_text = font.render("✅ Spacecraft: READY FOR LAUNCH", True, (0, 255, 0))
        else:
            status_text = font.render("🔧 Spacecraft: UNDER CONSTRUCTION", True, (255, 200, 0))

        self.screen.blit(status_text, (20, y_offset + 25))

    def render_game(self):
        """Enhanced game rendering with proper layering - fixes player visibility"""
        # Clear the screen at the beginning of each frame
        self.screen.fill((0, 0, 0))

        if self.level_manager.game_state == GameState.CHARACTER_SELECTION:
            if hasattr(self.renderer, 'render_character_selection'):
                self.renderer.render_character_selection()

        elif self.level_manager.game_state in [GameState.LEVEL_ONE, GameState.LEVEL_TWO, GameState.LEVEL_THREE]:
            # PROPER DRAW ORDER:
            # 1. Draw background first
            if self.bg_manager:
                self.bg_manager.draw(self.screen)

            # 2. Draw parts (but not on top of player)
            if self.level_manager.game_state == GameState.LEVEL_ONE and self.parts_manager:
                self.parts_manager.draw(self.screen)

            # 3. Draw player using clean draw method to prevent duplicates
            if self.player:
                if hasattr(self.player, 'draw_clean'):
                    self.player.draw_clean(self.screen)
                else:
                    # Draw directly without temp surface if draw_clean doesn't exist
                    if self.player.facing_right:
                        self.screen.blit(self.player.image, (self.player.rect.x, self.player.rect.y))
                    else:
                        flipped = pygame.transform.flip(self.player.image, True, False)
                        self.screen.blit(flipped, (self.player.rect.x, self.player.rect.y))

            # 4. Draw UI elements last
            if hasattr(self.ui, 'draw'):
                self.ui.draw(self.screen)

            # Draw inventory if visible
            if self.inventory and hasattr(self.inventory, 'visible') and self.inventory.visible:
                self.inventory.render(self.screen)

            # Draw spacecraft info for Level One
            if self.level_manager.game_state == GameState.LEVEL_ONE and self.parts_manager:
                if not self.transition_active:
                    # Draw spacecraft info
                    self.draw_enhanced_spacecraft_info()

                    # Draw launch button
                    mouse_pos = pygame.mouse.get_pos()
                    self.parts_manager.draw_launch_button(self.screen, mouse_pos)

            # Draw transition effects (always on top)
            self.draw_enhanced_transition()

            # Draw pause menu if game is paused
            if self.paused:
                self.draw_pause_menu()

        elif self.level_manager.game_state == GameState.GAME_OVER:
            if hasattr(self.renderer, 'render_game_over'):
                self.renderer.render_game_over(self.ui)

        # Update display
        pygame.display.flip()

    def run(self):
        """Optimized main game loop"""
        self.handle_character_selection()

        while self.running:
            dt = self.clock.tick(self.fps) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_reason = "quit"
                    self.running = False
                    break

                result = self.handle_gameplay_events(event)
                if result:  # If we got a True return from event handling
                    return False  # Exit to main menu

            self.update_game(dt)
            self.render_game()

        # Return True only for victory, False for game over or exit to main menu
        return self.exit_reason == "victory"


# Entry point
if __name__ == "__main__":
    try:
        game = SpaceGameMain()
        game.run()
    except Exception as e:
        print(f"❌ Game error: {e}")
        import traceback
        traceback.print_exc()  # Print full error details
        pygame.quit()
        sys.exit(1)

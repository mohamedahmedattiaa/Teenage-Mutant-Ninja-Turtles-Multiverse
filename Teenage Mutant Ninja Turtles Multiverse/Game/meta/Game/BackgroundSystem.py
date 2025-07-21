import pygame
import random


class BackgroundManager:
    def __init__(self, screen_width, screen_height):
        """Initialize the background manager with screen dimensions"""
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Load background images
        try:
            self.moon_bg_original = pygame.image.load("images/moon_background.png").convert()
            self.mars_bg_original = pygame.image.load("images/Mars_background.png").convert()
        except pygame.error as e:
            print(f"Error loading background images: {e}")
            self.moon_bg_original = self.create_moon_background()
            self.mars_bg_original = self.create_mars_background()

        # Scale backgrounds
        self.moon_bg = self.scale_background_smooth(self.moon_bg_original)
        self.mars_bg = self.scale_background_smooth(self.mars_bg_original)

        # Store background widths for scrolling
        self.moon_width = self.moon_bg.get_width()
        self.mars_width = self.mars_bg.get_width()

        # Background offset
        self.bg_offset = 0.0
        self.speed = 5.0

        # Current planet (0: Moon, 1: Mars)
        self.current_planet = 0

        # Transition parameters
        self.transitioning = False
        self.transition_progress = 0.0
        self.transition_speed = 1.0

        # Movement state tracking
        self.moving = False
        self.facing_right = True

    def create_moon_background(self):
        """Create a moon background with gradient and stars"""
        bg = pygame.Surface((self.screen_width, self.screen_height))

        # Create gradient from dark blue to black
        for y in range(self.screen_height):
            ratio = y / self.screen_height
            color_val = int(50 * (1 - ratio))
            color = (color_val, color_val, color_val + 20)
            pygame.draw.line(bg, color, (0, y), (self.screen_width, y))

        # Add stars
        for _ in range(100):
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height // 2)
            pygame.draw.circle(bg, (255, 255, 255), (x, y), random.randint(1, 2))

        return bg

    def create_mars_background(self):
        """Create a Mars background with gradient"""
        bg = pygame.Surface((self.screen_width, self.screen_height))

        # Create reddish gradient
        for y in range(self.screen_height):
            ratio = y / self.screen_height
            red_val = int(120 + 60 * ratio)
            green_val = int(40 + 20 * ratio)
            blue_val = int(20 + 10 * ratio)
            color = (red_val, green_val, blue_val)
            pygame.draw.line(bg, color, (0, y), (self.screen_width, y))

        # Add Mars features
        for _ in range(20):
            x = random.randint(0, self.screen_width)
            y = random.randint(self.screen_height // 2, self.screen_height)
            size = random.randint(5, 15)
            color = (random.randint(80, 140), random.randint(30, 70), random.randint(10, 50))
            pygame.draw.circle(bg, color, (x, y), size)

        return bg

    def scale_background_smooth(self, bg_surface):
        """Scale background maintaining aspect ratio"""
        original_width = bg_surface.get_width()
        original_height = bg_surface.get_height()

        scale_factor = self.screen_height / original_height
        new_width = int(original_width * scale_factor)

        if new_width < self.screen_width:
            new_width = self.screen_width

        return pygame.transform.smoothscale(bg_surface, (new_width, self.screen_height))

    def update_with_keys(self, keys):
        """Update background position based on key input"""
        self.moving = False

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.bg_offset -= self.speed
            self.facing_right = True
            self.moving = True
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.bg_offset += self.speed
            self.facing_right = False
            self.moving = True

    def update(self, dt):
        """Update background (for transitions)"""
        if self.transitioning:
            self.transition_progress += dt * self.transition_speed
            if self.transition_progress >= 1.0:
                self.transitioning = False
                self.transition_progress = 1.0
                self.current_planet = 1

    def start_mars_transition(self):
        """Start transition to Mars background"""
        if not self.transitioning and self.current_planet == 0:
            self.transitioning = True
            self.transition_progress = 0.0

    def draw_repeating_background(self, surface, bg_img, bg_width):
        """Draw repeating background with perfect tiling"""
        start_x = self.bg_offset % bg_width
        tiles_needed = (self.screen_width // bg_width) + 3

        for i in range(-1, tiles_needed):
            x_pos = start_x + i * bg_width
            surface.blit(bg_img, (x_pos, 0))

    def draw(self, surface):
        """Draw the appropriate backgrounds with smooth scrolling"""
        if not self.transitioning:
            if self.current_planet == 0:
                self.draw_repeating_background(surface, self.moon_bg, self.moon_width)
            else:
                self.draw_repeating_background(surface, self.mars_bg, self.mars_width)
        else:
            # Draw moon background first
            self.draw_repeating_background(surface, self.moon_bg, self.moon_width)

            # Create temporary surface for Mars background
            temp_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            self.draw_repeating_background(temp_surface, self.mars_bg, self.mars_width)

            # Apply alpha for smooth transition
            alpha = int(self.transition_progress * 255)
            temp_surface.set_alpha(alpha)
            surface.blit(temp_surface, (0, 0))

    def get_world_position(self, screen_x):
        """Convert screen position to world position"""
        return screen_x - self.bg_offset

    def get_screen_position(self, world_x):
        """Convert world position to screen position"""
        return world_x + self.bg_offset

    def is_moving(self):
        """Check if background is currently moving"""
        return self.moving

    def get_offset(self):
        """Get current background offset"""
        return self.bg_offset

    def reset_offset(self):
        """Reset background offset"""
        self.bg_offset = 0.0

    def get_movement_speed(self):
        """Get movement speed"""
        return self.speed
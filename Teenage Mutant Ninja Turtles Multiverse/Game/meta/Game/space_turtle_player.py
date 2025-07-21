import pygame
from sprits import Spritesheet


class SpaceTurtlePlayer(pygame.sprite.Sprite):
    def __init__(self, x, y, walk_sprite, light_attack_sprite,
                 jump_attack_sprite, ult_attack_sprite, shield_sprite, helmet_sprite):
        super().__init__()
        self.x = x
        self.y = y

        # Animation properties
        self.walk_frames = []
        self.light_attack_frames = []
        self.jump_attack_frames = []
        self.ult_attack_frames = []
        self.shield_frame = None
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_cooldown = 100

        # Load animation frames
        self._load_sprites(walk_sprite, light_attack_sprite, jump_attack_sprite,
                           ult_attack_sprite, shield_sprite, helmet_sprite)

        # Movement variables
        self.speed = 5
        self.gravity = 0.5
        self.velocity_y = 0
        self.jump_power = 12
        self.is_jumping = False
        self.facing_right = True
        self.ground_level = 720 - self.rect.height - 20  # 720 is screen height, 20 is padding

        # Combat states
        self.is_attacking = False
        self.is_leg_attacking = False
        self.is_ulting = False
        self.is_shielding = False

        # Character stats
        self.health = 100
        self.max_health = 100
        self.oxygen_level = 100
        self.max_oxygen = 100

        # Helmet and Space Suit (disabled as per requirements)
        self.helmet_on = False
        self.space_suit_on = False
        self.helmet_offset_x = max(0, (self.rect.width - 100) // 2)
        self.helmet_offset_y = max(0, (self.rect.height // 4) - 50)

        # Force initial positioning at ground level
        self.y = self.ground_level
        self.rect.y = int(self.y)

    def _load_sprites(self, walk_sprite, light_attack_sprite, jump_attack_sprite,
                      ult_attack_sprite, shield_sprite, helmet_sprite):
        """Load all sprite frames"""
        try:
            # Store original sprites for fallback
            self.walk_sprite_original = walk_sprite
            self.light_attack_sprite_original = light_attack_sprite
            self.jump_attack_sprite_original = jump_attack_sprite
            self.ult_attack_sprite_original = ult_attack_sprite
            self.shield_sprite_original = shield_sprite
            self.helmet_sprite = helmet_sprite

            # IMPORTANT: Get the actual dimensions of the sprite images
            # Different sprites may have different dimensions
            walk_width = walk_sprite.get_width() // 3  # Assuming 3 frames horizontally
            walk_height = walk_sprite.get_height()

            attack_width = light_attack_sprite.get_width() // 3  # Assuming 3 frames
            attack_height = light_attack_sprite.get_height()

            jump_width = jump_attack_sprite.get_width() // 2  # Assuming 2 frames
            jump_height = jump_attack_sprite.get_height()

            ult_width = ult_attack_sprite.get_width() // 4  # Assuming 4 frames
            ult_height = ult_attack_sprite.get_height()

            # Walk animation (3 frames)
            walk_sheet = Spritesheet(walk_sprite)
            for i in range(3):  # Assume 3 frames
                try:
                    self.walk_frames.append(walk_sheet.get_image(i, walk_width, walk_height, 1))
                except Exception as e:
                    print(f"Error loading walk frame {i}: {e}")
                    # Use original if frame extraction fails
                    self.walk_frames.append(walk_sprite)

            # Light attack (3 frames)
            attack_sheet = Spritesheet(light_attack_sprite)
            for i in range(3):  # Assume 3 frames
                try:
                    self.light_attack_frames.append(attack_sheet.get_image(i, attack_width, attack_height, 1))
                except Exception as e:
                    print(f"Error loading attack frame {i}: {e}")
                    self.light_attack_frames.append(light_attack_sprite)

            # Jump attack (2 frames)
            jump_sheet = Spritesheet(jump_attack_sprite)
            for i in range(2):  # Assume 2 frames
                try:
                    self.jump_attack_frames.append(jump_sheet.get_image(i, jump_width, jump_height, 1))
                except Exception as e:
                    print(f"Error loading jump frame {i}: {e}")
                    self.jump_attack_frames.append(jump_attack_sprite)

            # Ultimate attack (4 frames)
            ult_sheet = Spritesheet(ult_attack_sprite)
            for i in range(4):  # Assume 4 frames
                try:
                    self.ult_attack_frames.append(ult_sheet.get_image(i, ult_width, ult_height, 1))
                except Exception as e:
                    print(f"Error loading ult frame {i}: {e}")
                    self.ult_attack_frames.append(ult_attack_sprite)

            # Shield (single frame)
            shield_sheet = Spritesheet(shield_sprite)
            try:
                shield_width = shield_sprite.get_width()
                shield_height = shield_sprite.get_height()
                self.shield_frame = shield_sheet.get_image(0, shield_width, shield_height, 1)
            except Exception as e:
                print(f"Error loading shield frame: {e}")
                self.shield_frame = shield_sprite

            # Ensure we have at least one frame for each animation
            if not self.walk_frames:
                self.walk_frames = [walk_sprite]
            if not self.light_attack_frames:
                self.light_attack_frames = [light_attack_sprite]
            if not self.jump_attack_frames:
                self.jump_attack_frames = [jump_attack_sprite]
            if not self.ult_attack_frames:
                self.ult_attack_frames = [ult_attack_sprite]
            if not self.shield_frame:
                self.shield_frame = shield_sprite

            # Set initial image and rect
            self.image = self.walk_frames[0]
            self.rect = self.image.get_rect(topleft=(self.x, self.y))

        except Exception as e:
            print(f"Error loading player sprites: {e}")
            self._create_fallback_sprites()

    def _create_fallback_sprites(self):
        """Create simple colored rectangles as fallback"""
        # Create base fallback surface
        fallback = pygame.Surface((80, 100), pygame.SRCALPHA)
        fallback.fill((0, 255, 0, 200))
        pygame.draw.rect(fallback, (255, 255, 255), fallback.get_rect(), 2)

        # Add character shape to make it recognizable
        pygame.draw.circle(fallback, (255, 255, 255), (40, 30), 20, 2)  # Head
        pygame.draw.line(fallback, (255, 255, 255), (40, 50), (40, 70), 2)  # Body
        pygame.draw.line(fallback, (255, 255, 255), (40, 50), (20, 60), 2)  # Left arm
        pygame.draw.line(fallback, (255, 255, 255), (40, 50), (60, 60), 2)  # Right arm
        pygame.draw.line(fallback, (255, 255, 255), (40, 70), (30, 90), 2)  # Left leg
        pygame.draw.line(fallback, (255, 255, 255), (40, 70), (50, 90), 2)  # Right leg

        # Create different colored versions for different animations
        walk_fallback = fallback.copy()
        walk_fallback.fill((0, 220, 0, 200))

        attack_fallback = fallback.copy()
        attack_fallback.fill((220, 100, 0, 200))

        jump_fallback = fallback.copy()
        jump_fallback.fill((0, 100, 220, 200))

        ult_fallback = fallback.copy()
        ult_fallback.fill((220, 0, 220, 200))

        shield_fallback = fallback.copy()
        shield_fallback.fill((0, 150, 220, 200))

        # Set up animation frames
        self.walk_frames = [walk_fallback.copy() for _ in range(3)]
        self.light_attack_frames = [attack_fallback.copy() for _ in range(3)]
        self.jump_attack_frames = [jump_fallback.copy() for _ in range(2)]
        self.ult_attack_frames = [ult_fallback.copy() for _ in range(4)]
        self.shield_frame = shield_fallback

        # Add labels to each frame type
        font = pygame.font.SysFont('Arial', 10)
        for frame in self.walk_frames:
            text = font.render("WALK", True, (255, 255, 255))
            frame.blit(text, (20, 80))

        for frame in self.light_attack_frames:
            text = font.render("ATTACK", True, (255, 255, 255))
            frame.blit(text, (20, 80))

        for frame in self.jump_attack_frames:
            text = font.render("JUMP", True, (255, 255, 255))
            frame.blit(text, (20, 80))

        for frame in self.ult_attack_frames:
            text = font.render("ULT", True, (255, 255, 255))
            frame.blit(text, (20, 80))

        text = font.render("SHIELD", True, (255, 255, 255))
        self.shield_frame.blit(text, (20, 80))

        # Set initial image
        self.image = self.walk_frames[0]
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def toggle_helmet(self):
        # Helmet functionality removed as per requirements
        pass

    def toggle_space_suit(self):
        # Space suit functionality removed as per requirements
        pass

    def update(self):
        # Get keyboard input
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()

        # Reset movement state
        moved = False

        # Handle horizontal movement
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.x += self.speed
            self.facing_right = True
            moved = True
            if self.x > 1280 - self.rect.width:
                self.x = 1280 - self.rect.width

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.x -= self.speed
            self.facing_right = False
            moved = True
            if self.x < 0:
                self.x = 0

        # Handle jumping
        if (keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_SPACE]) and not self.is_jumping:
            self.velocity_y = -self.jump_power
            self.is_jumping = True
            moved = True

        # Apply gravity
        self.velocity_y += self.gravity
        self.y += self.velocity_y

        # Check if landed
        if self.y >= self.ground_level:
            self.y = self.ground_level
            self.velocity_y = 0
            self.is_jumping = False

        # Prevent going above the screen
        if self.y < 0:
            self.y = 0
            self.velocity_y = 0

        # Handle combat actions
        self.is_attacking = mouse_buttons[0] and not keys[pygame.K_LSHIFT]
        self.is_leg_attacking = mouse_buttons[0] and keys[pygame.K_LSHIFT]
        self.is_ulting = keys[pygame.K_e]
        self.is_shielding = mouse_buttons[2]

        # Update rect position
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        # Update animation based on current state
        self.update_animation(moved)

    def update_animation(self, moving):
        """Update animation frames based on current action"""
        current_time = pygame.time.get_ticks()

        # Only update animation after cooldown period
        if current_time - self.last_update >= self.animation_cooldown:
            self.last_update = current_time

            # Select animation based on priority
            if self.is_shielding:
                self.image = self.shield_frame
            elif self.is_ulting:
                self.current_frame = (self.current_frame + 1) % len(self.ult_attack_frames)
                self.image = self.ult_attack_frames[self.current_frame]
            elif self.is_leg_attacking:
                self.current_frame = (self.current_frame + 1) % len(self.jump_attack_frames)
                self.image = self.jump_attack_frames[self.current_frame]
            elif self.is_attacking:
                self.current_frame = (self.current_frame + 1) % len(self.light_attack_frames)
                self.image = self.light_attack_frames[self.current_frame]
            elif moving or self.is_jumping:
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames)
                self.image = self.walk_frames[self.current_frame]
            else:
                # Idle state - reset to first frame
                self.current_frame = 0
                self.image = self.walk_frames[0]

    def get_stats(self):
        """Return player stats for UI display"""
        return {
            'health': self.health,
            'max_health': self.max_health,
            'oxygen': self.oxygen_level,
            'max_oxygen': self.max_oxygen,
            'stamina': 100,  # Default stamina value
            'helmet_on': self.helmet_on,
            'space_suit_on': self.space_suit_on
        }

    def draw(self, surface):
        """Draw player without helmet and space suit as per requirements"""
        try:
            # Update rect position just to be sure
            self.rect.x = int(self.x)
            self.rect.y = int(self.y)

            # Get the correct image based on facing direction
            if self.facing_right:
                display_image = self.image
            else:
                display_image = pygame.transform.flip(self.image, True, False)

            # Draw player
            surface.blit(display_image, self.rect)

        except Exception as e:
            print(f"Error drawing player: {e}")
            # Fallback draw (simple rect)
            pygame.draw.rect(surface, (0, 255, 0), self.rect)

    # Use the same implementation for both drawing methods
    draw_clean = draw

    def set_position(self, x, y):
        """Helper method to forcibly set player position"""
        self.x = x
        self.y = y
        self.rect.x = int(x)
        self.rect.y = int(y)

    def reset_to_ground(self):
        """Reset player to ground level, useful when changing levels"""
        self.y = self.ground_level
        self.velocity_y = 0
        self.is_jumping = False
        self.rect.y = int(self.y)

# SpacecraftParts.py - Spacecraft parts collection system
import pygame
import random
import os
import math


class SpacecraftPart(pygame.sprite.Sprite):
    """Spacecraft part class with visual effects"""

    def __init__(self, x, y, part_name, part_number):
        super().__init__()
        self.part_name = part_name
        self.part_number = part_number

        # Get absolute project directory
        self.project_dir = self.find_project_root()
        print(f"Project directory: {self.project_dir}")

        # Try to load image from file first
        self.image = self.load_part_image(part_number)

        # If image loading failed, create default image
        if self.image is None:
            self.image = self.create_default_part_image(part_number)
            print(f"Created default image for {part_name} (Part {part_number})")
        else:
            print(f"Loaded image for {part_name} (Part {part_number})")

        self.image_path = f"part{part_number}.png"  # Path for reference
        self.original_image = self.image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Visual effects
        self.float_offset = 0
        self.glow_alpha = 100
        self.glow_direction = 1
        self.collected = False
        self.spawn_time = pygame.time.get_ticks()

        # Create glow surface
        self.glow_surface = pygame.Surface((self.rect.width + 40, self.rect.height + 40), pygame.SRCALPHA)

    def load_part_image(self, part_number):
        """Try to load part image from various possible locations"""
        possible_paths = [
            os.path.join(self.project_dir, "images", f"part{part_number}.png"),
            os.path.join(self.project_dir, "assets", "images", f"part{part_number}.png"),
            os.path.join(self.project_dir, "resources", "images", f"part{part_number}.png"),
            os.path.join(self.project_dir, f"part{part_number}.png"),
            os.path.join("images", f"part{part_number}.png"),
            os.path.join("assets", "images", f"part{part_number}.png")
        ]

        # Also try with different extensions
        for extension in [".jpg", ".jpeg", ".gif"]:
            possible_paths.append(os.path.join(self.project_dir, "images", f"part{part_number}{extension}"))
            possible_paths.append(os.path.join("images", f"part{part_number}{extension}"))

        for path in possible_paths:
            try:
                if os.path.exists(path):
                    print(f"Found image at {path}")
                    image = pygame.image.load(path).convert_alpha()

                    # Scale to appropriate size if needed
                    if image.get_width() > 100 or image.get_height() > 100:
                        image = pygame.transform.scale(image, (80, 80))

                    return image
            except Exception as e:
                print(f"Error loading image from {path}: {e}")

        # Create images folder if it doesn't exist
        try:
            images_dir = os.path.join(self.project_dir, "images")
            if not os.path.exists(images_dir):
                os.makedirs(images_dir)
                print(f"Created images directory at {images_dir}")
        except Exception as e:
            print(f"Error creating images directory: {e}")

        return None  # Image loading failed

    def find_project_root(self):
        """Find the project root directory by traversing up from current directory"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Start with current directory and go up until we find a recognizable project directory
        while True:
            # Check if this looks like our project root
            if (os.path.exists(os.path.join(current_dir, "leonardo_level.py")) or
                    os.path.exists(os.path.join(current_dir, "mars.py")) or
                    os.path.exists(os.path.join(current_dir, "level_manager.py"))):
                return current_dir

            # Go up one directory
            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir:  # Reached filesystem root
                return os.path.dirname(os.path.abspath(__file__))  # Fall back to current file's directory
            current_dir = parent_dir

    def create_default_part_image(self, part_number):
        """Create default part image with color coding and visually distinct designs"""
        surface = pygame.Surface((80, 80), pygame.SRCALPHA)

        # Different colors for each part
        colors = {
            1: (255, 100, 100),  # Red - Engine
            2: (100, 255, 100),  # Green - Navigation
            3: (100, 100, 255),  # Blue - Shield
            4: (255, 255, 100),  # Yellow - Fuel Tank
            5: (255, 100, 255),  # Purple - Scanner
            6: (100, 255, 255)  # Cyan - Weapon
        }

        color = colors.get(part_number, (255, 255, 255))

        # Make each part visually distinct based on number
        if part_number == 1:  # Engine - cylindrical shape
            pygame.draw.rect(surface, color, (15, 10, 50, 60), border_radius=5)
            pygame.draw.circle(surface, (50, 50, 50), (40, 70), 15)
            pygame.draw.circle(surface, (200, 200, 50), (40, 10), 15)

        elif part_number == 2:  # Navigation - satellite dish shape
            pygame.draw.circle(surface, color, (40, 50), 25)
            pygame.draw.arc(surface, (220, 220, 220), (15, 15, 50, 50), 0, 3.14, 5)
            pygame.draw.line(surface, (180, 180, 180), (40, 50), (40, 15), 3)

        elif part_number == 3:  # Shield - hexagonal shape
            points = []
            for i in range(6):
                angle = 3.14159 * 2 * i / 6
                points.append((40 + 30 * math.cos(angle),
                               40 + 30 * math.sin(angle)))
            pygame.draw.polygon(surface, color, points)
            pygame.draw.circle(surface, (50, 50, 150), (40, 40), 15)

        elif part_number == 4:  # Fuel Tank - circular tank
            pygame.draw.circle(surface, color, (40, 40), 30)
            pygame.draw.rect(surface, (100, 100, 100), (30, 10, 20, 60))
            pygame.draw.lines(surface, (50, 50, 50), False,
                              [(20, 25), (60, 25), (60, 55), (20, 55)], 2)

        else:  # Generic parts (5 and 6)
            pygame.draw.circle(surface, color, (40, 40), 30)
            pygame.draw.rect(surface, (255, 255, 255), (30, 20, 20, 40), 2)

        # Part number and border
        pygame.draw.circle(surface, (255, 255, 255), (40, 40), 30, 2)
        font = pygame.font.Font(None, 36)
        text = font.render(str(part_number), True, (255, 255, 255))
        text_rect = text.get_rect(center=(40, 40))
        surface.blit(text, text_rect)

        return surface

    def save_default_images(self):
        """Save default part images to files for future use"""
        try:
            images_dir = os.path.join(self.project_dir, "images")
            if not os.path.exists(images_dir):
                os.makedirs(images_dir)
                print(f"Created images directory at {images_dir}")

            # Save the current image
            image_path = os.path.join(images_dir, f"part{self.part_number}.png")
            pygame.image.save(self.image, image_path)
            print(f"Saved image to {image_path}")

            return True
        except Exception as e:
            print(f"Error saving image: {e}")
            return False

    def update(self, dt):
        """Update part animations"""
        if not self.collected:
            # Floating animation
            self.float_offset += dt * 3
            float_y = int(8 * math.sin(self.float_offset))

            # Glow pulsing effect
            self.glow_alpha += self.glow_direction * dt * 150
            if self.glow_alpha >= 255:
                self.glow_alpha = 255
                self.glow_direction = -1
            elif self.glow_alpha <= 80:
                self.glow_alpha = 80
                self.glow_direction = 1

    def draw(self, screen):
        """Draw part with glow effect"""
        if not self.collected:
            # Calculate floating position
            float_y = int(8 * math.sin(self.float_offset))
            draw_rect = self.rect.copy()
            draw_rect.y += float_y

            # Draw glow effect
            glow_rect = pygame.Rect(draw_rect.x - 20, draw_rect.y - 20,
                                    self.rect.width + 40, self.rect.height + 40)

            # Create glow surface
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            glow_color = (0, 255, 255, int(self.glow_alpha * 0.4))
            pygame.draw.ellipse(glow_surface, glow_color, (0, 0, glow_rect.width, glow_rect.height))
            screen.blit(glow_surface, glow_rect.topleft)

            # Draw the part
            screen.blit(self.image, draw_rect)

            # Draw collection hint
            current_time = pygame.time.get_ticks()
            if (current_time - self.spawn_time) % 3000 < 1500:  # Blink every 3 seconds
                font = pygame.font.Font(None, 24)
                hint_text = font.render("Press SPACE", True, (255, 255, 255))
                hint_rect = hint_text.get_rect(center=(draw_rect.centerx, draw_rect.y - 30))

                # Draw background for text
                bg_rect = hint_rect.inflate(10, 4)
                pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect, border_radius=3)
                screen.blit(hint_text, hint_rect)

    def collect(self):
        """Collect the part and return part info"""
        self.collected = True
        part_names = {
            1: "Engine",
            2: "Navigation System",
            3: "Shield Generator",
            4: "Fuel Tank"
        }

        part_descriptions = {
            1: "Propulsion system for interplanetary travel",
            2: "Guidance system for Mars trajectory",
            3: "Protects against cosmic radiation",
            4: "Stores fuel for the journey to Mars"
        }

        name = part_names.get(self.part_number, f"Unknown Part {self.part_number}")
        description = part_descriptions.get(self.part_number, "Essential spacecraft component")

        return {
            "name": f"Spacecraft {name}",
            "image": self.image.copy(),
            "description": description,
            "part_number": self.part_number
        }


class SpacecraftPartsManager:
    """Manager for all spacecraft parts"""

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.parts = pygame.sprite.Group()
        self.collection_sound = None
        self.launch_button_visible = False
        self.launch_button_rect = None

        # Collection tracking (replacing inventory)
        self.collected_parts = []
        self.parts_panel_visible = False

        # Task completion tracking
        self.tasks_completed = [False, False, False, False, False]
        self.task_completion_time = [0, 0, 0, 0, 0]  # For animations

        # Mission menu panel
        self.mission_panel_rect = pygame.Rect(
            self.screen_width - 320, 20, 300, 400
        )

        # Part names for display with better naming
        self.part_names = [
            "Engine",
            "Navigation System",
            "Shield Generator",
            "Fuel Tank"
        ]

        # Part descriptions
        self.part_descriptions = [
            "Main propulsion system",
            "Guidance and trajectory control",
            "Protection from radiation",
            "Stores fuel for the journey"
        ]

        # Tasks list
        self.tasks = [
            "Collect Engine",
            "Collect Navigation System",
            "Collect Shield Generator",
            "Collect Fuel Tank",
            "Launch to Mars"
        ]

        # Try to load collection sound - will be skipped if not found
        try:
            sound_path = self.find_sound_file("collect.wav")
            if sound_path:
                self.collection_sound = pygame.mixer.Sound(sound_path)
                print("Loaded collection sound")
        except:
            print("Collection sound not found, continuing without sound")

    def find_sound_file(self, filename):
        """Try to find sound file in various locations"""
        possible_paths = [
            os.path.join("sounds", filename),
            os.path.join("assets", "sounds", filename),
            os.path.join("resources", "sounds", filename),
            os.path.join(os.path.dirname(__file__), "sounds", filename),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "sounds", filename)
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None

    def generate_parts(self):
        """Generate 4 spacecraft parts in different locations"""
        self.parts.empty()

        # Predefined positions for good distribution across the level
        positions = [
            (150, 400),  # Left side - Part 1
            (400, 250),  # Center-left, elevated - Part 2
            (650, 450),  # Center-right - Part 3
            (900, 200),  # Right side, elevated - Part 4
        ]

        # Create parts
        for i in range(4):
            base_x, base_y = positions[i]

            # Add random offset
            x = base_x + random.randint(-30, 30)
            y = base_y + random.randint(-20, 20)

            # Ensure parts stay within screen bounds
            x = max(60, min(x, self.screen_width - 120))
            y = max(100, min(y, self.screen_height - 200))

            # Create part
            part_number = i + 1
            part_name = self.part_names[i]
            part = SpacecraftPart(x, y, part_name, part_number)

            # Save the default image if it was generated and not loaded
            if not os.path.exists(os.path.join(part.project_dir, "images", f"part{part_number}.png")):
                part.save_default_images()

            self.parts.add(part)

            print(f"Generated {part_name} (Part {part_number}) at position ({x}, {y})")

        print(f"Loaded {len(self.parts)} spacecraft parts")

    def check_collection(self, player_rect, parts_manager=None, keys_pressed=None):
        """Check for part collection by player - does not use inventory"""
        collected_parts = []

        for part in self.parts:
            if not part.collected and player_rect.colliderect(part.rect):
                # Check if SPACE key is pressed for collection
                if keys_pressed and keys_pressed[pygame.K_SPACE]:
                    # Get part info
                    part_info = part.collect()

                    # Add to collected parts
                    self.collected_parts.append({
                        "name": part_info["name"],
                        "image": part_info["image"],
                        "description": part_info["description"],
                        "part_number": part_info["part_number"],
                        "quantity": 1
                    })

                    collected_parts.append(part)

                    # Update task completion
                    self.tasks_completed[part.part_number - 1] = True
                    self.task_completion_time[part.part_number - 1] = pygame.time.get_ticks()

                    # Play collection sound
                    if self.collection_sound:
                        self.collection_sound.play()

                    print(f"✨ Collected: {part.part_name} (Part {part.part_number})!")

                    # Make parts panel visible briefly
                    self.parts_panel_visible = True

                    # Check if all parts collected
                    if self.all_parts_collected():
                        self.show_launch_button()

        return collected_parts

    def show_launch_button(self):
        """Show the launch button when all parts are collected"""
        self.launch_button_visible = True
        button_width = 200
        button_height = 60
        self.launch_button_rect = pygame.Rect(
            self.screen_width // 2 - button_width // 2,
            self.screen_height - 150,
            button_width,
            button_height
        )
        print("🚀 All parts collected! Launch button is now available!")

    def draw_launch_button(self, screen, mouse_pos=None):
        """Draw the launch to Mars button with rocket.png"""
        if not self.launch_button_visible or not self.launch_button_rect:
            return False

        # If mouse_pos is not provided, get the current mouse position
        if mouse_pos is None:
            mouse_pos = pygame.mouse.get_pos()

        # Check if mouse is hovering over button
        is_hovering = self.launch_button_rect.collidepoint(mouse_pos)

        # Button colors
        button_color = (0, 150, 0) if is_hovering else (0, 100, 0)
        border_color = (0, 255, 0) if is_hovering else (0, 200, 0)
        text_color = (255, 255, 255)

        # Draw button background
        pygame.draw.rect(screen, button_color, self.launch_button_rect, border_radius=10)

        # Draw button border
        pygame.draw.rect(screen, border_color, self.launch_button_rect, 3, border_radius=10)

        # Draw button text
        font = pygame.font.Font(None, 36)
        text = font.render("LAUNCH", True, text_color)
        text_rect = text.get_rect(center=self.launch_button_rect.center)
        screen.blit(text, text_rect)

        # Add glow effect when hovering
        if is_hovering:
            glow_rect = self.launch_button_rect.inflate(10, 10)
            pygame.draw.rect(screen, (100, 255, 100, 50), glow_rect, border_radius=12)

        # Draw rocket image
        try:
            rocket_img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", "rocket.png")
            if hasattr(self, 'rocket_img') and self.rocket_img:
                rocket_img = self.rocket_img
            else:
                if os.path.exists(rocket_img_path):
                    self.rocket_img = pygame.image.load(rocket_img_path).convert_alpha()
                    rocket_img = self.rocket_img
                else:
                    # Create a fallback rocket image
                    rocket_img = pygame.Surface((100, 150), pygame.SRCALPHA)
                    pygame.draw.polygon(rocket_img, (255, 200, 0), [
                        (50, 0),
                        (100, 100),
                        (75, 150),
                        (25, 150),
                        (0, 100),
                    ])
                    self.rocket_img = rocket_img

            # Calculate position for rocket image (above the launch button)
            rocket_y_offset = int(4 * math.sin(pygame.time.get_ticks() / 200))  # Floating effect
            rocket_rect = rocket_img.get_rect(
                midbottom=(self.launch_button_rect.centerx, self.launch_button_rect.top - 20 + rocket_y_offset)
            )
            screen.blit(rocket_img, rocket_rect)

        except Exception as e:
            print(f"Error drawing rocket image: {e}")
            # Fallback to simple polygon rocket if image loading fails
            rocket_y_offset = int(4 * math.sin(pygame.time.get_ticks() / 200))
            rocket_rect = pygame.Rect(
                self.launch_button_rect.centerx - 25,
                self.launch_button_rect.top - 80 + rocket_y_offset,
                50, 60
            )
            pygame.draw.polygon(screen, (255, 200, 0), [
                (rocket_rect.centerx, rocket_rect.top),
                (rocket_rect.right, rocket_rect.centery + 10),
                (rocket_rect.centerx + 10, rocket_rect.bottom),
                (rocket_rect.centerx - 10, rocket_rect.bottom),
                (rocket_rect.left, rocket_rect.centery + 10),
            ])

        return is_hovering

    def check_launch_button_click(self, mouse_pos, mouse_clicked):
        """Check if launch button was clicked"""
        if (self.launch_button_visible and self.launch_button_rect and
                mouse_clicked and self.launch_button_rect.collidepoint(mouse_pos)):
            # Update final task completion
            self.tasks_completed[4] = True
            self.task_completion_time[4] = pygame.time.get_ticks()
            return True
        return False

    def update(self, dt):
        """Update all parts"""
        for part in self.parts:
            part.update(dt)

    def draw(self, screen):
        """Draw all parts"""
        for part in self.parts:
            part.draw(screen)

    def draw_mission_panel(self, screen):
        """Draw mission panel with task list in a modern UI style - without inventory"""
        # Get parts count
        parts_count = len(self.collected_parts)
        collected_part_numbers = [part["part_number"] for part in self.collected_parts]

        # Calculate animation progress for tasks
        current_time = pygame.time.get_ticks()

        # Panel background with glass effect
        panel_rect = self.mission_panel_rect
        pygame.draw.rect(screen, (20, 30, 50, 230), panel_rect, border_radius=15)
        pygame.draw.rect(screen, (100, 140, 240), panel_rect, 2, border_radius=15)

        # Add highlight at the top (glass effect)
        highlight_rect = pygame.Rect(panel_rect.x + 10, panel_rect.y + 5, panel_rect.width - 20, 5)
        pygame.draw.rect(screen, (150, 180, 255, 100), highlight_rect, border_radius=5)

        # Title
        title_font = pygame.font.Font(None, 36)
        title = title_font.render("MISSION: MARS LAUNCH", True, (255, 255, 255))
        title_rect = title.get_rect(centerx=panel_rect.centerx, top=panel_rect.y + 15)
        screen.blit(title, title_rect)

        # Divider
        pygame.draw.line(screen, (100, 140, 240),
                         (panel_rect.x + 20, title_rect.bottom + 10),
                         (panel_rect.right - 20, title_rect.bottom + 10), 2)

        # Tasks list
        task_font = pygame.font.Font(None, 24)
        y_offset = title_rect.bottom + 30

        for i, task in enumerate(self.tasks):
            # Determine task status
            completed = self.tasks_completed[i]

            # Calculate animation effects for recent completions
            animation_time = current_time - self.task_completion_time[i]
            highlight = animation_time < 2000 and completed

            # Background for task row
            row_rect = pygame.Rect(panel_rect.x + 15, y_offset, panel_rect.width - 30, 32)

            if highlight:
                # Pulse animation for recently completed tasks
                pulse = int(127 + 127 * math.sin(animation_time / 200))
                row_color = (0, pulse // 2, pulse // 3, 150)
            else:
                row_color = (60, 80, 120, 150) if completed else (40, 50, 70, 150)

            pygame.draw.rect(screen, row_color, row_rect, border_radius=5)

            # Task number and checkmark
            if completed:
                status_text = "✓"
                status_color = (0, 255, 0)
            else:
                status_text = f"{i + 1}."
                status_color = (200, 200, 200)

            status = task_font.render(status_text, True, status_color)
            screen.blit(status, (panel_rect.x + 25, y_offset + 8))

            # Task text
            task_color = (255, 255, 255) if completed else (180, 180, 180)
            text = task_font.render(task, True, task_color)
            screen.blit(text, (panel_rect.x + 50, y_offset + 8))

            # Add little icon for each task
            icon_rect = pygame.Rect(panel_rect.right - 40, y_offset + 2, 28, 28)

            if i < 4:  # Part collection tasks
                # Show part icon or empty box
                part_collected = (i + 1) in collected_part_numbers

                if part_collected:
                    # Try to find the part and draw its image
                    for part in self.parts:
                        if part.part_number == i + 1:
                            small_img = pygame.transform.scale(part.image, (24, 24))
                            screen.blit(small_img, icon_rect)
                            break
                    else:
                        # If part not found, draw a colored square
                        colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255), (255, 255, 100)]
                        pygame.draw.rect(screen, colors[i], icon_rect, border_radius=3)
                else:
                    # Empty box
                    pygame.draw.rect(screen, (100, 100, 100, 128), icon_rect, 2, border_radius=3)

            elif i == 4:  # Launch task
                # Rocket icon
                if completed:
                    # Animated rocket
                    rocket_y = int(4 * math.sin(pygame.time.get_ticks() / 200))
                    rocket_color = (255, 200, 0)
                else:
                    rocket_y = 0
                    rocket_color = (150, 150, 150)

                # Draw simplified rocket
                rocket_points = [
                    (icon_rect.centerx, icon_rect.y + rocket_y),
                    (icon_rect.right, icon_rect.centery + 5 + rocket_y),
                    (icon_rect.centerx, icon_rect.bottom + rocket_y),
                    (icon_rect.left, icon_rect.centery + 5 + rocket_y)
                ]
                pygame.draw.polygon(screen, rocket_color, rocket_points)

            y_offset += 40

        # Progress summary at bottom
        progress_rect = pygame.Rect(panel_rect.x + 15, panel_rect.bottom - 60,
                                    panel_rect.width - 30, 40)
        pygame.draw.rect(screen, (30, 40, 60, 200), progress_rect, border_radius=8)

        # Progress text
        progress_text = f"Progress: {parts_count}/4 parts collected"
        progress_font = pygame.font.Font(None, 28)
        text = progress_font.render(progress_text, True, (255, 255, 255))
        screen.blit(text, (progress_rect.x + 10, progress_rect.y + 10))

        # Progress bar
        bar_rect = pygame.Rect(panel_rect.x + 15, panel_rect.bottom - 90,
                               panel_rect.width - 30, 15)
        pygame.draw.rect(screen, (40, 40, 40), bar_rect, border_radius=7)

        if parts_count > 0:
            fill_width = int(bar_rect.width * (parts_count / 4))
            fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, fill_width, bar_rect.height)

            if parts_count >= 4:
                color = (0, 255, 100)  # Green when complete
                # Add pulsing effect when complete
                pulse = int(127 + 127 * math.sin(pygame.time.get_ticks() / 200))
                pygame.draw.rect(screen, (0, pulse, 0), fill_rect, border_radius=7)
            else:
                # Gradient from yellow to green based on progress
                r = int(255 - (155 * parts_count / 4))
                g = 255
                color = (r, g, 0)
                pygame.draw.rect(screen, color, fill_rect, border_radius=7)

        # Border
        pygame.draw.rect(screen, (200, 200, 200), bar_rect, 1, border_radius=7)

    def draw_parts_status(self, screen):
        """Draw parts collection status without inventory"""
        # Use the mission panel instead of the old status display
        self.draw_mission_panel(screen)

    def render_parts_panel(self, screen, x=900, y=50, width=350, height=600):
        """Render the parts panel (replacement for inventory.render)"""
        if not self.parts_panel_visible:
            return

        # Background and border
        pygame.draw.rect(screen, (30, 30, 40), (x, y, width, height), border_radius=10)
        pygame.draw.rect(screen, (70, 70, 90), (x, y, width, height), 2, border_radius=10)

        # Panel title
        title_font = pygame.font.SysFont('Arial', 24)
        title = title_font.render("SPACECRAFT PARTS", True, (255, 215, 0))
        screen.blit(title, (x + (width - title.get_width()) // 2, y + 10))

        # List collected parts
        item_font = pygame.font.SysFont('Arial', 18)
        desc_font = pygame.font.SysFont('Arial', 14)
        item_y = y + 50

        if not self.collected_parts:
            # No parts collected yet
            text = item_font.render("No parts collected yet", True, (200, 200, 200))
            screen.blit(text, (x + 20, item_y + 20))
        else:
            # Display each collected part
            for i, part in enumerate(self.collected_parts):
                # Item background
                row_color = (50, 50, 60, 150) if i == 0 else (40, 40, 50, 150)
                row_rect = pygame.Rect(x + 10, item_y, width - 20, 50)
                pygame.draw.rect(screen, row_color, row_rect, border_radius=5)

                # Part image if available
                if part["image"]:
                    img_rect = part["image"].get_rect(center=(x + 30, item_y + 25))
                    screen.blit(part["image"], img_rect)

                # Part name and quantity
                name_text = item_font.render(f"{part['name']} x{part.get('quantity', 1)}", True, (255, 255, 255))
                screen.blit(name_text, (x + 60, item_y + 10))

                # Description
                desc_text = desc_font.render(part.get("description", ""), True, (200, 200, 200))
                screen.blit(desc_text, (x + 60, item_y + 30))

                item_y += 55

        # Parts count at bottom
        parts_count = len(self.collected_parts)
        parts_text = item_font.render(f"Spacecraft Parts: {parts_count}/4", True, (0, 255, 255))
        screen.blit(parts_text, (x + 10, y + height - 30))

    def toggle_parts_panel(self):
        """Toggle visibility of parts panel (replaces inventory.toggle_visibility)"""
        self.parts_panel_visible = not self.parts_panel_visible
        return self.parts_panel_visible

    def get_spacecraft_parts_count(self):
        """Get count of collected spacecraft parts (replaces inventory.get_spacecraft_parts_count)"""
        return len(self.collected_parts)

    def get_remaining_parts_count(self):
        """Get number of remaining parts"""
        return len([part for part in self.parts if not part.collected])

    def all_parts_collected(self):
        """Check if all parts are collected"""
        return self.get_remaining_parts_count() == 0

    def reset_parts(self):
        """Reset all parts for new game"""
        self.launch_button_visible = False
        self.launch_button_rect = None
        self.tasks_completed = [False, False, False, False, False]
        self.task_completion_time = [0, 0, 0, 0, 0]
        self.collected_parts = []
        self.parts_panel_visible = False
        self.generate_parts()


# Test the system when file is run directly
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Spacecraft Parts Collection Test")
    clock = pygame.time.Clock()

    # Initialize systems
    parts_manager = SpacecraftPartsManager(1280, 720)
    parts_manager.generate_parts()

    # Player rectangle for testing
    player_rect = pygame.Rect(100, 500, 50, 80)
    player_speed = 300

    print("🌙 Test Mode: Use arrow keys to move, SPACE to collect parts")
    print("🚀 Collect all 4 parts to see the launch button!")
    print("📦 Press 'I' to toggle parts panel view")

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    parts_manager.toggle_parts_panel()
                    print(f"Parts panel {'shown' if parts_manager.parts_panel_visible else 'hidden'}")
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if parts_manager.check_launch_button_click(mouse_pos, True):
                    print("🚀 LAUNCHING TO MARS! 🚀")

        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_rect.x -= player_speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_rect.x += player_speed * dt
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player_rect.y -= player_speed * dt
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player_rect.y += player_speed * dt

        # Keep player on screen
        player_rect.clamp_ip(pygame.Rect(0, 0, 1280, 720))

        # Update and check collection
        parts_manager.update(dt)
        parts_manager.check_collection(player_rect, parts_manager, keys)

        # Draw everything
        screen.fill((20, 25, 40))  # Dark space background

        # Draw parts
        parts_manager.draw(screen)

        # Draw player
        pygame.draw.rect(screen, (255, 255, 255), player_rect)
        pygame.draw.circle(screen, (0, 255, 255), player_rect.center, 3)

        # Draw mission panel
        parts_manager.draw_parts_status(screen)

        # Draw launch button
        mouse_pos = pygame.mouse.get_pos()
        parts_manager.draw_launch_button(screen, mouse_pos)

        # Draw parts panel if visible
        if parts_manager.parts_panel_visible:
            parts_manager.render_parts_panel(screen)

        # Draw basic instructions
        font = pygame.font.Font(None, 24)
        instructions = [
            "Arrow keys or WASD to move",
            "SPACE near parts to collect",
            "Press I to view parts panel",
            "Click launch button when ready"
        ]
        for i, instruction in enumerate(instructions):
            text = font.render(instruction, True, (200, 200, 200))
            screen.blit(text, (20, 650 + i * 20))

        pygame.display.flip()

    pygame.quit()

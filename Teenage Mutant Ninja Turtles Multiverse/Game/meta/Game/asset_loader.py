# asset_loader.py
import pygame
import os


class AssetLoader:
    """Handles loading and managing game assets"""

    def __init__(self):
        self.sprites = {}
        self.sounds = {}

    def load_player_sprites(self):
        """Load all player sprite assets"""
        try:
            self.sprites['walk'] = pygame.image.load('images/main.png').convert_alpha()
            self.sprites['light_attack'] = pygame.image.load('images/ult.png').convert_alpha()
            self.sprites['jump_attack'] = pygame.image.load('images/LegAttack.png').convert_alpha()
            self.sprites['ult_attack'] = pygame.image.load('images/TornadoAttack.png').convert_alpha()
            self.sprites['shield'] = pygame.image.load('images/Safe.png').convert_alpha()
            return True
        except pygame.error as e:
            print(f"Error loading player sprites: {e}")
            return False

    def load_item_sprites(self):
        """Load inventory item sprites, skip missing files"""
        parts_loaded = 0

        for i in range(1, 7):
            part_name = f'part{i}'
            image_path = f'images/{part_name}.png'

            try:
                if os.path.exists(image_path):
                    self.sprites[part_name] = pygame.image.load(image_path).convert_alpha()
                    parts_loaded += 1
                    print(f"Loaded {part_name}")
                else:
                    print(f"Skipping {part_name} - file not found")
            except pygame.error as e:
                print(f"Error loading {part_name}: {e}")

        print(f"Loaded {parts_loaded}/6 spacecraft parts")
        return True  # Always return True since missing parts are optional

    def create_space_helmet(self):
        """Create the space helmet sprite"""
        helmet = pygame.Surface((300, 300), pygame.SRCALPHA)
        glass_color = (173, 216, 230, 180)
        frame_color = (200, 200, 200, 255)

        pygame.draw.circle(helmet, frame_color, (150, 150), 120, 20)
        pygame.draw.circle(helmet, glass_color, (150, 150), 100)
        pygame.draw.rect(helmet, frame_color, (145, 240, 10, 30))
        pygame.draw.circle(helmet, frame_color, (150, 270), 15)
        pygame.draw.arc(helmet, (255, 255, 255, 100), (70, 70, 160, 160), 0.7, 2.5, 5)

        self.sprites['helmet'] = helmet
        return helmet

    def get_sprite(self, name):
        """Get a sprite by name"""
        return self.sprites.get(name)

    def load_all_assets(self):
        """Load all game assets"""
        success = True
        success &= self.load_player_sprites()
        success &= self.load_item_sprites()
        self.create_space_helmet()
        return success
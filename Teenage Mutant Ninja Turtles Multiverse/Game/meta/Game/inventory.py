import pygame
from pygame import Rect
import os
import json
import pickle


class InventoryItem:
    def __init__(self, name, image_path, description="", is_key_item=False):
        self.name = name
        try:
            self.image = pygame.image.load(image_path).convert_alpha()
        except (pygame.error, FileNotFoundError) as e:
            print(f"Warning: Could not load image {image_path}: {e}")
            # Create better fallback image with part number indicator
            self.image = self._create_fallback_image(name)
        self.description = description
        self.is_key_item = is_key_item
        self.quantity = 1

    def _create_fallback_image(self, name):
        """Create a visually distinct fallback image for missing part images"""
        # Extract part number if present in the name
        part_num = None
        if "Part" in name and name.split()[-1].isdigit():
            part_num = int(name.split()[-1])

        # Create surface with size appropriate for inventory
        surf = pygame.Surface((64, 64), pygame.SRCALPHA)

        # Background color based on part number (if available)
        if part_num:
            colors = [
                (255, 100, 100),  # Red (Part 1)
                (100, 255, 100),  # Green (Part 2)
                (100, 100, 255),  # Blue (Part 3)
                (255, 255, 100),  # Yellow (Part 4)
            ]
            color_idx = min(part_num - 1, len(colors) - 1)
            bg_color = colors[color_idx]
        else:
            bg_color = (200, 200, 200)  # Gray default

        # Fill with semi-transparent color
        surf.fill(bg_color + (200,))

        # Add border
        pygame.draw.rect(surf, (255, 255, 255), surf.get_rect(), 2)

        # Add text label
        font = pygame.font.SysFont('Arial', 14)
        if part_num:
            text = font.render(f"PART {part_num}", True, (255, 255, 255))
        else:
            text = font.render("ITEM", True, (255, 255, 255))

        text_rect = text.get_rect(center=(32, 32))
        surf.blit(text, text_rect)

        # Add decorative elements based on part number
        if part_num:
            # Draw different shapes based on part number
            if part_num == 1:  # Engine - draw flames
                pygame.draw.polygon(surf, (255, 165, 0), [(20, 48), (32, 60), (44, 48)])
            elif part_num == 2:  # Navigation - draw compass/radar
                pygame.draw.circle(surf, (255, 255, 255), (32, 22), 12, 2)
                pygame.draw.line(surf, (255, 255, 255), (32, 22), (32, 10), 2)
            elif part_num == 3:  # Shield - draw shield shape
                pygame.draw.polygon(surf, (255, 255, 255), [(20, 15), (44, 15), (44, 30), (32, 45), (20, 30)], 2)
            elif part_num == 4:  # Fuel - draw fuel tank
                pygame.draw.rect(surf, (255, 255, 255), (25, 15, 14, 30), 2)
                pygame.draw.rect(surf, (255, 255, 255), (27, 18, 10, 24))

        return surf

    def __str__(self):
        return f"{self.name} (x{self.quantity}) - {self.description}"


class Inventory:
    def __init__(self, capacity=10):
        self.items = []
        self.capacity = capacity
        self.selected_index = 0
        self.visible = False
        self.font = pygame.font.SysFont('Arial', 18)
        self.desc_font = pygame.font.SysFont('Arial', 14)
        self.save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_inventory.dat")

        # Try to load saved inventory on initialization
        self.load_inventory()

    def add_item(self, item):
        for existing_item in self.items:
            if existing_item.name == item.name:
                existing_item.quantity += 1
                self.save_inventory()  # Save after modifying inventory
                return True

        if len(self.items) < self.capacity:
            self.items.append(item)
            self.save_inventory()  # Save after modifying inventory
            return True
        return False

    def remove_item(self, name, quantity=1):
        for item in self.items[:]:  # Avoid mutation during iteration
            if item.name == name:
                if item.quantity > quantity:
                    item.quantity -= quantity
                    self.save_inventory()  # Save after modifying inventory
                elif not item.is_key_item:
                    self.items.remove(item)
                    self.save_inventory()  # Save after modifying inventory
                return True
        return False

    def has_item(self, name):
        return any(item.name == name for item in self.items)

    def get_spacecraft_parts_count(self):
        return sum(item.quantity for item in self.items if item.is_key_item)

    def toggle_visibility(self):
        self.visible = not self.visible

    def navigate(self, direction):
        if direction == "up" and self.selected_index > 0:
            self.selected_index -= 1
        elif direction == "down" and self.selected_index < len(self.items) - 1:
            self.selected_index += 1

    def can_launch_spacecraft(self):
        return self.get_spacecraft_parts_count() >= 4

    def launch_spacecraft(self):
        return self.can_launch_spacecraft()

    def save_inventory(self):
        """Save inventory items to a file"""
        try:
            # Create a serializable representation of inventory items
            serialized_items = []
            for item in self.items:
                item_data = {
                    'name': item.name,
                    'quantity': item.quantity,
                    'is_key_item': item.is_key_item,
                    'description': item.description
                }
                serialized_items.append(item_data)

            # Save to file
            with open(self.save_path, 'wb') as f:
                pickle.dump(serialized_items, f)
            print(f"✅ Inventory saved to {self.save_path}")
            return True
        except Exception as e:
            print(f"❌ Error saving inventory: {e}")
            return False

    def load_inventory(self):
        """Load inventory items from a file"""
        if not os.path.exists(self.save_path):
            print(f"ℹ️ No saved inventory found at {self.save_path}")
            return False

        try:
            with open(self.save_path, 'rb') as f:
                serialized_items = pickle.load(f)

            # Clear current inventory
            self.items = []

            # Recreate items from saved data
            for item_data in serialized_items:
                # Create a fallback image for the item
                image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", "item_fallback.png")
                item = InventoryItem(
                    item_data['name'],
                    image_path,
                    item_data['description'],
                    item_data['is_key_item']
                )
                item.quantity = item_data['quantity']
                self.items.append(item)

            print(f"✅ Loaded {len(self.items)} items from saved inventory")
            return True
        except Exception as e:
            print(f"❌ Error loading inventory: {e}")
            return False

    def render(self, screen, x=900, y=50, width=350, height=600):
        if not self.visible:
            return

        # Background and border
        pygame.draw.rect(screen, (30, 30, 40), (x, y, width, height), border_radius=10)
        pygame.draw.rect(screen, (70, 70, 90), (x, y, width, height), 2, border_radius=10)

        # Inventory title
        title = self.font.render("INVENTORY", True, (255, 215, 0))
        screen.blit(title, (x + (width - title.get_width()) // 2, y + 10))

        # Scroll and list management
        item_y = y + 50
        max_items_visible = 8
        total_items = len(self.items)
        start_index = max(0, min(self.selected_index - max_items_visible // 2, total_items - max_items_visible))

        for i, item in enumerate(self.items[start_index:start_index + max_items_visible]):
            idx = start_index + i
            is_selected = idx == self.selected_index

            # Background for selected item
            row_color = (50, 50, 60, 150) if is_selected else (40, 40, 50, 150)
            row_rect = Rect(x + 10, item_y, width - 20, 50)
            pygame.draw.rect(screen, row_color, row_rect, border_radius=5)

            # Item image
            img_rect = item.image.get_rect(center=(x + 30, item_y + 25))
            screen.blit(item.image, img_rect)

            # Item name and quantity
            color = (200, 200, 255) if is_selected else (255, 255, 255)
            name_text = self.font.render(f"{item.name} x{item.quantity}", True, color)
            screen.blit(name_text, (x + 60, item_y + 10))

            # Description
            desc_text = self.desc_font.render(item.description, True, (200, 200, 200))
            screen.blit(desc_text, (x + 60, item_y + 30))

            item_y += 55

        # Scroll indicators
        if total_items > max_items_visible:
            if start_index > 0:
                up_arrow = self.font.render("↑", True, (255, 255, 255))
                screen.blit(up_arrow, (x + width - 30, y + 30))
            if start_index + max_items_visible < total_items:
                down_arrow = self.font.render("↓", True, (255, 255, 255))
                screen.blit(down_arrow, (x + width - 30, y + height - 30))

        # Key items info
        parts_count = self.get_spacecraft_parts_count()
        parts_text = self.font.render(f"Spacecraft Parts: {parts_count}/4", True, (0, 255, 255))
        screen.blit(parts_text, (x + 10, y + height - 30))

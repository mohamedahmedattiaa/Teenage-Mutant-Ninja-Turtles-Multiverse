import pygame

class Spritesheet:
    def __init__(self, surface):
        try:
            self.sheet = surface
        except Exception as e:
            print(f"Error initializing spritesheet: {e}")
            self.sheet = pygame.Surface((100, 100), pygame.SRCALPHA)
            self.sheet.fill((255, 0, 255, 128))

    def get_image(self, frame, width, height, scale):
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        image.blit(self.sheet, (0, 0), (frame * width, 0, width, height))
        image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        return image   ##
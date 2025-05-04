# spritesheet.py
import pygame
#a
class Spritesheet:
    def __init__(self, image):
        self.sheet = image

    def get_image(self, frame, width, height, scale, colorkey):
        image = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
        image.blit(self.sheet, (0, 0), (frame * width, 0, width, height))

        if scale != 1:
            image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))

        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)

        return image

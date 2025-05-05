import pygame

class Spritesheet():
    def __init__(self, image):
        if isinstance(image, str):
            self.sheet = pygame.image.load(image).convert_alpha()
        else:
            self.sheet = image

    def get_image(self, frame, width, height, scale, color=None):
        # Create surface with per-pixel alpha
        image = pygame.Surface((width, height), pygame.SRCALPHA).convert_alpha()
        image.blit(self.sheet, (0, 0), ((frame * width), 0, width, height))
        image = pygame.transform.scale(image, (width * scale, height * scale))

        # Only apply color key if explicitly provided
        if color is not None:
            image.set_colorkey(color)

        return image

import pygame


class Spritesheet:
    def __init__(self, image):
        self.sheet = image

    def get_image(self, frame, width, height, scale, color):

        image = pygame.Surface((width, height), pygame.SRCALPHA)

        # Extract the frame from the spritesheet
        image.blit(self.sheet, (0, 0), ((frame * width), 0, width, height))

        # Scale the image
        image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))

        # Handle transparency
        if color:
            # For RGB color keys
            if len(color) == 3:
                # Make sure we're working with a surface that supports per-pixel alpha
                image = image.convert_alpha()
                pixel_array = pygame.PixelArray(image)
                pixel_array.replace(color, (0, 0, 0, 0))
                del pixel_array  # Release the pixel array
            # For RGBA specification
            elif len(color) == 4:
                image = image.convert_alpha()

        return image
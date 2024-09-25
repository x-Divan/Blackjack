# utils.py

import pygame

def scale_image(image, target_width, target_height):
    # Scale images once during loading for better performance
    image_width, image_height = image.get_size()
    scale_factor = min(target_width / image_width, target_height / image_height)
    new_width = int(image_width * scale_factor)
    new_height = int(image_height * scale_factor)
    return pygame.transform.scale(image, (new_width, new_height))

import pygame
import os
from .constants import suits, values
import sys

pygame.init()

card_images = {}
background_image = None

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_card_images():
    global background_image
    
    # Load the card back and background image
    card_images['red_back'] = pygame.image.load(resource_path('Images/red_back.png'))
    background_image = pygame.image.load(resource_path('Images/table.jpg'))

    # Load all card images based on suits and values
    for suit in suits:
        for value in values:
            image_filename = f'{value}_of_{suit}.png'
            card_images[f'{value}_of_{suit}'] = pygame.image.load(resource_path(f'Images/{image_filename}'))

# Call the function to load the images
load_card_images()

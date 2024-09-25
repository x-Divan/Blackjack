import pygame
from .assets import card_images
from .utils import scale_image

class Card:
    def __init__(self, value, suit, card_size):
        self.value = value
        self.suit = suit
        self.face_up = True
        self.base_image = card_images[f'{value}_of_{suit}']
        self.image = scale_image(self.base_image, *card_size)

    def get_value(self):
        if self.value in ['jack', 'queen', 'king']:
            return 10
        elif self.value == 'ace':
            return 11
        else:
            return int(self.value)

    def draw_card(self, screen, position, card_size):
        # Draw the card on the screen at the given position
        if self.face_up:
            screen.blit(self.image, position)
        else:
            back_image = scale_image(card_images['red_back'], *card_size)
            screen.blit(back_image, position)

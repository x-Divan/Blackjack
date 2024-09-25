import pygame
import os
from blackjack.game import Game
from blackjack.constants import SCREEN_WIDTH, SCREEN_HEIGHT
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def main():
    pygame.init()

    # Set the window icon
    icon_path = resource_path(os.path.join('Images', 'logo.png'))  # Modified here
    icon = pygame.image.load(icon_path)
    pygame.display.set_icon(icon)

    # Window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Blackjack")

    # Create and run the game
    game = Game(screen)
    game.run()

if __name__ == "__main__":
    main()

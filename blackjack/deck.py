import random
from .constants import suits, values
from .card import Card

class Deck:
    def __init__(self, card_size):
        # Create a full deck of cards
        self.cards = [Card(value, suit, card_size) for suit in suits for value in values]
        random.shuffle(self.cards)
    
    def deal_card(self):
        return self.cards.pop()
    
    def __iter__(self):
        return iter(self.cards)

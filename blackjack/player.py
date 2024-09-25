# player.py

from typing import List
from .card import Card

class Player:
    def __init__(self, name, starting_balance):
        self.name = name
        self.hand: List[Card] = []
        self.balance = starting_balance
        self.bet = 0  # The current bet placed by the player
    
    def add_cash(self, cash):
        self.balance += cash
    
    def remove_cash(self, cash):
        self.balance -= cash  # Subtract cash from balance
    
    def place_bet(self, amount):
        if amount <= self.balance:
            self.bet = amount
            self.remove_cash(amount)
            return True
        else:
            return False  # Not enough balance to place the bet
    
    def add_card(self, card):
        self.hand.append(card)
    
    def reset_hand(self):
        self.hand = []
        self.bet = 0  # Reset bet when the hand is reset
    
    def get_total(self):
        total = 0
        ace_count = 0
        for card in self.hand:
            card_value = card.get_value()
            total += card_value
            if card.value == 'ace':
                ace_count += 1
        # Adjust for aces if total is over 21
        while total > 21 and ace_count > 0:
            total -= 10  # Change an Ace from 11 to 1
            ace_count -= 1
        return total

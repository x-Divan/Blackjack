# game.py

import pygame
from .constants import *
from .utils import scale_image
from .deck import Deck
from .player import Player
from .slider import Slider
from .assets import card_images, background_image
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Determine if we are running as a frozen executable
if getattr(sys, 'frozen', False):
    # Running in a PyInstaller bundle
    base_path = sys._MEIPASS
else:
    # Running in a normal Python environment
    base_path = os.path.dirname(__file__)

# Load the game window icon using the relative path
icon_path = resource_path(os.path.join('Images', 'logo.png'))
icon = pygame.image.load(icon_path)

# Set the icon for the game window
pygame.display.set_icon(icon)

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.game_state = "BETTING"
        self.round_count = 0

        # Screen properties
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = screen.get_size()

        # Calculate initial CARD_SIZE
        self.CARD_SIZE = (int(self.SCREEN_WIDTH * CARD_WIDTH_RATIO), int(self.SCREEN_HEIGHT * CARD_HEIGHT_RATIO))

        # Font
        self.font_size = int(self.SCREEN_HEIGHT * 0.035 * 0.9)  # Reduced by 10%
        self.mono_font = pygame.font.SysFont('Consolas', self.font_size)  # Using 'Consolas' as monospaced font

        # Initialize deck and players
        self.deck = Deck(self.CARD_SIZE)
        self.player = Player("Player", starting_balance)
        self.dealer = Player("Dealer", starting_balance)

        # Initialize flags
        self.player_busted = False
        self.dealer_busted = False
        self.outcome_processed = False

        # Betting variables
        self.bet_amount = 0

        # Initialize buttons
        self.hit_button_rect, self.stand_button_rect = self.create_buttons()

        # Initialize slider
        self.bet_slider = self.create_slider()

        # Scale the back card image for the deck representation
        self.back_card_image = scale_image(card_images['red_back'], *self.CARD_SIZE)

        # Calculate deck position
        self.deck_x = self.SCREEN_WIDTH - self.CARD_SIZE[0] - int(self.SCREEN_WIDTH * 0.1)  # Adjusted to 10% from the right edge
        self.deck_y = (self.SCREEN_HEIGHT - self.CARD_SIZE[1]) // 2  # Centered vertically
        self.deck_position = (self.deck_x, self.deck_y)

        # Scale background image
        self.background_image = pygame.transform.scale(background_image, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

    def create_buttons(self):
        button_width = int(self.SCREEN_WIDTH * BUTTON_WIDTH_RATIO)
        button_height = int(self.SCREEN_HEIGHT * BUTTON_HEIGHT_RATIO)
        button_x = int(self.SCREEN_WIDTH * BUTTON_X_RATIO)
        button_y_start = int(self.SCREEN_HEIGHT * BUTTON_Y_START_RATIO)
        button_y_spacing = int(self.SCREEN_HEIGHT * BUTTON_Y_SPACING_RATIO)

        # Hit button
        hit_button_rect = pygame.Rect(
            button_x,
            button_y_start,
            button_width,
            button_height
        )

        # Stand button
        stand_button_rect = pygame.Rect(
            button_x,
            button_y_start + button_height + button_y_spacing,
            button_width,
            button_height
        )

        return hit_button_rect, stand_button_rect

    def create_slider(self):
        slider_width = int(self.SCREEN_WIDTH * 0.2)  # Adjusted width
        slider_height = 20
        slider_x = (self.SCREEN_WIDTH - slider_width) // 2
        slider_y = int(self.SCREEN_HEIGHT * 0.6)  # Adjusted position

        # Initialize the slider
        bet_slider = Slider(slider_x, slider_y, slider_width, slider_height, min_val=100, max_val=self.player.balance, initial_val=100)
        return bet_slider

    def get_card_position(self, player_type, card_index, total_cards):
        overlap_ratio = 0.2  # 20% overlap
        overlap_amount = self.CARD_SIZE[0] * overlap_ratio
        total_width = self.CARD_SIZE[0] + (total_cards - 1) * (self.CARD_SIZE[0] - overlap_amount)

        # Dynamic offsets based on screen size
        horizontal_offset_ratio = 0.05
        vertical_offset_ratio = 0.05
        horizontal_offset = self.SCREEN_WIDTH * horizontal_offset_ratio
        vertical_offset = self.SCREEN_HEIGHT * vertical_offset_ratio

        if player_type == 'player':
            start_x = (self.SCREEN_WIDTH - total_width) // 2 - horizontal_offset
            y = self.SCREEN_HEIGHT - self.CARD_SIZE[1] - (vertical_offset * 2)
        elif player_type == 'dealer':
            start_x = (self.SCREEN_WIDTH - total_width) // 2 + horizontal_offset
            y = vertical_offset
        else:
            raise ValueError("player_type must be 'player' or 'dealer'")

        x = start_x + card_index * (self.CARD_SIZE[0] - overlap_amount)
        return (x, y)

    def handle_events(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.VIDEORESIZE:
            self.handle_resize(event.size)
        elif self.game_state == "BETTING":
            # Handle slider events (mouse dragging)
            self.bet_slider.handle_event(event)

            # Handle keyboard inputs for adjusting slider value
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.bet_slider.update_with_arrows(pygame.K_LEFT)  # Move slider left
                elif event.key == pygame.K_RIGHT:
                    self.bet_slider.update_with_arrows(pygame.K_RIGHT)  # Move slider right
                elif event.key == pygame.K_RETURN:
                    # Confirm the bet when Enter is pressed
                    self.bet_amount = int(self.bet_slider.value)
                    if self.bet_amount >= 1 and self.bet_amount <= self.player.balance:
                        self.player.place_bet(self.bet_amount)
                        self.game_state = "DEALING"
        elif self.game_state == "GAME_OVER":
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Reset the game
                self.reset_game()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:  # Add the R key to restart after a game is over
                self.reset_game()

        elif self.game_state == "GAME_ENDED":
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.running = False  # Exit the game
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Restart the game if "R" is pressed
                    self.reset_game()
                    self.player.balance = 10000  # Reset the balance
                    self.bet_slider.max_val = self.player.balance  # Update the slider's max value
                    self.bet_slider.value = 100  # Reset the bet value to 100
                    self.bet_slider.update_handle_position()  # Update the slider handle position
                    self.game_state = "BETTING"  # Reset to betting state
        elif self.game_state == "PLAYER_TURN":
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos  # Get the mouse position
                if self.hit_button_rect.collidepoint(mouse_pos):
                    # Player chooses to "Hit"
                    self.player.add_card(self.deck.deal_card())
                    if self.player.get_total() > 21:
                        self.player_busted = True
                        self.game_state = "GAME_OVER"
                        self.outcome_processed = False
                elif self.stand_button_rect.collidepoint(mouse_pos):
                    # Player chooses to "Stand"
                    self.game_state = "DEALER_TURN"

        elif event.type == DEALER_HIT_EVENT and self.game_state == "DEALER_HITTING":
            if self.dealer.get_total() < 17:
                self.dealer.add_card(self.deck.deal_card())
            else:
                pygame.time.set_timer(DEALER_HIT_EVENT, 0)  # Stop the timer
                if self.dealer.get_total() > 21:
                    self.dealer_busted = True
                self.game_state = "GAME_OVER"
                self.outcome_processed = False

    def handle_resize(self, size):
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = size
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.RESIZABLE)
        # Recalculate CARD_SIZE
        self.CARD_SIZE = (int(self.SCREEN_WIDTH * CARD_WIDTH_RATIO), int(self.SCREEN_HEIGHT * CARD_HEIGHT_RATIO))
        # Rescale images
        self.background_image = pygame.transform.scale(background_image, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        for card in self.deck.cards + self.player.hand + self.dealer.hand:
            card.image = scale_image(card.base_image, *self.CARD_SIZE)
        # Recalculate buttons and fonts
        self.hit_button_rect, self.stand_button_rect = self.create_buttons()
        self.font_size = int(self.SCREEN_HEIGHT * 0.035 * 0.9)  # Reduced by 10%
        self.mono_font = pygame.font.SysFont('Consolas', self.font_size)
        # Recalculate slider dimensions
        self.bet_slider = self.create_slider()
        # Recalculate deck position
        self.deck_x = self.SCREEN_WIDTH - self.CARD_SIZE[0] - int(self.SCREEN_WIDTH * 0.1)  # Adjusted to 10% from the right edge
        self.deck_y = (self.SCREEN_HEIGHT - self.CARD_SIZE[1]) // 2  # Centered vertically
        self.deck_position = (self.deck_x, self.deck_y)
        # Rescale the back card image
        self.back_card_image = scale_image(card_images['red_back'], *self.CARD_SIZE)

    def reset_game(self):
        self.player.reset_hand()
        self.dealer.reset_hand()

        # Increment round count
        self.round_count += 1

        # Check if the deck is low on cards or if 5 rounds have passed
        if len(self.deck.cards) < 15 or self.round_count >= 10:  # Reshuffle if deck is low or 10 rounds passed
            self.deck = Deck(self.CARD_SIZE)  # Reshuffle the deck
            self.round_count = 0  # Reset the round counter

            # Optionally trigger a visual shuffle message (if you want to show the shuffle happened)
            self.shuffle_happened = True
            self.shuffle_display_time = pygame.time.get_ticks()

        self.player_busted = False
        self.dealer_busted = False
        self.bet_amount = 0
        self.outcome_processed = False

        # Update slider max value to current balance
        self.bet_slider.max_val = self.player.balance
        self.bet_slider.value = min(self.bet_slider.value, self.player.balance)
        
        # Update the slider's handle position to reflect the new value
        self.bet_slider.update_handle_position()

        if self.player.balance < 1:
            self.game_state = "GAME_ENDED"
        else:
            self.game_state = "BETTING"

    def game_logic(self):
        if self.game_state == "DEALING":
            # Deal initial cards
            self.player.add_card(self.deck.deal_card())
            self.player.add_card(self.deck.deal_card())
            self.dealer.add_card(self.deck.deal_card())
            self.dealer.add_card(self.deck.deal_card())
            self.dealer.hand[1].face_up = False  # Hide one of dealer's cards
            self.game_state = "PLAYER_TURN"
            self.outcome_processed = False  # Reset the flag when dealing new cards

        elif self.game_state == "DEALER_TURN":
            # Reveal dealer's hidden card
            self.dealer.hand[1].face_up = True
            # Start dealer hitting process
            pygame.time.set_timer(DEALER_HIT_EVENT, 1000)  # 1000 milliseconds between hits
            self.game_state = "DEALER_HITTING"

    def draw(self):
        self.screen.blit(self.background_image, (0, 0))
        # Draw game elements based on the game state
        if self.game_state != "BETTING":
            self.draw_hands()
            self.draw_deck()
        if self.game_state == "PLAYER_TURN":
            self.draw_buttons()
            self.draw_balance_and_bet()
        elif self.game_state == "BETTING":
            self.draw_betting()
        elif self.game_state == "GAME_OVER":
            self.process_outcome()
            self.draw_game_over()
        elif self.game_state == "GAME_ENDED":
            self.draw_game_ended()

        pygame.display.flip()  # Update the display

    def draw_hands(self):
        # Draw dealer's hand
        total_dealer_cards = len(self.dealer.hand)
        if total_dealer_cards > 0:  # Ensure dealer has cards
            for index, card in enumerate(self.dealer.hand):
                position = self.get_card_position('dealer', index, total_dealer_cards)
                card.draw_card(self.screen, position, self.CARD_SIZE)
            # After drawing the dealer's cards, get the last card's position
            dealer_card_y = position[1]

            # Display dealer's hand total if dealer's cards are all face up
            if all(card.face_up for card in self.dealer.hand):
                dealer_total = self.dealer.get_total()
                dealer_total_text = self.mono_font.render(f"Dealer's Total: {dealer_total}", True, WHITE)
                dealer_total_y = dealer_card_y + self.CARD_SIZE[1] + self.font_size * 0.5  # Adjust as needed for padding
                dealer_total_rect = dealer_total_text.get_rect(center=(self.SCREEN_WIDTH // 2, dealer_total_y))
                self.screen.blit(dealer_total_text, dealer_total_rect)

        # Draw player's hand
        total_player_cards = len(self.player.hand)
        if total_player_cards > 0:  # Ensure player has cards
            for index, card in enumerate(self.player.hand):
                position = self.get_card_position('player', index, total_player_cards)
                card.draw_card(self.screen, position, self.CARD_SIZE)
            # After drawing the player's cards, get the last card's position
            player_card_y = position[1]
            
            # Display player's hand total above the player's hand
            player_total = self.player.get_total()
            total_text = self.mono_font.render(f'Your Total: {player_total}', True, WHITE)
            total_y = player_card_y - self.font_size * 0.5  # Move it closer to the hand
            total_rect = total_text.get_rect(center=(self.SCREEN_WIDTH // 2, total_y))
            self.screen.blit(total_text, total_rect)

            # Adjust the text to be closer to the player's hand
            total_y = player_card_y - self.font_size * 0.5  # Move it closer to the hand
            total_rect = total_text.get_rect(center=(self.SCREEN_WIDTH // 2, total_y))
            self.screen.blit(total_text, total_rect)

    def draw_deck(self):
        # Draw the deck on the right side with overlapping back cards
        deck_card_count = 11
        vertical_offset_ratio = 0.05
        vertical_offset = self.SCREEN_HEIGHT * vertical_offset_ratio

        for i in range(deck_card_count):
            offset = i * int(self.CARD_SIZE[0] * -0.01)  # 5% of card width
            deck_card_position = (self.deck_x - offset, vertical_offset + (offset//2))
            self.screen.blit(self.back_card_image, deck_card_position)

    def draw_buttons(self):
        # Draw the buttons
        pygame.draw.rect(self.screen, WHITE, self.hit_button_rect)
        pygame.draw.rect(self.screen, WHITE, self.stand_button_rect)

        # Render the text
        hit_text = self.mono_font.render('Hit', True, BLACK)
        stand_text = self.mono_font.render('Stand', True, BLACK)

        # Center the text on the buttons
        hit_text_rect = hit_text.get_rect(center=self.hit_button_rect.center)
        stand_text_rect = stand_text.get_rect(center=self.stand_button_rect.center)

        # Blit the text onto the buttons
        self.screen.blit(hit_text, hit_text_rect)
        self.screen.blit(stand_text, stand_text_rect)

    def draw_balance_and_bet(self):
        # Display current balance and bet amount
        balance_text = self.mono_font.render(f'Cash Money: ${self.player.balance}', True, WHITE)
        balance_rect = balance_text.get_rect(topleft=(10, 10))
        self.screen.blit(balance_text, balance_rect)

        bet_text = self.mono_font.render(f'Current Bet: ${self.player.bet}', True, WHITE)
        bet_rect = bet_text.get_rect(topleft=(10, 10 + self.font_size + 5))
        self.screen.blit(bet_text, bet_rect)

    def draw_betting(self):
        # Draw slider
        self.bet_slider.draw(self.screen)

        slider_y = self.bet_slider.rect.y

        # Display current bet value
        bet_value_text = self.mono_font.render(f'Bet Amount: ${int(self.bet_slider.value)}', True, WHITE)
        bet_value_rect = bet_value_text.get_rect(center=(self.SCREEN_WIDTH // 2, slider_y - 30))
        self.screen.blit(bet_value_text, bet_value_rect)

        # Display prompt
        prompt_text = self.mono_font.render('Adjust your bet and press Enter', True, WHITE)
        prompt_rect = prompt_text.get_rect(center=(self.SCREEN_WIDTH // 2, slider_y - 60))
        self.screen.blit(prompt_text, prompt_rect)

        # Display current balance
        balance_text = self.mono_font.render(f'Cash Money: ${self.player.balance}', True, WHITE)
        balance_rect = balance_text.get_rect(center=(self.SCREEN_WIDTH // 2, slider_y + 50))
        self.screen.blit(balance_text, balance_rect)

    def process_outcome(self):
        if not self.outcome_processed:
            # Determine the outcome
            if self.player_busted:
                self.outcome = "Bust! You lose."
                # Player already lost the bet amount when placing the bet
            elif self.dealer_busted:
                self.outcome = "Dealer busts! You win!"
                self.player.add_cash(self.player.bet * 2)  # Win amount equal to the bet
            else:
                player_total = self.player.get_total()
                dealer_total = self.dealer.get_total()

                if player_total > dealer_total:
                    self.outcome = "You win!"
                    self.player.add_cash(self.player.bet * 2)  # Win amount equal to the bet
                elif player_total == dealer_total:
                    self.outcome = "Push! It's a tie."
                    self.player.add_cash(self.player.bet)  # Return the bet amount
                else:
                    self.outcome = "You lose."
                    # Player already lost the bet amount when placing the bet

            self.outcome_processed = True  # Set the flag to prevent re-processing

    def draw_game_over(self):
        # Centered positions
        center_x = self.SCREEN_WIDTH // 2
        balance_y = self.SCREEN_HEIGHT // 2

        # Display balance at the vertical center
        balance_text = self.mono_font.render(f'Cash Money: ${self.player.balance}', True, WHITE)
        balance_rect = balance_text.get_rect(center=(center_x, balance_y))
        self.screen.blit(balance_text, balance_rect)

        # Display outcome above the balance
        outcome_text = self.mono_font.render(self.outcome, True, WHITE)
        outcome_y = balance_y - self.font_size * 1.5  # Adjust spacing as needed
        outcome_rect = outcome_text.get_rect(center=(center_x, outcome_y))
        self.screen.blit(outcome_text, outcome_rect)

        # Display "Click anywhere to play again." below the balance
        if self.player.balance == 0:
            play_again_text = self.mono_font.render("Click to continue", True, WHITE)
        else:
            play_again_text = self.mono_font.render('Click anywhere to play again.', True, WHITE)
        play_again_y = balance_y + self.font_size * 1.5  # Adjust spacing as needed
        play_again_rect = play_again_text.get_rect(center=(center_x, play_again_y))
        self.screen.blit(play_again_text, play_again_rect)

    def draw_game_ended(self):
        # Clear the screen and display the background
        self.screen.blit(self.background_image, (0, 0))

        # Centered positions for displaying text
        center_x = self.SCREEN_WIDTH // 2
        center_y = self.SCREEN_HEIGHT // 2

        # Display game over message
        game_over_text = self.mono_font.render("Game Over!", True, WHITE)
        game_over_rect = game_over_text.get_rect(center=(center_x, center_y - self.font_size * 2))
        self.screen.blit(game_over_text, game_over_rect)

        # Display message that the player is out of cash
        out_of_cash_text = self.mono_font.render("You have run out of cash money.", True, WHITE)
        out_of_cash_rect = out_of_cash_text.get_rect(center=(center_x, center_y))
        self.screen.blit(out_of_cash_text, out_of_cash_rect)

        # Display message prompting the player to exit or restart
        exit_text = self.mono_font.render("Press 'R' to restart or click to exit.", True, WHITE)
        exit_rect = exit_text.get_rect(center=(center_x, center_y + self.font_size * 2))
        self.screen.blit(exit_text, exit_rect)

        pygame.display.flip()  # Update the display

    def run(self):
        while self.running:
            for event in pygame.event.get():
                self.handle_events(event)

            # Game logic outside event loop
            self.game_logic()

            # Draw everything
            self.draw()

        pygame.quit()

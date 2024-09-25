import pygame

class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, increment=500):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.increment = increment
        self.handle_width = height * 0.8  # Oval handle width (narrower than slider height)
        self.handle_height = height * 1.5  # Oval handle height (taller than slider height)
        self.handle_x = x + (width) * ((initial_val - min_val) / (max_val - min_val))
        self.dragging = False

    def update_handle_position(self):
        if self.max_val != self.min_val:
            ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
            self.handle_x = self.rect.x + int(ratio * self.rect.width)
        else:
            # Set the handle to the start or end of the slider as a default
            self.handle_x = self.rect.x  # Move to the start if there's no valid range



    def draw(self, surface):
        # Draw the slider track (a filled rectangle with rounded edges for a cleaner look)
        pygame.draw.rect(surface, (180, 180, 180), self.rect, border_radius=self.rect.height // 2)

        # Draw the vertically oval handle (narrower and taller than the slider)
        handle_rect = pygame.Rect(
            int(self.handle_x - self.handle_width / 2),  # Center the handle horizontally on the slider
            self.rect.y + (self.rect.height - self.handle_height) // 2,  # Center vertically
            self.handle_width,
            self.handle_height
        )
        pygame.draw.ellipse(surface, (50, 50, 50), handle_rect)  # Oval handle

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if the click is inside the handle (which is now a vertical oval)
            handle_rect = pygame.Rect(
                int(self.handle_x - self.handle_width / 2),
                self.rect.y + (self.rect.height - self.handle_height) // 2,
                self.handle_width,
                self.handle_height
            )
            if handle_rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                new_x = min(max(event.pos[0], self.rect.x), self.rect.x + self.rect.width)
                self.handle_x = new_x
                ratio = (self.handle_x - self.rect.x) / self.rect.width
                self.value = self.min_val + ratio * (self.max_val - self.min_val)
                self.value = round(self.value / self.increment) * self.increment
                self.value = max(self.min_val, min(self.value, self.max_val))

    def update_with_arrows(self, direction):
        if direction == pygame.K_LEFT:
            self.value = max(self.min_val, self.value - self.increment)
        elif direction == pygame.K_RIGHT:
            self.value = min(self.max_val, self.value + self.increment)

        # Recalculate the handle position based on the updated value
        self.update_handle_position()


import pygame
from constants import BLUE, LIGHT_GRAY, WHITE, BLACK, YELLOW, GRAY, GREEN, RED, NEON_MAGENTA, ELECTRIC_PURPLE

class Button:
    def __init__(self, x: float, y: float, width: float, height: float, text: str, 
                 color: tuple = BLUE, hover_color: tuple = (70, 170, 240), hover_effect: bool = True):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.hover_effect = hover_effect
        self.is_hovered = False
        self.scale = 1.0
        self.target_scale = 1.0
    
    def update(self, mouse_pos: tuple):
        was_hovered = self.is_hovered
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        # Smooth scale animation
        if self.hover_effect:
            self.target_scale = 1.05 if self.is_hovered else 1.0
        else:
            self.target_scale = 1.0
        self.scale += (self.target_scale - self.scale) * 0.3
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font):
        # Calculate scaled rect
        scaled_width = int(self.rect.width * self.scale)
        scaled_height = int(self.rect.height * self.scale)
        scaled_x = self.rect.centerx - scaled_width // 2
        scaled_y = self.rect.centery - scaled_height // 2
        scaled_rect = pygame.Rect(scaled_x, scaled_y, scaled_width, scaled_height)
        
        # Draw shadow
        shadow_offset = 4
        shadow_rect = scaled_rect.copy()
        shadow_rect.x += shadow_offset
        shadow_rect.y += shadow_offset
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 80), shadow_surface.get_rect(), border_radius=10)
        screen.blit(shadow_surface, shadow_rect)
        
        # Draw button background (solid color without neon gradient)
        pygame.draw.rect(screen, self.color, scaled_rect, border_radius=10)

        
        # Border
        border_color = WHITE if (self.is_hovered and self.hover_effect) else LIGHT_GRAY
        pygame.draw.rect(screen, border_color, scaled_rect, 3, border_radius=10)
        
        # Text with shadow
        text_surface = font.render(self.text, True, BLACK)
        text_shadow = font.render(self.text, True, (0, 0, 0, 100))
        text_rect = text_surface.get_rect(center=scaled_rect.center)
        shadow_rect = text_rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        screen.blit(text_shadow, shadow_rect)
        screen.blit(text_surface, text_rect)
        
        # Final text in white
        text_surface = font.render(self.text, True, WHITE)
        screen.blit(text_surface, text_rect)
    
    def is_clicked(self, mouse_pos: tuple) -> bool:
        return self.is_hovered

class Slider:
    def __init__(self, x: float, y: float, width: float, min_val: float, max_val: float, 
                 initial_val: float, label: str, step: float = 1):
        self.x = x
        self.y = y
        self.width = width
        self.height = 20
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        self.step = step
        self.dragging = False
        
        self.track_rect = pygame.Rect(x, y, width, self.height)
        self.handle_radius = 12
        self.update_handle_position()
    
    def update_handle_position(self):
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        self.handle_x = self.x + ratio * self.width
    
    def update(self, mouse_pos: tuple, mouse_pressed: bool):
        handle_rect = pygame.Rect(self.handle_x - self.handle_radius, 
                                  self.y + self.height // 2 - self.handle_radius,
                                  self.handle_radius * 2, self.handle_radius * 2)
        
        if mouse_pressed:
            if handle_rect.collidepoint(mouse_pos) or self.dragging:
                self.dragging = True
                # Update value based on mouse position
                ratio = max(0, min(1, (mouse_pos[0] - self.x) / self.width))
                raw_value = self.min_val + ratio * (self.max_val - self.min_val)
                self.value = round(raw_value / self.step) * self.step
                self.value = max(self.min_val, min(self.max_val, self.value))
                self.update_handle_position()
        else:
            self.dragging = False
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font):
        # Label
        label_surface = font.render(self.label, True, WHITE)
        screen.blit(label_surface, (self.x, self.y - 30))
        
        # Value display
        if self.step >= 1:
            value_text = f"{int(self.value)}"
        else:
            value_text = f"{self.value:.1f}"
        value_surface = font.render(value_text, True, YELLOW)
        screen.blit(value_surface, (self.x + self.width + 15, self.y - 5))
        
        # Track
        pygame.draw.rect(screen, GRAY, self.track_rect, border_radius=10)
        
        # Filled track
        filled_width = (self.value - self.min_val) / (self.max_val - self.min_val) * self.width
        filled_rect = pygame.Rect(self.x, self.y, filled_width, self.height)
        pygame.draw.rect(screen, GREEN, filled_rect, border_radius=10)
        
        # Handle
        handle_color = YELLOW if self.dragging else WHITE
        pygame.draw.circle(screen, handle_color, 
                          (int(self.handle_x), int(self.y + self.height // 2)), 
                          self.handle_radius)
        pygame.draw.circle(screen, BLACK, 
                          (int(self.handle_x), int(self.y + self.height // 2)), 
                          self.handle_radius, 2)

class ToggleButton:
    def __init__(self, x: float, y: float, label: str, initial_state: bool = False):
        self.x = x
        self.y = y
        self.width = 60
        self.height = 30
        self.label = label
        self.state = initial_state
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.is_hovered = False
    
    def update(self, mouse_pos: tuple):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    def toggle(self):
        self.state = not self.state
    
    def is_clicked(self, mouse_pos: tuple) -> bool:
        return self.is_hovered
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font):
        # Label
        label_surface = font.render(self.label, True, WHITE)
        screen.blit(label_surface, (self.x, self.y - 30))
        
        # Toggle background
        bg_color = GREEN if self.state else GRAY
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=15)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=15)
        
        # Toggle circle
        circle_x = self.x + self.width - 15 if self.state else self.x + 15
        pygame.draw.circle(screen, WHITE, (int(circle_x), int(self.y + self.height // 2)), 12)
        
        # State text
        state_text = "ON" if self.state else "OFF"
        state_surface = font.render(state_text, True, YELLOW)
        screen.blit(state_surface, (self.x + self.width + 15, self.y + 3))

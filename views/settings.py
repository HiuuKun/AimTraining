import pygame
from constants import *

class SettingsView:
    def __init__(self, game):
        self.game = game

    def draw(self, screen):
        # Title
        title = self.game.large_font.render("SETTINGS", True, YELLOW)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 60))
        screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.game.tiny_font.render("Customize your game experience", True, LIGHT_GRAY)
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, 100))
        screen.blit(subtitle, subtitle_rect)
        
        # Draw tab buttons with active highlighting
        if self.game.settings_tab == "difficulty":
            # Difficulty tab active - draw with solid color
            diff_rect = pygame.Rect(250, 120, 200, 50)
            pygame.draw.rect(screen, ACCENT_BLUE, diff_rect, border_radius=10)
            pygame.draw.rect(screen, WHITE, diff_rect, 3, border_radius=10)
            diff_text = self.game.medium_font.render("Difficulty", True, WHITE)
            diff_text_rect = diff_text.get_rect(center=diff_rect.center)
            screen.blit(diff_text, diff_text_rect)
            
            # Mouse tab inactive
            self.game.mouse_tab_button.draw(screen, self.game.medium_font)
        else:
            # Difficulty tab inactive
            self.game.difficulty_tab_button.draw(screen, self.game.medium_font)
            
            # Mouse tab active - draw with solid color
            mouse_rect = pygame.Rect(470, 120, 200, 50)
            pygame.draw.rect(screen, ACCENT_GREEN, mouse_rect, border_radius=10)
            pygame.draw.rect(screen, WHITE, mouse_rect, 3, border_radius=10)
            mouse_text = self.game.medium_font.render("Mouse", True, WHITE)
            mouse_text_rect = mouse_text.get_rect(center=mouse_rect.center)
            screen.blit(mouse_text, mouse_text_rect)
        
        # Draw content based on active tab
        if self.game.settings_tab == "difficulty":
            self.draw_difficulty_settings(screen)
        else:
            self.draw_mouse_settings(screen)
        
        # Back button (also applies settings)
        self.game.back_button.draw(screen, self.game.small_font)
    
    def draw_difficulty_settings(self, screen):
        """Draw difficulty settings tab content"""
        
        # Difficulty Preset Title
        title = self.game.medium_font.render("Difficulty Preset", True, WHITE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, 220))
        screen.blit(title, title_rect)
        
        # Draw Presets aligned directly in the middle
        self.game.btn_easy.draw(screen, self.game.medium_font)
        self.game.btn_medium.draw(screen, self.game.medium_font)
        self.game.btn_hard.draw(screen, self.game.medium_font)
        
        # Highlight active
        active_btn = None
        if self.game.manager.difficulty == "Easy":
            active_btn = self.game.btn_easy
        elif self.game.manager.difficulty == "Medium":
            active_btn = self.game.btn_medium
        elif self.game.manager.difficulty == "Hard":
            active_btn = self.game.btn_hard
            
        if active_btn:
            pygame.draw.rect(screen, NEON_PURPLE, active_btn.rect, 4, border_radius=min(10, active_btn.rect.height//2))
            
        # Draw other controls horizontally below presets
        pygame.draw.line(screen, DARK_GRAY, (WINDOW_WIDTH//2 - 200, 520), (WINDOW_WIDTH//2 + 200, 520), 2)
        
        # Adjust label positions slightly so they form neat layout below presets
        # Toggle will display with customized spacing below
        self.game.duration_slider.draw(screen, self.game.small_font)
        self.game.difficulty_toggle.draw(screen, self.game.small_font)
    
    def draw_mouse_settings(self, screen):
        """Draw mouse settings tab content"""
        # Draw mouse sliders
        self.game.sensitivity_slider.draw(screen, self.game.small_font)
        self.game.crosshair_size_slider.draw(screen, self.game.small_font)
        
        # Crosshair color selection
        color_label_y = 365  # Moved down to avoid overlap with sliders
        color_label = self.game.small_font.render("Crosshair Color:", True, WHITE)
        screen.blit(color_label, (280, color_label_y))
        
        # Draw color buttons with labels
        for name, button_data in self.game.color_buttons.items():
            rect = button_data["rect"]
            color = button_data["color"]
            
            # Draw color button
            pygame.draw.rect(screen, color, rect, border_radius=8)
            
            # Highlight selected color
            if name == self.game.crosshair_color_name:
                pygame.draw.rect(screen, WHITE, rect, 5, border_radius=8)
                # Draw checkmark
                check_x = rect.centerx
                check_y = rect.centery
                pygame.draw.circle(screen, BLACK, (check_x, check_y), 8)
                pygame.draw.circle(screen, WHITE, (check_x, check_y), 6)
            else:
                pygame.draw.rect(screen, GRAY, rect, 2, border_radius=8)
            
            # Color name label below button
            label = self.game.tiny_font.render(name[:3], True, LIGHT_GRAY)
            label_rect = label.get_rect(centerx=rect.centerx, top=rect.bottom + 3)
            screen.blit(label, label_rect)
        
        # Crosshair type selection
        type_label_y = 550  # Adjusted to be above type buttons
        type_label = self.game.small_font.render("Crosshair Type:", True, WHITE)
        screen.blit(type_label, (280, type_label_y))
        
        # Draw type buttons
        for ctype, button_data in self.game.type_buttons.items():
            rect = button_data["rect"]
            
            # Button color based on selection
            if ctype == self.game.crosshair_type:
                btn_color = ACCENT_GREEN
                border_color = WHITE
                border_width = 4
            else:
                btn_color = DARK_GRAY
                border_color = GRAY
                border_width = 2
            
            # Draw button
            pygame.draw.rect(screen, btn_color, rect, border_radius=8)
            pygame.draw.rect(screen, border_color, rect, border_width, border_radius=8)
            
            # Draw text
            text = self.game.tiny_font.render(ctype, True, WHITE)
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)
        
        # Crosshair preview panel
        preview_x = 800
        preview_y = 300
        preview_width = 320
        preview_height = 220
        
        preview_panel = pygame.Rect(preview_x, preview_y, preview_width, preview_height)
        pygame.draw.rect(screen, (20, 20, 30), preview_panel, border_radius=10)
        pygame.draw.rect(screen, ACCENT_PURPLE, preview_panel, 2, border_radius=10)
        
        preview_title = self.game.medium_font.render("Preview", True, YELLOW)
        preview_rect = preview_title.get_rect(center=(preview_x + preview_width // 2, preview_y + 30))
        screen.blit(preview_title, preview_rect)
        
        # Preview background with grid
        preview_bg_x = preview_x + 60
        preview_bg_y = preview_y + 70
        preview_bg = pygame.Rect(preview_bg_x, preview_bg_y, 200, 120)
        pygame.draw.rect(screen, DARK_GRAY, preview_bg, border_radius=10)
        
        # Draw grid lines
        for i in range(1, 4):
            x_pos = preview_bg_x + i * 50
            pygame.draw.line(screen, (60, 60, 70), (x_pos, preview_bg_y), (x_pos, preview_bg_y + 120), 1)
        for i in range(1, 3):
            y_pos = preview_bg_y + i * 40
            pygame.draw.line(screen, (60, 60, 70), (preview_bg_x, y_pos), (preview_bg_x + 200, y_pos), 1)
        
        pygame.draw.rect(screen, GRAY, preview_bg, 2, border_radius=10)
        
        # Draw crosshair preview in center
        self.game.draw_crosshair_at(preview_bg_x + 100, preview_bg_y + 60, int(self.game.crosshair_size_slider.value))
        
        # Help panel
        help_x = 780
        help_y = 540
        help_width = 360
        help_height = 150
        
        help_panel = pygame.Rect(help_x, help_y, help_width, help_height)
        pygame.draw.rect(screen, (20, 20, 30), help_panel, border_radius=10)
        pygame.draw.rect(screen, ACCENT_YELLOW, help_panel, 2, border_radius=10)
        
        help_title = self.game.small_font.render("Tips:", True, YELLOW)
        screen.blit(help_title, (help_x + 20, help_y + 15))
        
        help_lines = [
            "• Adjust crosshair for comfort",
            "• Different types suit different",
            "  play styles and preferences",
            "• Preview shows real size",
        ]
        
        y_pos = help_y + 55
        for line in help_lines:
            text = self.game.tiny_font.render(line, True, LIGHT_GRAY)
            screen.blit(text, (help_x + 20, y_pos))
            y_pos += 22

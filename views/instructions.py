import pygame
from constants import *

class InstructionView:
    def __init__(self, game):
        self.game = game

    def draw(self, screen):
        # Title
        title = self.game.large_font.render("INSTRUCTIONS", True, YELLOW)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 80))
        screen.blit(title, title_rect)
        
        # Instructions panel
        panel_rect = pygame.Rect(WINDOW_WIDTH // 2 - 400, 140, 800, 550)
        pygame.draw.rect(screen, (20, 20, 30), panel_rect, border_radius=15)
        pygame.draw.rect(screen, ACCENT_BLUE, panel_rect, 3, border_radius=15)
        
        instructions = [
            "HOW TO PLAY:",
            "",
            "• Click on targets before they disappear",
            "• Targets shrink and disappear faster over time",
            "• Aim for the center for MAXIMUM points",
            "",
            "CONTROLS:",
            "",
            "• Left Mouse Button - Click targets",
            "• ESC key - Pause / Resume game",
            "",
            "SCORING:",
            "",
            "• Inner Circle (PERFECT!): 150 Base Points",
            "• Middle Circle (GREAT!): 125 Base Points",
            "• Outer Circle (GOOD!): 100 Base Points",
            "• Faster Reaction: Up to +100 Bonus Points",
            "• Miss / Timeout: 0 Points & Accuracy Penalty",
        ]
        
        y_offset = 165
        for line in instructions:
            if line.startswith("•"):
                text = self.game.small_font.render(line, True, WHITE)
            elif line.endswith(":"):
                text = self.game.medium_font.render(line, True, YELLOW)
            else:
                text = self.game.small_font.render(line, True, LIGHT_GRAY)
            
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, y_offset))
            screen.blit(text, text_rect)
            y_offset += 30 if line else 15
        
        # Back button
        self.game.back_button.draw(screen, self.game.small_font)

import os
import pygame
from constants import *
from ui import Button

class ScoreboardView:
    def __init__(self, game):
        self.game = game

    def get_scores(self):
        scores = []
        if os.path.exists("scores.txt"):
            try:
                with open("scores.txt", "r") as f:
                    for line in f:
                        parts = line.strip().split(',')
                        if len(parts) == 4:
                            scores.append({
                                'date': parts[0],
                                'score': int(parts[1]),
                                'accuracy': parts[2],
                                'reaction': parts[3]
                            })
            except Exception:
                pass
        # Sort by score descending
        scores.sort(key=lambda x: x['score'], reverse=True)
        return scores[:10]  # Top 10

    def draw(self, screen):
        # Title
        title = self.game.large_font.render("HIGH SCORES", True, ACCENT_YELLOW)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 80))
        screen.blit(title, title_rect)
        
        # Panel
        panel_rect = pygame.Rect(WINDOW_WIDTH // 2 - 400, 150, 800, 500)
        pygame.draw.rect(screen, (20, 20, 30), panel_rect, border_radius=15)
        pygame.draw.rect(screen, ACCENT_YELLOW, panel_rect, 3, border_radius=15)

        # Headers
        headers = ["Date", "Score", "Accuracy", "Reaction"]
        x_offsets = [WINDOW_WIDTH//2 - 250, WINDOW_WIDTH//2 - 50, WINDOW_WIDTH//2 + 100, WINDOW_WIDTH//2 + 250]
        
        for text, x in zip(headers, x_offsets):
            surf = self.game.medium_font.render(text, True, LIGHT_GRAY)
            rect = surf.get_rect(center=(x, 190))
            screen.blit(surf, rect)

        pygame.draw.line(screen, DARK_GRAY, (WINDOW_WIDTH//2 - 350, 220), (WINDOW_WIDTH//2 + 350, 220), 2)

        # Scores
        scores = self.get_scores()
        y_offset = 250
        for idx, s in enumerate(scores):
            color = WHITE if idx > 2 else [ACCENT_YELLOW, LIGHT_GRAY, ORANGE][idx] # Gold, Silver, Bronze
            
            date_surf = self.game.small_font.render(s['date'], True, color)
            score_surf = self.game.small_font.render(str(s['score']), True, color)
            acc_surf = self.game.small_font.render(f"{s['accuracy']}%", True, color)
            react_surf = self.game.small_font.render(f"{s['reaction']}ms", True, color)

            screen.blit(date_surf, date_surf.get_rect(center=(x_offsets[0], y_offset)))
            screen.blit(score_surf, score_surf.get_rect(center=(x_offsets[1], y_offset)))
            screen.blit(acc_surf, acc_surf.get_rect(center=(x_offsets[2], y_offset)))
            screen.blit(react_surf, react_surf.get_rect(center=(x_offsets[3], y_offset)))

            y_offset += 40

        # Back button
        self.game.back_button.draw(screen, self.game.medium_font)

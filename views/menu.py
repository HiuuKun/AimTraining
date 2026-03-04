import pygame
from constants import *

class MenuView:
    def __init__(self, game):
        self.game = game
    
    def draw_start_screen(self, screen):
        # Animated particles in background
        # Title with glow effect
        title = self.game.title_font.render("AIM TRAINER PRO", True, BLUE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 150))
        
        screen.blit(title, title_rect)
        
        # Subtitle with better styling
        subtitle = self.game.small_font.render("Reflex Training", True, LIGHT_GRAY)
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, 180))
        screen.blit(subtitle, subtitle_rect)
        
        # Buttons
        self.game.start_button.draw(screen, self.game.medium_font)
        self.game.instructions_button.draw(screen, self.game.medium_font)
        self.game.scoreboard_button.draw(screen, self.game.medium_font)
        self.game.settings_button.draw(screen, self.game.medium_font)
        self.game.exit_button.draw(screen, self.game.medium_font)
    
    def draw_results_screen(self, screen):
        # Title
        title = self.game.large_font.render("GAME OVER", True, YELLOW)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 80))
        screen.blit(title, title_rect)
        
        # Stats panel (Left)
        stats_panel = pygame.Rect(100, 150, 450, 500)
        pygame.draw.rect(screen, (20, 20, 30), stats_panel, border_radius=15)
        pygame.draw.rect(screen, YELLOW, stats_panel, 3, border_radius=15)
        
        y_offset = 190
        line_spacing = 60
        center_x = 100 + 450 // 2
        
        # Score
        score_text = self.game.large_font.render(f"Final Score: {self.game.stats.score}", True, GREEN)
        score_rect = score_text.get_rect(center=(center_x, y_offset))
        screen.blit(score_text, score_rect)
        y_offset += line_spacing + 20
        
        # Hits and Misses
        hits_text = self.game.medium_font.render(f"Hits: {self.game.stats.hits}", True, WHITE)
        hits_rect = hits_text.get_rect(center=(center_x, y_offset))
        screen.blit(hits_text, hits_rect)
        y_offset += line_spacing
        
        misses_text = self.game.medium_font.render(f"Misses: {self.game.stats.misses}", True, WHITE)
        misses_rect = misses_text.get_rect(center=(center_x, y_offset))
        screen.blit(misses_text, misses_rect)
        y_offset += line_spacing
        
        # Accuracy
        accuracy = self.game.stats.get_accuracy()
        accuracy_color = GREEN if accuracy >= 80 else YELLOW if accuracy >= 60 else RED
        accuracy_text = self.game.medium_font.render(f"Accuracy: {accuracy:.1f}%", True, accuracy_color)
        accuracy_rect = accuracy_text.get_rect(center=(center_x, y_offset))
        screen.blit(accuracy_text, accuracy_rect)
        y_offset += line_spacing
        
        # Reaction times text
        if self.game.stats.reaction_times:
            avg_rt = self.game.stats.get_avg_reaction_time()
            best_rt = self.game.stats.get_best_reaction_time()
            
            avg_text = self.game.small_font.render(f"Avg: {avg_rt:.0f}ms   Best: {best_rt:.0f}ms", True, WHITE)
            avg_rect = avg_text.get_rect(center=(center_x, y_offset))
            screen.blit(avg_text, avg_rect)
        
        # Graph panel (Right)
        graph_panel = pygame.Rect(600, 150, 500, 500)
        pygame.draw.rect(screen, (20, 20, 30), graph_panel, border_radius=15)
        pygame.draw.rect(screen, BLUE, graph_panel, 3, border_radius=15)
        
        if self.game.stats.reaction_times and len(self.game.stats.reaction_times) > 1:
            self.draw_reaction_graph(screen, graph_panel, self.game.stats.reaction_times)
        else:
            no_data = self.game.medium_font.render("Not enough data for graph", True, LIGHT_GRAY)
            screen.blit(no_data, no_data.get_rect(center=graph_panel.center))
        
        # Buttons
        self.game.restart_button.draw(screen, self.game.medium_font)
        self.game.menu_button.draw(screen, self.game.medium_font)
        
    def draw_reaction_graph(self, screen, rect, times):
        title = self.game.small_font.render("Reaction Time (ms) over Targets", True, YELLOW)
        screen.blit(title, (rect.x + 20, rect.y + 15))
        
        pad_x = 60
        pad_y = 60
        g_width = rect.width - pad_x * 2
        g_height = rect.height - pad_y * 1.5
        g_x = rect.x + pad_x
        g_y = rect.y + 50
        
        # Axes
        pygame.draw.line(screen, WHITE, (g_x, g_y), (g_x, g_y + g_height), 2)
        pygame.draw.line(screen, WHITE, (g_x, g_y + g_height), (g_x + g_width, g_y + g_height), 2)
        
        # Value logic
        y_max = max(times)
        if y_max == 0: y_max = 1000
        # Give some padding at top
        y_max = y_max * 1.1
        
        num_labels = 5
        for i in range(num_labels + 1):
            val = y_max - (y_max / num_labels) * i
            y_pos = g_y + (g_height / num_labels) * i
            
            # Y label
            label = self.game.tiny_font.render(f"{val:.0f}", True, LIGHT_GRAY)
            screen.blit(label, (g_x - 45, y_pos - 10))
            
            # Grid
            if i < num_labels:
                pygame.draw.line(screen, (50, 50, 60), (g_x, y_pos), (g_x + g_width, y_pos), 1)
        
        # Points and lines
        points = []
        x_step = g_width / (len(times) - 1)
        for i, t in enumerate(times):
            px = g_x + i * x_step
            py = g_y + g_height - (t / y_max) * g_height
            points.append((px, py))
            
        pygame.draw.lines(screen, NEON_PURPLE, False, points, 3)
        for p in points:
            pygame.draw.circle(screen, CYAN, (int(p[0]), int(p[1])), 4)

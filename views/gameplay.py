import pygame
import math
from constants import *

class GameplayView:
    def __init__(self, game):
        self.game = game

    def draw(self, screen):
        # Draw HUD
        self.draw_hud(screen)
        
        # Draw target first
        if self.game.current_target:
            # Use pause-adjusted time for accurate TTL display
            current_time = pygame.time.get_ticks()
            if self.game.state == GameState.PAUSED:
                # When paused, use the time when pause started
                current_time = self.game.pause_start_time
            
            remaining_ratio = self.game.current_target.get_remaining_time(current_time) / self.game.current_target.ttl
            
            # Draw target sprites if available, otherwise draw circles
            if self.game.target_sprites:
                # --- SPRITE MODE (With Fancy Masking) ---
                target_diameter = int(self.game.current_target.radius * 2)
                target_size = (target_diameter, target_diameter)

                # 1. Prepare Layers (Scaled to intended relative sizes)
                # User mapped 'inner' -> Circle1 (Big Background) -> Scale to 100%
                # User mapped 'middle' -> Circle2 (Middle) -> Scale to 65%
                # User mapped 'outer' -> Circle3 (Small Dot) -> Scale to 30%
                
                size_big = target_size
                size_mid = (int(target_diameter * 0.65), int(target_diameter * 0.65))
                size_sml = (int(target_diameter * 0.3), int(target_diameter * 0.3))
                
                # Calculate centering offsets
                off_big = (0, 0)
                off_mid = ((target_diameter - size_mid[0]) // 2, (target_diameter - size_mid[1]) // 2)
                off_sml = ((target_diameter - size_sml[0]) // 2, (target_diameter - size_sml[1]) // 2)
                
                # Scale images
                # Note: target_sprites['inner'] is the Big Background
                layer_3 = pygame.transform.smoothscale(self.game.target_sprites['inner'], size_big)
                # Note: target_sprites['middle'] is the Middle Ring
                layer_2 = pygame.transform.smoothscale(self.game.target_sprites['middle'], size_mid)
                # Note: target_sprites['outer'] is the Small Dot
                layer_1 = pygame.transform.smoothscale(self.game.target_sprites['outer'], size_sml)
                
                # 2. Base Composite (The Original "Done" State)
                base_surf = pygame.Surface(target_size, pygame.SRCALPHA)
                
                # Stack Order: Big (Bottom) -> Mid -> Small (Top)
                base_surf.blit(layer_3, off_big)
                base_surf.blit(layer_2, off_mid)
                base_surf.blit(layer_1, off_sml)
                
                # 3. Create Red Overlay (Only on Outer and Inner layers)
                if remaining_ratio > 0:
                    # Create a composite source for the Red Mask
                    # We want Red on 'Inner' (Big Background) and 'Outer' (Small Dot)
                    mask_source = pygame.Surface(target_size, pygame.SRCALPHA)
                    mask_source.blit(layer_3, off_big)  # Big Background (Red Base)
                    mask_source.blit(layer_1, off_sml)  # Small Dot (Red Top)
                    
                    # Create precise mask from non-transparent pixels
                    # Threshold 200: Shrink outer edge (cut off fuzz)
                    mask_sprite = pygame.mask.from_surface(mask_source, 200)
                    
                    # Geometric Clipping Mask: Force Red Overlay to stay inside visual circle
                    # Draw a perfect circle mask slightly smaller (radius - 2) to clip edges/shadows
                    clip_surf = pygame.Surface(target_size, pygame.SRCALPHA)
                    clip_center = (target_diameter // 2, target_diameter // 2)
                    clip_radius = (target_diameter // 2) - 2
                    pygame.draw.circle(clip_surf, (255, 255, 255, 255), clip_center, clip_radius)
                    mask_clip = pygame.mask.from_surface(clip_surf)
                    
                    # Intersect: Red Overlay = Sprite Shape AND Geometric Circle
                    mask_target = mask_sprite.overlap_mask(mask_clip, (0, 0))
                    
                    # Create mask for the Middle Ring (which we want to keep CLEAR)
                    # We need to position it correctly on a full-size surface to convert to mask
                    surf_mid = pygame.Surface(target_size, pygame.SRCALPHA)
                    surf_mid.blit(layer_2, off_mid)
                    # Threshold 50: Expand hole (include fuzz) to ensure Red doesn't bleed onto Middle
                    mask_middle = pygame.mask.from_surface(surf_mid, 50)
                    
                    # Create mask for the Small Dot (to re-add later)
                    surf_sml = pygame.Surface(target_size, pygame.SRCALPHA)
                    surf_sml.blit(layer_1, off_sml)
                    # Threshold 200: Shrink dot
                    mask_small = pygame.mask.from_surface(surf_sml, 200)
                    
                    # Erase Middle Ring from the Red Mask
                    mask_target.erase(mask_middle, (0, 0))
                    
                    # Re-add Small Dot (because it sits on top of Middle, so erasing Middle might have erased it if they overlap)
                    mask_target.draw(mask_small, (0, 0))
                    
                    # Convert to Red Surface
                    red_surf = mask_target.to_surface(setcolor=(220, 60, 60, 255), unsetcolor=(0, 0, 0, 0))
                    
                    # 4. Create Wedge Mask (The "Remaining Time" shape)
                    # We want to keep the Red Color only on the "Remaining" wedge
                    wedge_surf = pygame.Surface(target_size, pygame.SRCALPHA)
                    
                    center = (target_diameter // 2, target_diameter // 2)
                    radius = target_diameter # Cover corners
                    
                    # Wedge points (Top -> Clockwise)
                    points = [center]
                    start_angle = -math.pi / 2
                    total_angle = 2 * math.pi * remaining_ratio
                    num_points = max(30, int(360 * remaining_ratio))
                    
                    for i in range(num_points + 1):
                         angle = start_angle + (total_angle * i / num_points)
                         px = center[0] + radius * math.cos(angle)
                         py = center[1] + radius * math.sin(angle)
                         points.append((px, py))
                    
                    if len(points) > 2:
                        pygame.draw.polygon(wedge_surf, (255, 255, 255, 255), points)
                    
                    # 5. Apply Wedge to Red Overlay (Mult: Red * White = Red, Red * Transparent = Transparent)
                    red_surf.blit(wedge_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                    
                    # 6. Apply Red Overlay to Base
                    base_surf.blit(red_surf, (0, 0))
                
                # Draw final result centered on target position
                screen_pos = (int(self.game.current_target.x - self.game.current_target.radius),
                              int(self.game.current_target.y - self.game.current_target.radius))
                screen.blit(base_surf, screen_pos)
                
            else:
                # --- FALLBACK MODE (Basic Circles) ---
                # Outer zone (100 points) - Fixed red color
                pygame.draw.circle(screen, (220, 60, 60), 
                                 (int(self.game.current_target.x), int(self.game.current_target.y)), 
                                 int(self.game.current_target.radius))
                
                # Middle zone (125 points) - Fixed white color
                pygame.draw.circle(screen, (240, 240, 240), 
                                 (int(self.game.current_target.x), int(self.game.current_target.y)), 
                                 int(self.game.current_target.radius * 0.65))

                # Inner zone (150 points) - Fixed red color (same as outer)
                pygame.draw.circle(screen, (220, 60, 60), 
                                 (int(self.game.current_target.x), int(self.game.current_target.y)), 
                                 int(self.game.current_target.radius * 0.3))

                
                # Fallback TTL visual (Simple Arc)
                if remaining_ratio > 0:
                    start_angle = -math.pi / 2
                    end_angle = start_angle + (2 * math.pi * remaining_ratio)
                    rect = (self.game.current_target.x - self.game.current_target.radius,
                            self.game.current_target.y - self.game.current_target.radius,
                            self.game.current_target.radius * 2, self.game.current_target.radius * 2)
                    pygame.draw.arc(screen, (255, 255, 255), rect, -end_angle, -start_angle, 3)
        
        # Draw floating texts
        for text in self.game.floating_texts:
            text.draw(screen, self.game.medium_font)
        
        # Draw pop effects
        for effect in self.game.pop_effects:
            effect.draw(screen)
        
        # Draw custom crosshair cursor LAST (so it's on top of everything)
        self.game.draw_crosshair()
        
        # Draw Pause overlay if needed
        if self.game.state == GameState.PAUSED:
            self.draw_pause_overlay(screen)

    def draw_hud(self, screen):
        # Background bar
        pygame.draw.rect(screen, BLACK, (0, 0, WINDOW_WIDTH, 70))
        pygame.draw.rect(screen, WHITE, (0, 0, WINDOW_WIDTH, 70), 2)
        
        # Time remaining with better visual
        time_color = RED if self.game.time_remaining <= 10 else YELLOW if self.game.time_remaining <= 20 else GREEN
        time_text = f"Time: {int(self.game.time_remaining)}s"
        time_surface = self.game.medium_font.render(time_text, True, time_color)
        screen.blit(time_surface, (30, 20))
        
        # Score
        score_text = f"Score: {self.game.stats.score}"
        score_surface = self.game.medium_font.render(score_text, True, ACCENT_GREEN)
        score_rect = score_surface.get_rect(center=(WINDOW_WIDTH // 2 - 150, 35))
        screen.blit(score_surface, score_rect)
        
        # Hits/Misses with better formatting
        stats_text = f"Hits: {self.game.stats.hits}  | Misses: {self.game.stats.user_misses}  |  Target Misses: {self.game.stats.target_misses}"
        stats_surface = self.game.medium_font.render(stats_text, True, WHITE)
        stats_rect = stats_surface.get_rect(right=WINDOW_WIDTH - 30, centery=35)
        screen.blit(stats_surface, stats_rect)
        
        # ESC hint
        hint = self.game.tiny_font.render("Press ESC to pause", True, GRAY)
        screen.blit(hint, (WINDOW_WIDTH - 160, WINDOW_HEIGHT - 25))

    def draw_pause_overlay(self, screen):
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Pause text
        pause_text = self.game.title_font.render("PAUSED", True, YELLOW)
        pause_rect = pause_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100))
        screen.blit(pause_text, pause_rect)
        
        # Instruction text
        instruction_text = self.game.small_font.render("Press ESC to resume or choose an option:", True, LIGHT_GRAY)
        instruction_rect = instruction_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30))
        screen.blit(instruction_text, instruction_rect)
        
        # Draw pause menu buttons
        self.game.resume_button.draw(screen, self.game.medium_font)
        self.game.pause_menu_button.draw(screen, self.game.medium_font)
        self.game.pause_quit_button.draw(screen, self.game.medium_font)

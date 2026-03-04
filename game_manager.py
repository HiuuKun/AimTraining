import random
import pygame
import datetime
from typing import Optional, List, Dict

from constants import *
from target import Target, GameStats

class GameManager:
    """
    Manages the pure game logic, state, and data.
    Does NOT handle drawing, windowing, or UI input (except settings data).
    """
    def __init__(self):
        # Game state
        self.state = GameState.START
        self.stats = GameStats()
        
        # Target settings (Medium preset default)
        self.difficulty = "Medium"
        self.initial_radius = 50
        self.initial_ttl = 2000  # milliseconds
        self.min_radius = 20
        self.min_ttl = 1000
        
        # Gameplay variables
        self.current_target: Optional[Target] = None
        self.game_start_time = 0
        self.time_remaining = GAME_DURATION
        self.spawn_delay = 200  # milliseconds between targets
        self.last_despawn_time = 0
        
        # Pause tracking
        self.pause_start_time = 0
        self.total_pause_time = 0
        
        # Settings (configurable logic data)
        self.game_duration = GAME_DURATION
        self.difficulty_scaling = True
        self.mouse_sensitivity = 1.0
        self.crosshair_size = 20
        self.crosshair_color = GREEN
        self.crosshair_color_name = "Green"
        self.crosshair_type = "Circle"
        self.settings_tab = "difficulty"
    
    def spawn_target(self, window_width, window_height):
        # Calculate difficulty progression
        elapsed_time = self.game_duration - self.time_remaining
        progress = elapsed_time / self.game_duration if self.difficulty_scaling else 0
        
        # Gradually decrease radius and TTL
        radius = max(self.min_radius, self.initial_radius - progress * (self.initial_radius - self.min_radius))
        ttl = max(self.min_ttl, self.initial_ttl - progress * (self.initial_ttl - self.min_ttl))
        
        # Random position (keeping target fully visible)
        # Note: logic needs window dim. Passed as args or stored constants?
        # Using constants is safer for logic if window is fixed.
        x = random.uniform(radius + 10, window_width - radius - 10)
        y = random.uniform(radius + 80, window_height - radius - 10)
        
        self.current_target = Target(x, y, radius, ttl, pygame.time.get_ticks())
    
    def calculate_score(self, reaction_time: float, ttl: float, zone: str = 'outer') -> int:
        if zone == 'inner':
            base_points = 150
        elif zone == 'middle':
            base_points = 125
        else:
            base_points = 100
        
        bonus_cap = 100
        bonus = max(0, (ttl - reaction_time) / ttl * bonus_cap)
        return int(base_points + bonus)
    
    def handle_shot(self, pos: tuple) -> dict:
        """
        Process a shot at the target.
        Returns a dict with result info: {'type': 'hit'|'miss'|'none', ...}
        """
        if self.state != GameState.PLAYING:
            return {'type': 'none'}
            
        if self.current_target and self.current_target.contains_point(pos[0], pos[1]):
            # Hit
            zone = self.current_target.get_hit_zone(pos[0], pos[1])
            current_time = pygame.time.get_ticks()
            reaction_time = current_time - self.current_target.spawn_time
            score_gained = self.calculate_score(reaction_time, self.current_target.ttl, zone)
            
            self.stats.add_hit(reaction_time, score_gained)
            
            # Logic cleanup
            self.last_despawn_time = current_time
            target_x = self.current_target.x
            target_y = self.current_target.y
            target_radius = self.current_target.radius
            self.current_target = None
            
            return {
                'type': 'hit',
                'zone': zone,
                'score': score_gained,
                'x': target_x,
                'y': target_y,
                'radius': target_radius
            }
        else:
            # Miss
            self.stats.add_miss()
            return {
                'type': 'miss',
                'x': pos[0],
                'y': pos[1]
            }

    def start_game(self):
        self.state = GameState.PLAYING
        self.stats = GameStats()
        self.current_target = None
        self.game_start_time = pygame.time.get_ticks()
        self.time_remaining = self.game_duration
        self.last_despawn_time = pygame.time.get_ticks()
        self.spawn_target(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.pause_start_time = 0
        self.total_pause_time = 0
        
    def update(self, dt: float) -> Optional[dict]:
        """
        Updates logic. Returns dict if event happened (e.g. timeout), else None.
        """
        if self.state == GameState.PLAYING:
            # Update timer
            current_time = pygame.time.get_ticks()
            elapsed = (current_time - self.game_start_time - self.total_pause_time) / 1000
            self.time_remaining = max(0, self.game_duration - elapsed)
            
            if self.time_remaining <= 0:
                self.state = GameState.RESULTS
                return {'type': 'game_over'}
            
            # Update target
            if self.current_target:
                if self.current_target.is_expired(current_time):
                    # Timeout
                    self.stats.add_miss()
                    self.last_despawn_time = current_time
                    tx, ty = self.current_target.x, self.current_target.y
                    self.current_target = None
                    return {
                        'type': 'timeout',
                        'x': tx,
                        'y': ty
                    }
            else:
                if current_time - self.last_despawn_time >= self.spawn_delay:
                    self.spawn_target(WINDOW_WIDTH, WINDOW_HEIGHT)
        return None

    def save_score(self):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open("scores.txt", "a") as f:
                f.write(f"{now},{self.stats.score},{self.stats.get_accuracy():.1f},{self.stats.get_avg_reaction_time():.0f}\n")
        except Exception as e:
            print(f"Could not save score: {e}")

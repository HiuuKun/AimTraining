import pygame
import math
from dataclasses import dataclass
from typing import List
from constants import NEON_PURPLE, NEON_MAGENTA, ELECTRIC_PURPLE

@dataclass
class Target:
    x: float
    y: float
    radius: float
    ttl: float  # time to live in milliseconds
    spawn_time: float  # when the target was spawned
    
    def is_expired(self, current_time: float) -> bool:
        return (current_time - self.spawn_time) >= self.ttl
    
    def contains_point(self, px: float, py: float) -> bool:
        distance = math.sqrt((px - self.x) ** 2 + (py - self.y) ** 2)
        return distance <= self.radius
    
    def get_hit_zone(self, px: float, py: float) -> str:
        """Determine which zone was hit: 'inner', 'middle', 'outer', or None"""
        distance = math.sqrt((px - self.x) ** 2 + (py - self.y) ** 2)
        
        # Inner circle: 30% of radius
        if distance <= self.radius * 0.3:
            return 'inner'
        # Middle circle: 30-65% of radius
        elif distance <= self.radius * 0.65:
            return 'middle'
        # Outer circle: 65-100% of radius
        elif distance <= self.radius:
            return 'outer'
        else:
            return None
    
    def get_remaining_time(self, current_time: float) -> float:
        return max(0, self.ttl - (current_time - self.spawn_time))

@dataclass
class GameStats:
    hits: int = 0
    user_misses: int = 0
    target_misses: int = 0
    score: int = 0
    reaction_times: List[float] = None
    
    @property
    def misses(self) -> int:
        return self.user_misses + self.target_misses
    
    def __post_init__(self):
        if self.reaction_times is None:
            self.reaction_times = []
    
    def add_hit(self, reaction_time: float, score_gained: int):
        self.hits += 1
        self.reaction_times.append(reaction_time)
        self.score += score_gained
    
    def add_user_miss(self):
        self.user_misses += 1
        
    def add_target_miss(self):
        self.target_misses += 1
    
    def get_accuracy(self) -> float:
        total = self.hits + self.user_misses
        return (self.hits / total * 100) if total > 0 else 0
    
    def get_avg_reaction_time(self) -> float:
        return sum(self.reaction_times) / len(self.reaction_times) if self.reaction_times else 0
    
    def get_best_reaction_time(self) -> float:
        return min(self.reaction_times) if self.reaction_times else 0


def create_vertical_gradient(size: tuple, colors: list) -> pygame.Surface:
    """Create a vertical gradient surface interpolated between list of colors"""
    width, height = size
    surface = pygame.Surface(size, pygame.SRCALPHA)
    
    if len(colors) < 2:
        if colors:
            surface.fill(colors[0])
        return surface
        
    for y in range(height):
        # Calculate ratio 0.0 to 1.0
        global_ratio = y / (height - 1) if height > 1 else 0
        
        # Determine segments for multi-color gradients
        n_segments = len(colors) - 1
        segment = int(global_ratio * n_segments)
        segment = min(segment, n_segments - 1)
        
        # Local ratio within the segment
        local_ratio = (global_ratio * n_segments) - segment
        
        c1 = colors[segment]
        c2 = colors[segment + 1]
        
        r = int(c1[0] + (c2[0] - c1[0]) * local_ratio)
        g = int(c1[1] + (c2[1] - c1[1]) * local_ratio)
        b = int(c1[2] + (c2[2] - c1[2]) * local_ratio)
        
        pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
        
    return surface

class FloatingText:
    def __init__(self, x: float, y: float, text: str, color: tuple, duration: float = 1000):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.duration = duration
        self.spawn_time = pygame.time.get_ticks()
        self.alpha = 255
    
    def update(self, dt: float):
        elapsed = pygame.time.get_ticks() - self.spawn_time
        self.y -= 0.5  # Float upward
        self.alpha = max(0, 255 - (elapsed / self.duration * 255))
    
    def is_expired(self) -> bool:
        return pygame.time.get_ticks() - self.spawn_time >= self.duration
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font):
        if self.alpha > 0:
            if self.color == NEON_PURPLE:
                # Gradient Neon glow effect (Magenta to Electric Purple)
                # mimicking LinearSegmentedColormap
                
                # Create mask
                text_mask = font.render(self.text, True, (255, 255, 255))
                
                # Create gradient
                gradient = create_vertical_gradient(
                    text_mask.get_size(), 
                    [NEON_MAGENTA, ELECTRIC_PURPLE]
                )
                
                # Apply text mask
                gradient.blit(text_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                
                rect = gradient.get_rect(center=(self.x, self.y))
                
                # 1. Glow layer (Gradient with offsets)
                gradient.set_alpha(int(self.alpha * 0.12))
                # Expanded glow for fuller neon effect
                for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), 
                             (-2, -2), (2, 2), (-2, 2), (2, -2)]:
                    screen.blit(gradient, (rect.x + dx, rect.y + dy))
                
                # 2. Base layer (Gradient - Main Text)
                gradient.set_alpha(int(self.alpha))
                screen.blit(gradient, rect)
            else:
                text_surface = font.render(self.text, True, self.color)
                text_surface.set_alpha(int(self.alpha))
                rect = text_surface.get_rect(center=(self.x, self.y))
                screen.blit(text_surface, rect)

class PopEffect:
    """Visual pop effect when hitting a target"""
    def __init__(self, x: float, y: float, initial_radius: float, color: tuple, duration: float = 400):
        self.x = x
        self.y = y
        self.initial_radius = initial_radius
        self.max_radius = initial_radius * 1.5  # Expand to 150% of original size
        self.current_radius = initial_radius
        self.color = color
        self.duration = duration
        self.spawn_time = pygame.time.get_ticks()
        self.alpha = 255
    
    def update(self, dt: float):
        elapsed = pygame.time.get_ticks() - self.spawn_time
        progress = elapsed / self.duration
        
        # Expand the circle
        self.current_radius = self.initial_radius + (self.max_radius - self.initial_radius) * progress
        
        # Fade out
        self.alpha = max(0, 255 - (progress * 255))
    
    def is_expired(self) -> bool:
        return pygame.time.get_ticks() - self.spawn_time >= self.duration
    
    def draw(self, screen: pygame.Surface):
        if self.alpha > 0:
            # Create a surface for the circle with alpha
            size = int(self.current_radius * 2 + 10)
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            
            # Draw expanding circle with decreasing thickness
            thickness = max(1, int(5 * (1 - (pygame.time.get_ticks() - self.spawn_time) / self.duration)))
            
            # Draw the circle on the surface
            center = (size // 2, size // 2)
            color_with_alpha = (*self.color[:3], int(self.alpha))
            pygame.draw.circle(surf, color_with_alpha, center, int(self.current_radius), thickness)
            
            # Blit to screen
            screen.blit(surf, (int(self.x - size // 2), int(self.y - size // 2)))


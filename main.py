import pygame
import sys
import math
from typing import List

from constants import *
from ui import Button, Slider, ToggleButton
from game_manager import GameManager
from target import FloatingText, PopEffect
from views.gameplay import GameplayView
from views.settings import SettingsView
from views.instructions import InstructionView
from views.menu import MenuView
from views.scoreboard import ScoreboardView

class GameApp:
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Aim Trainer Pro")
        self.clock = pygame.time.Clock()
        
        # Initialize Logic Manager
        self.manager = GameManager()
        
        # Resources / Fonts
        self.title_font = pygame.font.Font(None, 72)
        self.large_font = pygame.font.Font(None, 48)
        self.medium_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 28)
        self.tiny_font = pygame.font.Font(None, 20)
        
        # Load sprites
        self.target_sprites = {}
        try:
            self.target_sprites['middle'] = pygame.image.load("resources/Circle2.png").convert_alpha()
            self.target_sprites['outer'] = pygame.image.load("resources/Circle3.png").convert_alpha()
            self.target_sprites['inner'] = pygame.image.load("resources/Circle1.png").convert_alpha()
        except Exception:
            self.target_sprites = None
            
        # Load sound effects
        self.pop_sound = None
        try:
            pygame.mixer.init()
            pygame.mixer.set_num_channels(32)
            self.pop_sound = pygame.mixer.Sound("resources/dragon-studio-pop-402324.mp3")
            self.pop_sound.set_volume(0.5)  # Set volume to 50%
        except Exception:
            pass  # Sound is optional
            
        # Visual Effects
        self.floating_texts: List[FloatingText] = []
        self.pop_effects: List[PopEffect] = []
        
        # UI Elements
        self.create_buttons()
        self.create_setting_controls()
        
        # Views
        # Note: Views expect 'game' argument. We pass 'self' (GameApp).
        # We must proxy Logic properties for compatibility.
        self.gameplay_view = GameplayView(self)
        self.settings_view = SettingsView(self)
        self.instruction_view = InstructionView(self)
        self.menu_view = MenuView(self)
        self.scoreboard_view = ScoreboardView(self)
        
    # --- Property Proxies for Views ---
    @property
    def state(self): return self.manager.state
    @state.setter
    def state(self, val): self.manager.state = val
    
    @property
    def stats(self): return self.manager.stats
    
    @property
    def current_target(self): return self.manager.current_target
    
    @property
    def crosshair_type(self): return self.manager.crosshair_type
    @crosshair_type.setter
    def crosshair_type(self, val): self.manager.crosshair_type = val
    
    @property
    def crosshair_color(self): return self.manager.crosshair_color
    @crosshair_color.setter
    def crosshair_color(self, val): self.manager.crosshair_color = val
    
    @property
    def settings_tab(self): return self.manager.settings_tab
    @settings_tab.setter
    def settings_tab(self, val): self.manager.settings_tab = val

    @property
    def crosshair_size(self): return self.manager.crosshair_size
    @crosshair_size.setter
    def crosshair_size(self, val): self.manager.crosshair_size = val

    @property
    def crosshair_color_name(self): return self.manager.crosshair_color_name
    @crosshair_color_name.setter
    def crosshair_color_name(self, val): self.manager.crosshair_color_name = val
    
    @property
    def time_remaining(self): return self.manager.time_remaining
    
    @property
    def pause_start_time(self): return self.manager.pause_start_time

    # --- UI Creation ---
    def create_buttons(self):
        bw = 260
        bh = 56
        center_x = WINDOW_WIDTH // 2 - bw // 2
        start_y = 225
        gap = 66
        
        self.start_button = Button(center_x, start_y, bw, bh, "Start Game", NEON_PURPLE)
        self.instructions_button = Button(center_x, start_y + gap, bw, bh, "Instructions", GREEN)
        self.scoreboard_button = Button(center_x, start_y + gap * 2, bw, bh, "Scoreboard", BLUE)
        self.settings_button = Button(center_x, start_y + gap * 3, bw, bh, "Settings", GRAY)
        self.exit_button = Button(center_x, start_y + gap * 4, bw, bh, "Exit Game", RED)
        
        self.restart_button = Button(WINDOW_WIDTH // 2 - 280, WINDOW_HEIGHT - 100, 250, 60, "Play Again", GREEN)
        self.menu_button = Button(WINDOW_WIDTH // 2 + 30, WINDOW_HEIGHT - 100, 250, 60, "Main Menu", BLUE)
        self.back_button = Button(50, WINDOW_HEIGHT - 100, 150, 50, "Back", GRAY)
        
        tab_y = 120
        self.difficulty_tab_button = Button(250, tab_y, 200, 50, "Difficulty", BLUE)
        self.mouse_tab_button = Button(470, tab_y, 200, 50, "Mouse", GREEN)
        
        pause_cx = WINDOW_WIDTH // 2 - 125
        pause_y = WINDOW_HEIGHT // 2 + 50
        self.resume_button = Button(pause_cx, pause_y, 250, 60, "Resume", GREEN)
        self.pause_menu_button = Button(pause_cx, pause_y + 70, 250, 60, "Main Menu", BLUE)
        self.pause_quit_button = Button(pause_cx, pause_y + 140, 250, 60, "Quit Game", RED)

    def create_setting_controls(self):
        # Sync initial values with Manager
        m = self.manager
        btn_w = 400
        btn_h = 60
        gap = 80
        center_x = WINDOW_WIDTH // 2 - btn_w // 2
        
        # Used for the mouse tab
        x, w, y = 280, 380, 220

        self.btn_easy = Button(center_x, 280, btn_w, btn_h, "Easy", GREEN, hover_effect=False)
        self.btn_medium = Button(center_x, 280 + gap, btn_w, btn_h, "Medium", YELLOW, hover_effect=False)
        self.btn_hard = Button(center_x, 280 + gap * 2, btn_w, btn_h, "Hard", RED, hover_effect=False)

        self.duration_slider = Slider(WINDOW_WIDTH // 2 - 200, 560, 400, 30, 120, m.game_duration, "Game Duration (Seconds):", 5)
        self.difficulty_toggle = ToggleButton(WINDOW_WIDTH // 2 - 40, 650, "Difficulty Scaling Enabled:", m.difficulty_scaling)
       
        
        self.sensitivity_slider = Slider(x, y, w, 0.5, 2.0, m.mouse_sensitivity, "Sensitivity:", 0.1)
        self.crosshair_size_slider = Slider(x, y+75, w, 10, 40, m.crosshair_size, "Crosshair Size:", 2)
        
        self.crosshair_colors = {"Green": GREEN, "Red": RED, "Blue": BLUE, "Yellow": YELLOW, "White": WHITE, "Cyan": CYAN}
        self.color_buttons = {}
        for i, (name, color) in enumerate(self.crosshair_colors.items()):
            bx = x + (i%3)*(65)
            by = y+180 + (i//3)*(65)
            self.color_buttons[name] = {"rect": pygame.Rect(bx, by, 50, 50), "color": color, "name": name}
            
        self.type_buttons = {}
        types = ["Circle", "Cross", "Dot", "Plus", "X"]
        for i, ctype in enumerate(types):
            bx = x + (i%3)*(100)
            by = y+370 + (i//3)*(52)
            self.type_buttons[ctype] = {"rect": pygame.Rect(bx, by, 90, 42), "name": ctype}

    def start_game(self):
        self.floating_texts.clear()
        self.pop_effects.clear()
        self.manager.start_game()
        pygame.mouse.set_visible(False)

    def apply_settings(self):
        m = self.manager
        m.game_duration = int(self.duration_slider.value)
        m.difficulty_scaling = self.difficulty_toggle.state
        m.mouse_sensitivity = self.sensitivity_slider.value
        m.crosshair_size = int(self.crosshair_size_slider.value)

    # --- Interaction Handling ---
    def handle_click(self, pos):
        # 1. Handle UI Clicks
        if self.state == GameState.START:
            if self.start_button.is_clicked(pos): self.start_game()
            elif self.instructions_button.is_clicked(pos): self.state = GameState.INSTRUCTIONS
            elif self.scoreboard_button.is_clicked(pos): self.state = GameState.SCOREBOARD
            elif self.settings_button.is_clicked(pos): 
                self.settings_tab = "difficulty"
                self.state = GameState.SETTINGS
            elif self.exit_button.is_clicked(pos): 
                pygame.quit(); sys.exit()
                
        elif self.state == GameState.RESULTS:
            if self.restart_button.is_clicked(pos): self.start_game()
            elif self.menu_button.is_clicked(pos): self.state = GameState.START

        elif self.state == GameState.PAUSED:
            if self.resume_button.is_clicked(pos):
                self.state = GameState.PLAYING
                # Adjust pause time in logic
                pause_duration = pygame.time.get_ticks() - self.manager.pause_start_time
                self.manager.total_pause_time += pause_duration
                if self.manager.current_target: self.manager.current_target.spawn_time += pause_duration
                pygame.mouse.set_visible(False)
            elif self.pause_menu_button.is_clicked(pos):
                self.state = GameState.START
                pygame.mouse.set_visible(True)
            elif self.pause_quit_button.is_clicked(pos):
                pygame.quit(); sys.exit()

        elif self.state in [GameState.INSTRUCTIONS, GameState.SCOREBOARD]:
            if self.back_button.is_clicked(pos): self.state = GameState.START

        elif self.state == GameState.SETTINGS:
            if self.back_button.is_clicked(pos):
                self.apply_settings()
                self.state = GameState.START
            elif self.difficulty_tab_button.is_clicked(pos): self.settings_tab = "difficulty"
            elif self.mouse_tab_button.is_clicked(pos): self.settings_tab = "mouse"
            elif self.settings_tab == "difficulty": 
                if self.difficulty_toggle.is_clicked(pos): self.difficulty_toggle.toggle()
                if self.btn_easy.is_clicked(pos):
                    self.manager.difficulty = "Easy"
                    self.manager.initial_radius, self.manager.min_radius, self.manager.initial_ttl, self.manager.min_ttl = 60, 30, 3000, 1200
                if self.btn_medium.is_clicked(pos):
                    self.manager.difficulty = "Medium"
                    self.manager.initial_radius, self.manager.min_radius, self.manager.initial_ttl, self.manager.min_ttl = 50, 20, 2000, 1000
                if self.btn_hard.is_clicked(pos):
                    self.manager.difficulty = "Hard"
                    self.manager.initial_radius, self.manager.min_radius, self.manager.initial_ttl, self.manager.min_ttl = 40, 15, 1600, 600
            elif self.settings_tab == "mouse":
                for data in self.color_buttons.values():
                    if data["rect"].collidepoint(pos): 
                        self.crosshair_color = data["color"]
                        self.crosshair_color_name = data["name"]
                for data in self.type_buttons.values():
                    if data["rect"].collidepoint(pos): self.crosshair_type = data["name"]

        # 2. Handle Gameplay Clicks
        elif self.state == GameState.PLAYING:
            result = self.manager.handle_shot(pos)
            if result['type'] == 'hit':
                zone_text = "PERFECT!" if result['zone'] == 'inner' else "GREAT!" if result['zone'] == 'middle' else "GOOD!"
                text_color = NEON_PURPLE if result['zone'] == 'inner' else ACCENT_GREEN if result['zone'] == 'middle' else BLUE
                self.floating_texts.append(FloatingText(result['x'], result['y'], f"{zone_text} +{result['score']}", text_color, 800))
                
                # Add pop effect
                pop_color = NEON_PURPLE if result['zone'] == 'inner' else ACCENT_GREEN if result['zone'] == 'middle' else BLUE
                self.pop_effects.append(PopEffect(result['x'], result['y'], result['radius'], pop_color))
                
                # Play pop sound
                if self.pop_sound:
                    self.pop_sound.play()
            elif result['type'] == 'miss':
                self.floating_texts.append(FloatingText(result['x'], result['y'], "MISS", RED, 600))


    def update(self):
        dt = self.clock.tick(FPS)
        # Mouse updates
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        # Update Logic
        logic_res = self.manager.update(dt)
        if logic_res and logic_res['type'] == 'game_over':
            pygame.mouse.set_visible(True)
            self.manager.save_score()
        elif logic_res and logic_res['type'] == 'timeout':
            self.floating_texts.append(FloatingText(logic_res['x'], logic_res['y'], "TIMEOUT", ORANGE, 600))
            
        # UI Updates
        # (Same as old GameManager.update UI parts)
        if self.state == GameState.START:
            self.start_button.update(mouse_pos)
            self.instructions_button.update(mouse_pos)
            self.scoreboard_button.update(mouse_pos)
            self.settings_button.update(mouse_pos)
            self.exit_button.update(mouse_pos)
        # ... (Abbreviated, but full list needed)
        elif self.state == GameState.RESULTS:
            self.restart_button.update(mouse_pos)
            self.menu_button.update(mouse_pos)
        elif self.state == GameState.PAUSED:
            self.resume_button.update(mouse_pos)
            self.pause_menu_button.update(mouse_pos)
            self.pause_quit_button.update(mouse_pos)
        elif self.state in [GameState.INSTRUCTIONS, GameState.SCOREBOARD]:
            self.back_button.update(mouse_pos)
        elif self.state == GameState.SETTINGS:
            self.back_button.update(mouse_pos)
            self.difficulty_tab_button.update(mouse_pos)
            self.mouse_tab_button.update(mouse_pos)
            if self.settings_tab == "difficulty":
                self.difficulty_toggle.update(mouse_pos)
                self.duration_slider.update(mouse_pos, mouse_pressed)
                self.btn_easy.update(mouse_pos)
                self.btn_medium.update(mouse_pos)
                self.btn_hard.update(mouse_pos)
            elif self.settings_tab == "mouse":
                self.sensitivity_slider.update(mouse_pos, mouse_pressed)
                self.crosshair_size_slider.update(mouse_pos, mouse_pressed)

        # Floating text update
        for text in self.floating_texts[:]:
            text.update(dt)
            if text.is_expired(): self.floating_texts.remove(text)
        
        # Pop effects update
        for effect in self.pop_effects[:]:
            effect.update(dt)
            if effect.is_expired(): self.pop_effects.remove(effect)

    def draw(self):
        # Gradient BG
        for y in range(WINDOW_HEIGHT):
            ratio = y / WINDOW_HEIGHT
            r = int(BG_DARK[0] + (BG_MEDIUM[0]-BG_DARK[0])*ratio)
            g = int(BG_DARK[1] + (BG_MEDIUM[1]-BG_DARK[1])*ratio)
            b = int(BG_DARK[2] + (BG_MEDIUM[2]-BG_DARK[2])*ratio)
            pygame.draw.line(self.screen, (r,g,b), (0,y), (WINDOW_WIDTH,y))
            
        # Draw View
        if self.state == GameState.START: self.menu_view.draw_start_screen(self.screen)
        elif self.state == GameState.PLAYING: self.gameplay_view.draw(self.screen)
        elif self.state == GameState.PAUSED: self.gameplay_view.draw(self.screen)
        elif self.state == GameState.RESULTS: self.menu_view.draw_results_screen(self.screen)
        elif self.state == GameState.INSTRUCTIONS: self.instruction_view.draw(self.screen)
        elif self.state == GameState.SETTINGS: self.settings_view.draw(self.screen)
        elif self.state == GameState.SCOREBOARD: self.scoreboard_view.draw(self.screen)
        
        pygame.display.flip()

    # Helpers for Views (compatibility)
    def draw_particles(self): pass # removed
    def draw_crosshair(self):
        mx, my = pygame.mouse.get_pos()
        self.draw_crosshair_at(mx, my, self.crosshair_size)
        
    def draw_crosshair_at(self, x, y, size):
        color = self.crosshair_color
        ctype = self.crosshair_type
        
        if ctype == "Circle":
            pygame.draw.circle(self.screen, color, (x, y), size // 2, 2)
            pygame.draw.circle(self.screen, color, (x, y), 2)
            line_length = size // 2 + 5
            gap = 5
            pygame.draw.line(self.screen, color, (x, y - line_length), (x, y - gap), 2)
            pygame.draw.line(self.screen, color, (x, y + gap), (x, y + line_length), 2)
            pygame.draw.line(self.screen, color, (x - line_length, y), (x - gap, y), 2)
            pygame.draw.line(self.screen, color, (x + gap, y), (x + line_length, y), 2)
        elif ctype == "Cross":
            line_length = size // 2 + 5
            pygame.draw.line(self.screen, color, (x, y - line_length), (x, y + line_length), 2)
            pygame.draw.line(self.screen, color, (x - line_length, y), (x + line_length, y), 2)
            pygame.draw.circle(self.screen, color, (x, y), 2)
        elif ctype == "Dot":
            pygame.draw.circle(self.screen, color, (x, y), size // 4, 2)
            pygame.draw.circle(self.screen, color, (x, y), 3)
        elif ctype == "Plus":
            line_length = size // 2 + 5
            gap = size // 4
            pygame.draw.line(self.screen, color, (x, y - line_length), (x, y - gap), 3)
            pygame.draw.line(self.screen, color, (x, y + gap), (x, y + line_length), 3)
            pygame.draw.line(self.screen, color, (x - line_length, y), (x - gap, y), 3)
            pygame.draw.line(self.screen, color, (x + gap, y), (x + line_length, y), 3)
        elif ctype == "X":
            line_length = size // 2 + 3
            pygame.draw.line(self.screen, color, (x - line_length, y - line_length), (x + line_length, y + line_length), 2)
            pygame.draw.line(self.screen, color, (x + line_length, y - line_length), (x - line_length, y + line_length), 2)
            pygame.draw.circle(self.screen, color, (x, y), 2)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                        self.manager.pause_start_time = pygame.time.get_ticks()
                        pygame.mouse.set_visible(True)
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING
                        pause_d = pygame.time.get_ticks() - self.manager.pause_start_time
                        self.manager.total_pause_time += pause_d
                        if self.manager.current_target: self.manager.current_target.spawn_time += pause_d
                        pygame.mouse.set_visible(False)
            self.update()
            self.draw()
        pygame.quit(); sys.exit()

if __name__ == "__main__":
    app = GameApp()
    app.run()
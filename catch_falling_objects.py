import pygame
import sys
import random
import time
import os
import struct
import wave
import math

# Initialize pygame
pygame.init()
pygame.mixer.init()

class FallingObject:
    def __init__(self, x, y, speed, object_type):
        self.x = x
        self.y = y
        self.speed = speed
        self.type = object_type  # 0 = good, 1 = bad
        self.width = 40
        self.height = 40
        self.caught = False
        self.missed = False
    
    def update(self, dt):
        self.y += self.speed * dt
        
    def draw(self, screen):
        if self.type == 0:  # Good object (apple)
            color = (255, 0, 0)  # Red
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 20)
            # Draw stem
            pygame.draw.rect(screen, (101, 67, 33), (int(self.x - 2), int(self.y - 25), 4, 10))
            # Draw leaf
            pygame.draw.ellipse(screen, (0, 128, 0), (int(self.x + 2), int(self.y - 25), 10, 6))
        else:  # Bad object (rock)
            color = (100, 100, 100)  # Gray
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 20)
            # Add some texture to the rock
            for i in range(3):
                pygame.draw.circle(screen, (80, 80, 80), 
                                  (int(self.x - 5 + i*10), int(self.y - 5)), 5)

    def check_caught(self, basket_x, basket_width, basket_y):
        if (self.y >= basket_y - 10 and 
            self.y <= basket_y + 10 and 
            self.x >= basket_x - basket_width//2 and 
            self.x <= basket_x + basket_width//2):
            return True
        return False
        
    def check_missed(self, screen_height):
        if self.y > screen_height:
            return True
        return False


class CatchGame:
    # Constants
    WIDTH, HEIGHT = 800, 600
    BG_COLOR = (135, 206, 235)  # Sky blue
    TEXT_COLOR = (0, 0, 0)  # Black
    TITLE_COLOR = (0, 100, 0)  # Dark green
    BUTTON_COLOR = (70, 130, 180)  # Steel blue
    BUTTON_HOVER_COLOR = (100, 149, 237)  # Cornflower blue
    BUTTON_SELECTED_COLOR = (25, 25, 112)  # Midnight blue
    GAME_DURATION = 60  # Game lasts 60 seconds

    # Difficulty settings
    DIFFICULTY = {
        "Easy": {"spawn_rate": 1.5, "speed_range": (100, 200)},
        "Medium": {"spawn_rate": 1.0, "speed_range": (150, 250)},
        "Hard": {"spawn_rate": 0.7, "speed_range": (200, 300)}
    }

    def __init__(self):
        # Set up the display
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Catch the Falling Objects")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.title_font = pygame.font.SysFont(None, 72, bold=True)
        
        # Game state
        self.score = 0
        self.misses = 0
        self.game_start_time = None
        self.game_over = False
        self.last_spawn_time = 0
        self.current_difficulty = "Medium"
        self.game_state = "menu"  # Can be "menu", "playing", "game_over"
        
        # Player's basket
        self.basket_width = 100
        self.basket_height = 50
        self.basket_x = self.WIDTH // 2
        self.basket_y = self.HEIGHT - 50
        
        # Falling objects
        self.objects = []
        
        # Load sounds
        self.sound_dir = os.path.join(os.path.dirname(__file__), "sounds")
        self.load_sounds()

    def load_sounds(self):
        """Load game sound effects"""
        self.sounds = {}
        
        # Create simple sound files if they don't exist
        self.create_default_sounds()
        
        # Load the sounds
        try:
            self.sounds["catch"] = pygame.mixer.Sound(os.path.join(self.sound_dir, "catch.wav"))
            self.sounds["miss"] = pygame.mixer.Sound(os.path.join(self.sound_dir, "miss.wav"))
            self.sounds["bad_catch"] = pygame.mixer.Sound(os.path.join(self.sound_dir, "bad_catch.wav"))
        except:
            print("Warning: Could not load sound files")

    def create_default_sounds(self):
        """Create simple sound files if they don't exist"""
        import wave
        import struct
        
        # Only create if they don't exist
        if not os.path.exists(self.sound_dir):
            os.makedirs(self.sound_dir)
            
        # Create a simple catch sound
        if not os.path.exists(os.path.join(self.sound_dir, "catch.wav")):
            self.create_simple_sound(os.path.join(self.sound_dir, "catch.wav"), 
                                    frequency=600, duration=0.15, volume=0.8)
            
        # Create a simple miss sound
        if not os.path.exists(os.path.join(self.sound_dir, "miss.wav")):
            self.create_simple_sound(os.path.join(self.sound_dir, "miss.wav"), 
                                    frequency=200, duration=0.2, volume=0.5)
            
        # Create a simple bad catch sound
        if not os.path.exists(os.path.join(self.sound_dir, "bad_catch.wav")):
            self.create_simple_sound(os.path.join(self.sound_dir, "bad_catch.wav"), 
                                    frequency=300, duration=0.3, volume=0.7)

    def create_simple_sound(self, filename, frequency=440, duration=0.5, volume=1.0):
        """Create a simple sine wave sound file"""
        sample_rate = 44100
        num_samples = int(duration * sample_rate)
        
        # Create sine wave
        buf = []
        for i in range(num_samples):
            sample = int(32767.0 * volume * 
                        math.sin(2 * math.pi * frequency * i / sample_rate))
            buf.append(struct.pack('h', sample))
        
        # Write to file
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(b''.join(buf))

    def draw_button(self, rect, color, text, hover=False):
        """Helper to draw a button with proper text centering"""
        # Draw button background
        pygame.draw.rect(self.screen, color, rect, 0, 10)
        
        # Draw text
        text_surf = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)
        
        # Return True if mouse is over button and clicked
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        
        if rect.collidepoint(mouse_pos):
            if hover:
                pygame.draw.rect(self.screen, self.BUTTON_HOVER_COLOR, rect, 0, 10)
                self.screen.blit(text_surf, text_rect)
            return mouse_clicked
        
        return False

    def draw_basket(self):
        """Draw the player's basket"""
        # Draw basket
        basket_rect = pygame.Rect(
            self.basket_x - self.basket_width // 2,
            self.basket_y - self.basket_height // 2,
            self.basket_width,
            self.basket_height
        )
        
        # Draw basket body (brown)
        pygame.draw.rect(self.screen, (139, 69, 19), basket_rect, 0, 5)
        
        # Draw basket rim
        pygame.draw.rect(self.screen, (101, 67, 33), 
                        (basket_rect.left, basket_rect.top, basket_rect.width, 10), 0, 5)
        
        # Draw basket handle
        handle_height = 20
        handle_width = self.basket_width // 2
        handle_rect = pygame.Rect(
            self.basket_x - handle_width // 2,
            self.basket_y - self.basket_height // 2 - handle_height,
            handle_width,
            handle_height
        )
        pygame.draw.rect(self.screen, (101, 67, 33), handle_rect, 3, 5)

    def show_menu(self):
        """Display the main menu"""
        # Background - sky with clouds
        self.screen.fill(self.BG_COLOR)
        
        # Draw some clouds
        for i in range(5):
            cloud_x = 100 + i * 150
            cloud_y = 100 + (i % 3) * 50
            self.draw_cloud(cloud_x, cloud_y)
        
        # Draw ground
        pygame.draw.rect(self.screen, (76, 153, 0), (0, self.HEIGHT - 20, self.WIDTH, 20))
        
        # Title
        title_shadow = self.title_font.render("CATCH THE FALLING OBJECTS", True, (0, 0, 0))
        title_text = self.title_font.render("CATCH THE FALLING OBJECTS", True, self.TITLE_COLOR)
        shadow_rect = title_shadow.get_rect(center=(self.WIDTH // 2 + 4, 74))
        title_rect = title_text.get_rect(center=(self.WIDTH // 2, 70))
        self.screen.blit(title_shadow, shadow_rect)
        self.screen.blit(title_text, title_rect)
        
        # Start game button
        start_button = pygame.Rect(self.WIDTH // 2 - 150, 150, 300, 60)
        if self.draw_button(start_button, self.BUTTON_COLOR, "Start Game", True):
            self.reset_game()
            self.game_state = "playing"
        
        # Difficulty label
        diff_label = self.font.render("Select Difficulty:", True, self.TEXT_COLOR)
        diff_label_rect = diff_label.get_rect(center=(self.WIDTH // 2, 250))
        self.screen.blit(diff_label, diff_label_rect)
        
        # Difficulty buttons
        difficulties = ["Easy", "Medium", "Hard"]
        for i, diff in enumerate(difficulties):
            y_pos = 300 + i * 80
            diff_button = pygame.Rect(self.WIDTH // 2 - 150, y_pos, 300, 60)
            
            # Use selected color if this is the current difficulty
            button_color = self.BUTTON_SELECTED_COLOR if diff == self.current_difficulty else self.BUTTON_COLOR
            
            # Draw selection indicator
            if diff == self.current_difficulty:
                indicator = pygame.Rect(self.WIDTH // 2 - 170, y_pos + 20, 10, 20)
                pygame.draw.rect(self.screen, (255, 215, 0), indicator)
            
            # Draw the button and check for clicks
            if self.draw_button(diff_button, button_color, diff, diff != self.current_difficulty):
                if diff != self.current_difficulty:
                    self.current_difficulty = diff
                    pygame.time.delay(200)  # Prevent multiple clicks
        
        # Instructions
        instructions = [
            "Catch the falling apples with your basket",
            "Avoid catching rocks",
            "Move the basket with your mouse"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.font.render(instruction, True, self.TEXT_COLOR)
            text_rect = text.get_rect(center=(self.WIDTH // 2, 500 + i * 30))
            self.screen.blit(text, text_rect)

    def draw_cloud(self, x, y):
        """Draw a simple cloud"""
        cloud_color = (255, 255, 255)
        pygame.draw.circle(self.screen, cloud_color, (x, y), 30)
        pygame.draw.circle(self.screen, cloud_color, (x + 20, y - 10), 25)
        pygame.draw.circle(self.screen, cloud_color, (x + 40, y), 30)
        pygame.draw.circle(self.screen, cloud_color, (x + 20, y + 10), 25)

    def show_game_over(self):
        """Display the game over screen"""
        # Background - sky with clouds
        self.screen.fill(self.BG_COLOR)
        
        # Draw some clouds
        for i in range(5):
            cloud_x = 100 + i * 150
            cloud_y = 100 + (i % 3) * 50
            self.draw_cloud(cloud_x, cloud_y)
        
        # Draw ground
        pygame.draw.rect(self.screen, (76, 153, 0), (0, self.HEIGHT - 20, self.WIDTH, 20))
        
        # Game over text
        game_over_shadow = self.title_font.render("GAME OVER", True, (0, 0, 0))
        game_over_text = self.title_font.render("GAME OVER", True, self.TITLE_COLOR)
        shadow_rect = game_over_shadow.get_rect(center=(self.WIDTH // 2 + 4, 74))
        text_rect = game_over_text.get_rect(center=(self.WIDTH // 2, 70))
        self.screen.blit(game_over_shadow, shadow_rect)
        self.screen.blit(game_over_text, text_rect)
        
        # Create a stats panel
        stats_panel = pygame.Rect(self.WIDTH // 2 - 200, 150, 400, 200)
        pygame.draw.rect(self.screen, (255, 255, 255, 200), stats_panel, 0, 10)
        pygame.draw.rect(self.screen, (0, 0, 0), stats_panel, 2, 10)
        
        # Stats text
        stats_texts = [
            f"Final Score: {self.score}",
            f"Misses: {self.misses}",
            f"Difficulty: {self.current_difficulty}"
        ]
        
        for i, text in enumerate(stats_texts):
            text_surf = self.font.render(text, True, self.TEXT_COLOR)
            text_rect = text_surf.get_rect(center=(stats_panel.centerx, stats_panel.y + 50 + i * 50))
            self.screen.blit(text_surf, text_rect)
        
        # Draw menu button
        menu_button = pygame.Rect(self.WIDTH // 2 - 150, 400, 300, 60)
        if self.draw_button(menu_button, self.BUTTON_COLOR, "Main Menu", True):
            self.game_state = "menu"

    def draw_game_ui(self):
        """Draw the game UI elements"""
        # Draw UI panel at the top
        panel_rect = pygame.Rect(0, 0, self.WIDTH, 50)
        pygame.draw.rect(self.screen, (255, 255, 255, 180), panel_rect)
        pygame.draw.line(self.screen, (0, 0, 0), (0, 50), (self.WIDTH, 50), 2)
        
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, self.TEXT_COLOR)
        self.screen.blit(score_text, (20, 10))
        
        # Misses
        misses_text = self.font.render(f"Misses: {self.misses}", True, self.TEXT_COLOR)
        misses_rect = misses_text.get_rect(midright=(self.WIDTH - 20, 25))
        self.screen.blit(misses_text, misses_rect)
        
        # Timer
        elapsed = time.time() - self.game_start_time if self.game_start_time else 0
        remaining = max(0, self.GAME_DURATION - elapsed)
        
        # Timer text
        timer_text = self.font.render(f"Time: {int(remaining)}s", True, self.TEXT_COLOR)
        timer_rect = timer_text.get_rect(center=(self.WIDTH // 2, 25))
        self.screen.blit(timer_text, timer_rect)

    def reset_game(self):
        """Reset the game state to start a new game"""
        self.score = 0
        self.misses = 0
        self.game_start_time = time.time()
        self.last_spawn_time = time.time()
        self.game_over = False
        self.objects = []
        
        # Set difficulty parameters
        self.spawn_rate = self.DIFFICULTY[self.current_difficulty]["spawn_rate"]
        self.speed_range = self.DIFFICULTY[self.current_difficulty]["speed_range"]

    def spawn_object(self):
        """Spawn a new falling object"""
        x = random.randint(50, self.WIDTH - 50)
        y = -20  # Start above the screen
        speed = random.randint(self.speed_range[0], self.speed_range[1])
        object_type = 0 if random.random() < 0.7 else 1  # 70% chance for good objects
        
        self.objects.append(FallingObject(x, y, speed, object_type))

    def update(self, dt):
        """Update game state"""
        # Check if game is over
        if self.game_start_time is not None and time.time() - self.game_start_time >= self.GAME_DURATION:
            self.game_over = True
            self.game_state = "game_over"
            return
            
        # Update basket position to follow mouse
        mouse_x, _ = pygame.mouse.get_pos()
        self.basket_x = mouse_x
        
        # Spawn new objects
        current_time = time.time()
        if current_time - self.last_spawn_time > self.spawn_rate:
            self.spawn_object()
            self.last_spawn_time = current_time
        
        # Update falling objects
        objects_to_remove = []
        for obj in self.objects:
            obj.update(dt)
            
            # Check if object is caught
            if not obj.caught and not obj.missed and obj.check_caught(self.basket_x, self.basket_width, self.basket_y):
                obj.caught = True
                if obj.type == 0:  # Good object
                    self.score += 10
                    if "catch" in self.sounds:
                        self.sounds["catch"].play()
                else:  # Bad object
                    self.score -= 5
                    if "bad_catch" in self.sounds:
                        self.sounds["bad_catch"].play()
                objects_to_remove.append(obj)
            
            # Check if object is missed
            elif not obj.caught and not obj.missed and obj.check_missed(self.HEIGHT):
                obj.missed = True
                if obj.type == 0:  # Only count misses for good objects
                    self.misses += 1
                    if "miss" in self.sounds:
                        self.sounds["miss"].play()
                objects_to_remove.append(obj)
        
        # Remove caught or missed objects
        for obj in objects_to_remove:
            self.objects.remove(obj)

    def handle_events(self):
        """Process pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        
        return True

    def run(self):
        """Main game loop"""
        running = True
        last_time = time.time()
        
        while running:
            # Calculate delta time
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            
            # Handle events
            running = self.handle_events()
            
            # Update game state if playing
            if self.game_state == "playing" and not self.game_over:
                self.update(dt)
            
            # Draw everything
            if self.game_state == "menu":
                self.show_menu()
            elif self.game_state == "playing":
                # Draw background - sky with clouds
                self.screen.fill(self.BG_COLOR)
                
                # Draw some clouds
                for i in range(5):
                    cloud_x = 100 + i * 150
                    cloud_y = 100 + (i % 3) * 50
                    self.draw_cloud(cloud_x, cloud_y)
                
                # Draw ground
                pygame.draw.rect(self.screen, (76, 153, 0), (0, self.HEIGHT - 20, self.WIDTH, 20))
                
                # Draw falling objects
                for obj in self.objects:
                    obj.draw(self.screen)
                
                # Draw basket
                self.draw_basket()
                
                # Draw UI
                self.draw_game_ui()
                
            elif self.game_state == "game_over":
                self.show_game_over()
            
            # Update the display
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()


def main():
    game = CatchGame()
    game.run()

if __name__ == "__main__":
    main()

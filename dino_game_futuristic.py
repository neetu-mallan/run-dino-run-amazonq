#!/usr/bin/env python3
import pygame
import random
import sys
import os
import math  # Import the standard math module

# Initialize pygame
pygame.init()
pygame.mixer.init()  # Initialize the mixer for sound

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
GROUND_HEIGHT = 350
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)

# Futuristic color palette
NEON_BLUE = (0, 195, 255)
NEON_PINK = (255, 0, 153)
NEON_GREEN = (57, 255, 20)
DARK_PURPLE = (28, 12, 91)
CYBER_YELLOW = (255, 211, 25)

# Game variables
score = 0
game_speed = 10
high_score = 0

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Futuristic T-Rex Runner")
clock = pygame.time.Clock()

# Load font
try:
    font = pygame.font.SysFont("Arial", 20)
    title_font = pygame.font.SysFont("Arial", 30, bold=True)
except:
    font = pygame.font.Font(None, 20)
    title_font = pygame.font.Font(None, 30)

# Sound variables
jump_sound = None
collision_sound = None
point_sound = None

# Create sound files
def create_sound_files():
    global jump_sound, collision_sound, point_sound
    
    # Create a simple jump sound
    sample_rate = 44100
    duration = 0.2  # seconds
    frequency = 800  # Hz
    
    # Generate a simple sine wave for jump sound
    buf = []
    for i in range(int(duration * sample_rate)):
        t = i / sample_rate
        value = int(127 * (0.5 + 0.5 * math.sin(2 * math.pi * frequency * t)))
        buf.append(value)
    
    jump_sound = pygame.mixer.Sound(buffer=bytes(buf))
    
    # Create a simple collision sound (lower tone)
    duration = 0.3  # seconds
    frequency = 200  # Hz
    
    # Generate a simple sine wave with decay for collision sound
    buf = []
    for i in range(int(duration * sample_rate)):
        t = i / sample_rate
        decay = 1 - (t / duration)
        value = int(127 * decay * (0.5 + 0.5 * math.sin(2 * math.pi * frequency * t)))
        buf.append(value)
    
    collision_sound = pygame.mixer.Sound(buffer=bytes(buf))
    
    # Create a simple point sound (high beep)
    duration = 0.1  # seconds
    frequency = 1200  # Hz
    
    # Generate a simple sine wave for point sound
    buf = []
    for i in range(int(duration * sample_rate)):
        t = i / sample_rate
        value = int(127 * (0.5 + 0.5 * math.sin(2 * math.pi * frequency * t)))
        buf.append(value)
    
    point_sound = pygame.mixer.Sound(buffer=bytes(buf))

# Try to create sound files
try:
    create_sound_files()
    print("Sound effects created successfully!")
except Exception as e:
    print(f"Could not create sound files: {e}. Game will run without sound.")

# Create futuristic background elements
def create_grid_background():
    bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    bg.fill(DARK_PURPLE)
    
    # Draw horizontal grid lines
    for y in range(0, SCREEN_HEIGHT, 20):
        alpha = 100 - (y // 4)  # Lines fade with distance
        if alpha < 0:
            alpha = 0
        line_color = (NEON_BLUE[0], NEON_BLUE[1], NEON_BLUE[2], alpha)
        line_surf = pygame.Surface((SCREEN_WIDTH, 1), pygame.SRCALPHA)
        line_surf.fill(line_color)
        bg.blit(line_surf, (0, y))
    
    # Draw vertical grid lines
    for x in range(0, SCREEN_WIDTH, 40):
        pygame.draw.line(bg, (NEON_BLUE[0], NEON_BLUE[1], NEON_BLUE[2], 30), (x, 0), (x, GROUND_HEIGHT), 1)
    
    return bg

# Create background
background = create_grid_background()

# Create stars for the background
stars = []
for _ in range(50):
    stars.append([random.randint(0, SCREEN_WIDTH), random.randint(0, GROUND_HEIGHT - 50), random.randint(1, 3)])

class TRex:
    def __init__(self):
        # Create a T-Rex shape
        self.width = 60
        self.height = 70
        self.x = 80
        self.y = GROUND_HEIGHT - self.height
        self.jump_vel = 8.5
        self.is_jumping = False
        self.is_ducking = False
        self.vel_y = 0
        self.step_index = 0
        
        # Create T-Rex images for animation
        self.run_imgs = []
        for i in range(2):
            img = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            
            # T-Rex body (dark green with neon highlights)
            body_color = (20, 100, 50)
            highlight_color = NEON_GREEN
            
            # Body
            pygame.draw.ellipse(img, body_color, (5, 10, self.width-15, self.height-30))
            
            # Head
            pygame.draw.ellipse(img, body_color, (self.width-25, 5, 25, 20))
            
            # Jaw
            pygame.draw.ellipse(img, body_color, (self.width-20, 15, 20, 10))
            
            # Tail
            pygame.draw.ellipse(img, body_color, (0, 20, 20, 10))
            
            # Legs
            leg_height = 25 if i == 0 else 20
            pygame.draw.rect(img, body_color, (15, self.height-leg_height, 10, leg_height))
            pygame.draw.rect(img, body_color, (35, self.height-leg_height-5, 10, leg_height+5))
            
            # Neon highlights
            pygame.draw.line(img, highlight_color, (10, 20), (self.width-20, 20), 2)
            pygame.draw.line(img, highlight_color, (self.width-15, 10), (self.width-5, 10), 2)
            
            # Eye (glowing)
            pygame.draw.circle(img, NEON_BLUE, (self.width-10, 10), 4)
            pygame.draw.circle(img, WHITE, (self.width-10, 10), 2)
            
            # Teeth
            for j in range(3):
                pygame.draw.rect(img, WHITE, (self.width-15+j*5, 20, 2, 4))
            
            self.run_imgs.append(img)
            
        # Jump image
        self.jump_img = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        # Copy the first run image but adjust the legs
        self.jump_img.blit(self.run_imgs[0], (0, 0))
        # Clear the leg area
        pygame.draw.rect(self.jump_img, (0, 0, 0, 0), (10, self.height-30, 40, 30))
        # Draw tucked legs
        pygame.draw.ellipse(self.jump_img, body_color, (15, self.height-20, 30, 15))
        
        # Duck image (shorter and longer)
        self.duck_img = pygame.Surface((self.width+10, self.height-20), pygame.SRCALPHA)
        # Stretched body
        pygame.draw.ellipse(self.duck_img, body_color, (5, 5, self.width, 20))
        # Head
        pygame.draw.ellipse(self.duck_img, body_color, (self.width-15, 0, 25, 15))
        # Jaw
        pygame.draw.ellipse(self.duck_img, body_color, (self.width-10, 10, 20, 8))
        # Eye
        pygame.draw.circle(self.duck_img, NEON_BLUE, (self.width-5, 5), 3)
        pygame.draw.circle(self.duck_img, WHITE, (self.width-5, 5), 1)
        # Neon highlights
        pygame.draw.line(self.duck_img, highlight_color, (10, 10), (self.width-20, 10), 2)
        
        self.image = self.run_imgs[0]
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        
        # Add neon trail effect
        self.trail_positions = []
        
    def update(self, user_input):
        if self.is_jumping:
            self.jump()
        elif self.is_ducking:
            self.duck()
        elif not (self.is_jumping and self.is_ducking):
            self.run()
            
        if user_input[pygame.K_UP] and not self.is_jumping:
            self.is_jumping = True
            self.is_ducking = False
            # Play jump sound
            if jump_sound:
                jump_sound.play()
        elif user_input[pygame.K_DOWN] and not self.is_jumping:
            self.is_ducking = True
        elif not (user_input[pygame.K_DOWN]):
            self.is_ducking = False
            
        # Animation
        if self.step_index >= 10:
            self.step_index = 0
            
        # Update trail
        if len(self.trail_positions) > 5:
            self.trail_positions.pop(0)
        self.trail_positions.append((self.rect.x, self.rect.y))
            
    def jump(self):
        self.image = self.jump_img
        if self.is_jumping:
            self.rect.y -= self.vel_y * 4
            self.vel_y -= 0.8
            
        if self.vel_y < -self.jump_vel:
            self.is_jumping = False
            self.vel_y = self.jump_vel
            self.rect.y = self.y
            
    def duck(self):
        self.image = self.duck_img
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y + 20  # Adjust y position when ducking
        self.step_index += 1
            
    def run(self):
        self.image = self.run_imgs[self.step_index // 5]
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.step_index += 1
        
    def draw(self, screen):
        # Draw trail effect
        for i, pos in enumerate(self.trail_positions):
            alpha = 50 * (i / len(self.trail_positions))
            size = 10 + (i * 3)
            trail_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, (NEON_GREEN[0], NEON_GREEN[1], NEON_GREEN[2], alpha), 
                              (size//2, size//2), size//2)
            screen.blit(trail_surf, (pos[0] + self.width//2 - size//2, pos[1] + self.height//2 - size//2))
        
        screen.blit(self.image, self.rect)

class FuturisticObstacle:
    def __init__(self, image, type):
        self.image = image
        self.type = type
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        
    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            # Find this obstacle in the list and remove it
            if self in obstacles:
                obstacles.remove(self)
            
    def draw(self, screen):
        screen.blit(self.image, self.rect)

class CyberCactus(FuturisticObstacle):
    def __init__(self, image=None):
        self.type = random.randint(0, 2)
        
        # Create futuristic cactus/spike images
        if self.type == 0:
            # Small spike
            width, height = 20, 40
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            # Base
            pygame.draw.rect(self.image, NEON_PINK, (0, height-10, width, 10))
            # Spike
            pygame.draw.polygon(self.image, NEON_PINK, [(width//2, 0), (0, height-10), (width, height-10)])
            # Highlight
            pygame.draw.line(self.image, WHITE, (width//2, 5), (width//2, height-15), 2)
        elif self.type == 1:
            # Medium spike cluster
            width, height = 40, 60
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            # Base
            pygame.draw.rect(self.image, NEON_PINK, (0, height-10, width, 10))
            # Multiple spikes
            pygame.draw.polygon(self.image, NEON_PINK, [(10, 10), (0, height-10), (20, height-10)])
            pygame.draw.polygon(self.image, NEON_PINK, [(30, 0), (20, height-10), (40, height-10)])
            # Highlights
            pygame.draw.line(self.image, WHITE, (10, 15), (10, height-15), 1)
            pygame.draw.line(self.image, WHITE, (30, 5), (30, height-15), 1)
        else:
            # Large energy barrier
            width, height = 50, 80
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            # Base
            pygame.draw.rect(self.image, NEON_BLUE, (0, height-10, width, 10))
            # Energy field
            for i in range(0, height-10, 5):
                alpha = 150 - i
                if alpha < 0:
                    alpha = 0
                pygame.draw.rect(self.image, (NEON_BLUE[0], NEON_BLUE[1], NEON_BLUE[2], alpha), 
                                (5, i, width-10, 5))
            # Frame
            pygame.draw.rect(self.image, NEON_BLUE, (0, 0, 5, height))
            pygame.draw.rect(self.image, NEON_BLUE, (width-5, 0, 5, height))
            
        super().__init__(self.image, self.type)
        self.rect.y = GROUND_HEIGHT - height
        
        # Add pulsing effect variables
        self.pulse_counter = random.randint(0, 20)
        self.original_image = self.image.copy()

    def update(self):
        super().update()
        
        # Pulsing effect
        self.pulse_counter += 1
        if self.pulse_counter > 20:
            self.pulse_counter = 0
            
        pulse_intensity = abs(10 - self.pulse_counter) / 10
        
        # Create a copy of the original image for the pulse effect
        self.image = self.original_image.copy()
        
        # Add a glow based on the type
        glow_color = NEON_PINK if self.type < 2 else NEON_BLUE
        glow_surf = pygame.Surface((self.rect.width + 10, self.rect.height + 10), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (glow_color[0], glow_color[1], glow_color[2], 50 * pulse_intensity), 
                        (0, 0, self.rect.width + 10, self.rect.height + 10))
        
        # Blit the glow onto the image
        temp_surf = pygame.Surface((self.rect.width + 10, self.rect.height + 10), pygame.SRCALPHA)
        temp_surf.blit(glow_surf, (0, 0))
        temp_surf.blit(self.image, (5, 5))
        self.image = temp_surf
        self.rect = self.image.get_rect(bottomright=self.rect.bottomright)

class CyberDrone(FuturisticObstacle):
    def __init__(self):
        self.type = 0
        
        # Create futuristic drone images for animation
        self.images = []
        for i in range(2):
            # Drone with different propeller positions
            width, height = 50, 30
            img = pygame.Surface((width, height), pygame.SRCALPHA)
            
            # Drone body
            pygame.draw.ellipse(img, GRAY, (10, 10, 30, 15))
            
            # Propellers
            prop_y = 5 if i == 0 else 15
            pygame.draw.ellipse(img, NEON_BLUE, (5, prop_y, 10, 5))
            pygame.draw.ellipse(img, NEON_BLUE, (35, prop_y, 10, 5))
            
            # Lights
            pygame.draw.circle(img, NEON_RED, (15, 15), 3)
            pygame.draw.circle(img, NEON_GREEN, (35, 15), 3)
            
            # Scanner beam
            beam_height = 50 if i == 0 else 30
            beam_surf = pygame.Surface((20, beam_height), pygame.SRCALPHA)
            for j in range(beam_height):
                alpha = 150 - (j * 3)
                if alpha < 0:
                    alpha = 0
                pygame.draw.line(beam_surf, (NEON_BLUE[0], NEON_BLUE[1], NEON_BLUE[2], alpha), 
                                (0, j), (20, j), 1)
            img.blit(beam_surf, (15, height))
            
            self.images.append(img)
            
        self.image = self.images[0]
        self.index = 0
        
        # Random height for the drone
        height_options = [GROUND_HEIGHT - 50, GROUND_HEIGHT - 100, GROUND_HEIGHT - 150]
        self.height = random.choice(height_options)
        
        super().__init__(self.image, self.type)
        self.rect.y = self.height
        
    def update(self):
        # Drone animation
        if self.index >= 10:
            self.image = self.images[self.index // 5 % 2]
            self.index = 0
        self.index += 1
        
        super().update()

class HologramCloud:
    def __init__(self):
        self.width = random.randint(60, 120)
        self.height = random.randint(30, 50)
        self.x = SCREEN_WIDTH
        self.y = random.randint(50, 200)
        self.speed = random.randint(1, 3)
        
        # Create a holographic cloud image
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw holographic effect
        for i in range(3):  # Draw multiple shapes for cloud puffs
            radius = self.height // 2
            center_x = self.width // 4 + (i * self.width // 4)
            center_y = self.height // 2
            
            # Draw with scanlines effect
            for j in range(0, radius*2, 2):
                alpha = 100 - (j * 2)
                if alpha < 0:
                    alpha = 0
                pygame.draw.circle(self.image, (NEON_BLUE[0], NEON_BLUE[1], NEON_BLUE[2], alpha), 
                                  (center_x, center_y), radius - j//2, 1)
        
        # Add some random "data" points
        for _ in range(5):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(1, 3)
            pygame.draw.circle(self.image, CYBER_YELLOW, (x, y), size)
        
        # Pulse effect variables
        self.pulse_counter = random.randint(0, 20)
        self.original_image = self.image.copy()
        
    def update(self):
        self.x -= self.speed
        if self.x < -self.width:
            clouds.remove(self)
            
        # Pulsing effect
        self.pulse_counter += 1
        if self.pulse_counter > 20:
            self.pulse_counter = 0
            
        pulse_intensity = abs(10 - self.pulse_counter) / 10
        self.image = self.original_image.copy()
        
        # Adjust transparency based on pulse
        for x in range(self.width):
            for y in range(self.height):
                color = self.image.get_at((x, y))
                if color.a > 0:
                    new_alpha = int(color.a * (0.7 + 0.3 * pulse_intensity))
                    self.image.set_at((x, y), (color.r, color.g, color.b, new_alpha))
            
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

# Neon colors with alpha for glow effects
NEON_RED = (255, 0, 60)
NEON_BLUE_ALPHA = (0, 195, 255, 100)

def main():
    global game_speed, score, obstacles, clouds, high_score
    
    # Create game objects
    dino = TRex()
    obstacles = []
    clouds = []
    
    # Game loop
    run = True
    game_over = False
    obstacle_timer = 0
    cloud_timer = 0
    point_milestone = 100  # For playing point sound every 100 points
    
    # Ground effect variables
    ground_scroll = 0
    ground_speed = 5
    
    def reset_game():
        nonlocal game_over, obstacle_timer, cloud_timer, point_milestone
        global game_speed, score, obstacles, clouds
        
        game_over = False
        obstacle_timer = 0
        cloud_timer = 0
        point_milestone = 100
        game_speed = 10
        score = 0
        obstacles = []
        clouds = []
        dino.rect.y = dino.y
        dino.is_jumping = False
        dino.is_ducking = False
        dino.vel_y = dino.jump_vel
        dino.trail_positions = []
    
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game_over:
                    reset_game()
        
        # Get user input
        user_input = pygame.key.get_pressed()
        
        # Draw background
        screen.blit(background, (0, 0))
        
        # Update and draw stars (twinkling effect)
        for star in stars:
            # Twinkle effect
            brightness = random.randint(150, 255)
            color = (brightness, brightness, brightness)
            pygame.draw.circle(screen, color, (star[0], star[1]), star[2])
            
            # Move stars for parallax effect
            star[0] -= star[2] // 2
            if star[0] < 0:
                star[0] = SCREEN_WIDTH
                star[1] = random.randint(0, GROUND_HEIGHT - 50)
        
        if not game_over:
            # Update game speed and score
            if score % 100 == 0 and score > 0:
                game_speed += 0.1
                
            score += 1
            
            # Play point sound every 100 points
            if score >= point_milestone:
                if point_sound:
                    point_sound.play()
                point_milestone += 100
                
            if score > high_score:
                high_score = score
            
            # Generate obstacles
            obstacle_timer += 1
            if obstacle_timer >= random.randint(50, 150):
                if random.randint(0, 2) == 0:  # 1/3 chance for drone
                    obstacles.append(CyberDrone())
                else:  # 2/3 chance for cyber cactus
                    obstacles.append(CyberCactus())
                obstacle_timer = 0
                
            # Generate clouds
            cloud_timer += 1
            if cloud_timer >= random.randint(75, 150):
                clouds.append(HologramCloud())
                cloud_timer = 0
            
            # Update and draw clouds
            for cloud in list(clouds):
                cloud.update()
                cloud.draw(screen)
            
            # Draw futuristic ground
            ground_scroll = (ground_scroll - ground_speed) % 40
            for x in range(-40 + ground_scroll, SCREEN_WIDTH, 40):
                pygame.draw.rect(screen, NEON_BLUE, (x, GROUND_HEIGHT, 20, 2))
                pygame.draw.rect(screen, NEON_PINK, (x + 20, GROUND_HEIGHT, 20, 2))
            
            # Draw grid on ground
            for x in range(0, SCREEN_WIDTH, 40):
                pygame.draw.line(screen, (NEON_BLUE[0], NEON_BLUE[1], NEON_BLUE[2], 30), 
                                (x, GROUND_HEIGHT), (x, SCREEN_HEIGHT), 1)
            
            # Update and draw dino
            dino.update(user_input)
            dino.draw(screen)
            
            # Update and draw obstacles
            for obstacle in list(obstacles):
                obstacle.update()
                obstacle.draw(screen)
                
                # Check for collision
                if dino.rect.colliderect(obstacle.rect):
                    # Play collision sound
                    if collision_sound:
                        collision_sound.play()
                    game_over = True
        else:
            # Game over screen
            game_over_surf = pygame.Surface((400, 100), pygame.SRCALPHA)
            game_over_surf.fill((0, 0, 0, 150))
            screen.blit(game_over_surf, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 50))
            
            game_over_text = title_font.render("SYSTEM FAILURE", True, NEON_RED)
            restart_text = font.render("Press SPACE to reboot", True, NEON_BLUE)
            
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 
                                        SCREEN_HEIGHT // 2 - 30))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 
                                      SCREEN_HEIGHT // 2 + 10))
        
        # Draw score in futuristic style
        score_text = font.render(f"SCORE: {score}", True, NEON_GREEN)
        high_score_text = font.render(f"HI-SCORE: {high_score}", True, CYBER_YELLOW)
        
        # Score background
        score_bg = pygame.Surface((150, 50), pygame.SRCALPHA)
        score_bg.fill((0, 0, 0, 100))
        screen.blit(score_bg, (10, 10))
        
        # Draw score with glow effect
        screen.blit(score_text, (20, 15))
        screen.blit(high_score_text, (20, 35))
        
        # Update display
        pygame.display.update()
        clock.tick(30)

if __name__ == "__main__":
    main()

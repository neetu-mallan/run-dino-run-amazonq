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
DINO_GREEN = (50, 120, 50)  # T-Rex color

# Game variables
score = 0
game_speed = 10
high_score = 0

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pixelated T-Rex Runner")
clock = pygame.time.Clock()

# Load font
font = pygame.font.SysFont("Arial", 20)

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

# Helper function to draw pixelated shapes
def draw_pixel_rect(surface, color, rect, pixel_size=2):
    """Draw a pixelated rectangle"""
    for x in range(rect[0], rect[0] + rect[2], pixel_size):
        for y in range(rect[1], rect[1] + rect[3], pixel_size):
            pygame.draw.rect(surface, color, (x, y, pixel_size, pixel_size))

def draw_pixel_circle(surface, color, center, radius, pixel_size=2):
    """Draw a pixelated circle"""
    x0, y0 = center
    for x in range(x0 - radius, x0 + radius + 1, pixel_size):
        for y in range(y0 - radius, y0 + radius + 1, pixel_size):
            if (x - x0)**2 + (y - y0)**2 <= radius**2:
                pygame.draw.rect(surface, color, (x, y, pixel_size, pixel_size))

class TRex:
    def __init__(self):
        # Create a pixelated T-Rex shape
        self.width = 50
        self.height = 60
        self.x = 80
        self.y = GROUND_HEIGHT - self.height
        self.jump_vel = 8.5
        self.is_jumping = False
        self.is_ducking = False
        self.vel_y = 0
        self.step_index = 0
        self.pixel_size = 2  # Size of each "pixel" for the pixelated look
        
        # Create pixelated T-Rex images for animation
        self.run_imgs = []
        for i in range(2):
            img = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            
            # T-Rex body (main body block)
            draw_pixel_rect(img, DINO_GREEN, (5, 10, 30, 30), self.pixel_size)
            
            # T-Rex head (larger for T-Rex)
            draw_pixel_rect(img, DINO_GREEN, (25, 0, 20, 20), self.pixel_size)
            
            # T-Rex tail
            draw_pixel_rect(img, DINO_GREEN, (0, 15, 15, 10), self.pixel_size)
            
            # T-Rex arms (tiny arms)
            draw_pixel_rect(img, DINO_GREEN, (25, 25, 8, 5), self.pixel_size)
            
            # T-Rex legs
            leg_height = 20 if i == 0 else 15
            leg_offset = 0 if i == 0 else 5
            # Back leg
            draw_pixel_rect(img, DINO_GREEN, (10, self.height - leg_height, 8, leg_height), self.pixel_size)
            # Front leg
            draw_pixel_rect(img, DINO_GREEN, (30, self.height - leg_height - leg_offset, 8, leg_height + leg_offset), self.pixel_size)
            
            # T-Rex eye
            draw_pixel_rect(img, WHITE, (35, 5, 4, 4), self.pixel_size)
            draw_pixel_rect(img, BLACK, (36, 6, 2, 2), self.pixel_size)
            
            # T-Rex teeth (pixelated)
            draw_pixel_rect(img, WHITE, (40, 15, 2, 2), self.pixel_size)
            draw_pixel_rect(img, WHITE, (43, 15, 2, 2), self.pixel_size)
            
            self.run_imgs.append(img)
            
        # Jump image
        self.jump_img = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        # Copy the first run image but adjust the legs
        self.jump_img.blit(self.run_imgs[0], (0, 0))
        # Clear the leg area
        pygame.draw.rect(self.jump_img, (0, 0, 0, 0), (5, self.height-25, 40, 25))
        # Draw tucked legs
        draw_pixel_rect(self.jump_img, DINO_GREEN, (10, self.height - 10, 25, 10), self.pixel_size)
        
        # Duck image (shorter and longer)
        self.duck_img = pygame.Surface((self.width + 10, self.height - 20), pygame.SRCALPHA)
        # Stretched body
        draw_pixel_rect(self.duck_img, DINO_GREEN, (0, 10, 40, 20), self.pixel_size)
        # Head
        draw_pixel_rect(self.duck_img, DINO_GREEN, (30, 0, 20, 15), self.pixel_size)
        # Eye
        draw_pixel_rect(self.duck_img, WHITE, (40, 5, 4, 4), self.pixel_size)
        draw_pixel_rect(self.duck_img, BLACK, (41, 6, 2, 2), self.pixel_size)
        # Legs
        draw_pixel_rect(self.duck_img, DINO_GREEN, (10, self.height - 30, 8, 10), self.pixel_size)
        draw_pixel_rect(self.duck_img, DINO_GREEN, (25, self.height - 30, 8, 10), self.pixel_size)
        
        self.image = self.run_imgs[0]
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        
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
        screen.blit(self.image, self.rect)

class Obstacle:
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

class Cactus(Obstacle):
    def __init__(self, image=None):
        self.type = random.randint(0, 2)
        self.pixel_size = 2  # Size of each "pixel" for pixelated look
        
        # Create pixelated cactus images
        if self.type == 0:
            # Small cactus
            width, height = 20, 40
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            # Main stem
            draw_pixel_rect(self.image, (30, 100, 30), (8, 0, 8, height), self.pixel_size)
            # Arms
            draw_pixel_rect(self.image, (30, 100, 30), (0, 15, 8, 5), self.pixel_size)
            draw_pixel_rect(self.image, (30, 100, 30), (16, 25, 8, 5), self.pixel_size)
        elif self.type == 1:
            # Medium cactus
            width, height = 30, 60
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            # Main stem
            draw_pixel_rect(self.image, (30, 100, 30), (12, 0, 10, height), self.pixel_size)
            # Arms
            draw_pixel_rect(self.image, (30, 100, 30), (0, 20, 12, 6), self.pixel_size)
            draw_pixel_rect(self.image, (30, 100, 30), (22, 35, 12, 6), self.pixel_size)
        else:
            # Large cactus
            width, height = 40, 80
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            # Main stem
            draw_pixel_rect(self.image, (30, 100, 30), (15, 0, 12, height), self.pixel_size)
            # Arms
            draw_pixel_rect(self.image, (30, 100, 30), (0, 25, 15, 8), self.pixel_size)
            draw_pixel_rect(self.image, (30, 100, 30), (27, 40, 15, 8), self.pixel_size)
            draw_pixel_rect(self.image, (30, 100, 30), (5, 50, 10, 6), self.pixel_size)
            
        super().__init__(self.image, self.type)
        self.rect.y = GROUND_HEIGHT - height

class Bird(Obstacle):
    def __init__(self):
        self.type = 0
        self.pixel_size = 2  # Size of each "pixel" for pixelated look
        
        # Create pixelated bird images for animation
        self.images = []
        for i in range(2):
            # Bird with wings up or down
            width, height = 40, 30
            img = pygame.Surface((width, height), pygame.SRCALPHA)
            
            # Bird body
            draw_pixel_rect(img, (100, 100, 100), (10, 10, 20, 15), self.pixel_size)
            
            # Bird head
            draw_pixel_rect(img, (80, 80, 80), (25, 5, 10, 10), self.pixel_size)
            
            # Bird beak
            draw_pixel_rect(img, (200, 150, 0), (35, 8, 5, 4), self.pixel_size)
            
            # Bird eye
            draw_pixel_rect(img, BLACK, (30, 7, 2, 2), self.pixel_size)
            
            # Bird wings
            if i == 0:
                # Wings up
                draw_pixel_rect(img, (120, 120, 120), (15, 0, 15, 5), self.pixel_size)
            else:
                # Wings down
                draw_pixel_rect(img, (120, 120, 120), (15, 20, 15, 5), self.pixel_size)
            
            # Bird tail
            draw_pixel_rect(img, (100, 100, 100), (0, 12, 10, 6), self.pixel_size)
            
            self.images.append(img)
            
        self.image = self.images[0]
        self.index = 0
        
        # Random height for the bird
        height_options = [GROUND_HEIGHT - 50, GROUND_HEIGHT - 100, GROUND_HEIGHT - 150]
        self.height = random.choice(height_options)
        
        super().__init__(self.image, self.type)
        self.rect.y = self.height
        
    def update(self):
        # Bird animation
        if self.index >= 10:
            self.image = self.images[self.index // 5 % 2]
            self.index = 0
        self.index += 1
        
        super().update()

class Cloud:
    def __init__(self):
        self.width = random.randint(60, 120)
        self.height = random.randint(30, 50)
        self.x = SCREEN_WIDTH
        self.y = random.randint(50, 200)
        self.speed = random.randint(1, 3)
        self.pixel_size = 3  # Size of each "pixel" for pixelated look
        
        # Create a pixelated cloud image
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw cloud in a pixelated style
        cloud_points = [
            (self.width // 4, self.height // 2),
            (self.width // 2, self.height // 3),
            (3 * self.width // 4, self.height // 2)
        ]
        
        for center_x, center_y in cloud_points:
            radius = random.randint(self.height // 3, self.height // 2)
            draw_pixel_circle(self.image, WHITE, (center_x, center_y), radius, self.pixel_size)
        
    def update(self):
        self.x -= self.speed
        if self.x < -self.width:
            clouds.remove(self)
            
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

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
        screen.fill(WHITE)
        
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
                if random.randint(0, 2) == 0:  # 1/3 chance for bird
                    obstacles.append(Bird())
                else:  # 2/3 chance for cactus
                    obstacles.append(Cactus())
                obstacle_timer = 0
                
            # Generate clouds
            cloud_timer += 1
            if cloud_timer >= random.randint(75, 150):
                clouds.append(Cloud())
                cloud_timer = 0
            
            # Update and draw clouds
            for cloud in list(clouds):
                cloud.update()
                cloud.draw(screen)
            
            # Draw pixelated ground
            for x in range(0, SCREEN_WIDTH, 4):  # 4-pixel blocks for ground
                height = 2 if x % 8 == 0 else 1  # Vary height for texture
                pygame.draw.rect(screen, BLACK, (x, GROUND_HEIGHT, 4, height))
            
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
            game_over_text = font.render("GAME OVER - Press SPACE to restart", True, BLACK)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 10))
        
        # Draw score in pixelated style
        score_text = font.render(f"Score: {score}", True, BLACK)
        high_score_text = font.render(f"High Score: {high_score}", True, BLACK)
        screen.blit(score_text, (10, 10))
        screen.blit(high_score_text, (10, 30))
        
        # Update display
        pygame.display.update()
        clock.tick(30)

if __name__ == "__main__":
    main()

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

# Space theme colors
SPACE_BG = (5, 5, 30)  # Dark blue/black for space
STAR_COLOR = (255, 255, 255)  # White stars
PLANET_COLORS = [
    (255, 100, 100),  # Red planet
    (100, 255, 100),  # Green planet
    (100, 100, 255),  # Blue planet
    (255, 255, 100),  # Yellow planet
    (255, 100, 255),  # Purple planet
]
GROUND_COLOR = (80, 80, 100)  # Alien ground color

# Game variables
score = 0
game_speed = 10
high_score = 0

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space T-Rex Runner")
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

# Create stars for space background
stars = []
for _ in range(100):  # More stars for space theme
    stars.append([
        random.randint(0, SCREEN_WIDTH),  # x position
        random.randint(0, GROUND_HEIGHT - 20),  # y position
        random.randint(1, 3),  # size
        random.random() * 0.5 + 0.5  # brightness (0.5 to 1.0)
    ])

# Create a few planets
planets = []
for _ in range(3):
    planets.append([
        random.randint(0, SCREEN_WIDTH),  # x position
        random.randint(50, GROUND_HEIGHT - 50),  # y position
        random.randint(15, 40),  # size
        random.choice(PLANET_COLORS),  # color
        random.randint(1, 3)  # speed (slower than game speed)
    ])

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

class SpaceRock(Obstacle):
    def __init__(self, image=None):
        self.type = random.randint(0, 2)
        self.pixel_size = 2  # Size of each "pixel" for pixelated look
        
        # Create pixelated asteroid/space rock images
        if self.type == 0:
            # Small asteroid
            width, height = 25, 25
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            # Main rock
            draw_pixel_circle(self.image, (150, 150, 150), (width//2, height//2), width//2 - 2, self.pixel_size)
            # Craters
            draw_pixel_circle(self.image, (100, 100, 100), (width//4, height//4), 3, self.pixel_size)
            draw_pixel_circle(self.image, (100, 100, 100), (3*width//4, 3*height//4), 2, self.pixel_size)
        elif self.type == 1:
            # Medium asteroid
            width, height = 40, 40
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            # Main rock (slightly irregular)
            draw_pixel_circle(self.image, (130, 130, 130), (width//2, height//2), width//2 - 4, self.pixel_size)
            draw_pixel_rect(self.image, (130, 130, 130), (width//4, height//4, width//2, height//2), self.pixel_size)
            # Craters
            draw_pixel_circle(self.image, (80, 80, 80), (width//3, height//3), 4, self.pixel_size)
            draw_pixel_circle(self.image, (80, 80, 80), (2*width//3, 2*height//3), 5, self.pixel_size)
            draw_pixel_circle(self.image, (80, 80, 80), (width//4, 2*height//3), 3, self.pixel_size)
        else:
            # Large asteroid
            width, height = 60, 60
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            # Main rock (irregular shape)
            draw_pixel_circle(self.image, (120, 120, 120), (width//2, height//2), width//2 - 5, self.pixel_size)
            draw_pixel_rect(self.image, (120, 120, 120), (width//5, height//5, 3*width//5, 3*height//5), self.pixel_size)
            # Craters
            for _ in range(5):
                x = random.randint(width//4, 3*width//4)
                y = random.randint(height//4, 3*height//4)
                size = random.randint(2, 6)
                draw_pixel_circle(self.image, (70, 70, 70), (x, y), size, self.pixel_size)
            
        super().__init__(self.image, self.type)
        self.rect.y = GROUND_HEIGHT - height

class AlienShip(Obstacle):
    def __init__(self):
        self.type = 0
        self.pixel_size = 2  # Size of each "pixel" for pixelated look
        
        # Create pixelated alien ship images for animation
        self.images = []
        for i in range(2):
            # Ship with different light patterns
            width, height = 50, 25
            img = pygame.Surface((width, height), pygame.SRCALPHA)
            
            # Ship body (saucer shape)
            draw_pixel_rect(img, (150, 150, 150), (10, 10, 30, 10), self.pixel_size)
            draw_pixel_circle(img, (150, 150, 150), (width//2, height//2), 15, self.pixel_size)
            
            # Cockpit dome
            draw_pixel_circle(img, (100, 200, 255), (width//2, height//2 - 5), 8, self.pixel_size)
            
            # Lights (alternating)
            light_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
            for j in range(3):
                if (i + j) % 2 == 0:
                    draw_pixel_circle(img, light_colors[j], (15 + j*10, height - 5), 2, self.pixel_size)
            
            # Bottom glow
            glow_color = (200, 200, 100) if i == 0 else (100, 200, 200)
            draw_pixel_rect(img, glow_color, (20, height - 3, 10, 3), self.pixel_size)
            
            self.images.append(img)
            
        self.image = self.images[0]
        self.index = 0
        
        # Random height for the ship
        height_options = [GROUND_HEIGHT - 50, GROUND_HEIGHT - 100, GROUND_HEIGHT - 150]
        self.height = random.choice(height_options)
        
        super().__init__(self.image, self.type)
        self.rect.y = self.height
        
    def update(self):
        # Ship animation
        if self.index >= 10:
            self.image = self.images[self.index // 5 % 2]
            self.index = 0
        self.index += 1
        
        super().update()

class SpaceCloud:
    def __init__(self):
        self.width = random.randint(60, 120)
        self.height = random.randint(30, 50)
        self.x = SCREEN_WIDTH
        self.y = random.randint(50, 200)
        self.speed = random.randint(1, 3)
        self.pixel_size = 3  # Size of each "pixel" for pixelated look
        
        # Create a pixelated nebula/gas cloud
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Choose a random nebula color
        nebula_colors = [
            (255, 100, 100, 50),  # Red nebula
            (100, 100, 255, 50),  # Blue nebula
            (255, 100, 255, 50),  # Purple nebula
            (100, 255, 100, 50),  # Green nebula
        ]
        nebula_color = random.choice(nebula_colors)
        
        # Draw nebula in a pixelated style
        cloud_points = [
            (self.width // 4, self.height // 2),
            (self.width // 2, self.height // 3),
            (3 * self.width // 4, self.height // 2)
        ]
        
        for center_x, center_y in cloud_points:
            radius = random.randint(self.height // 3, self.height // 2)
            for x in range(center_x - radius, center_x + radius, self.pixel_size):
                for y in range(center_y - radius, center_y + radius, self.pixel_size):
                    if (x - center_x)**2 + (y - center_y)**2 <= radius**2:
                        # Add some randomness to the nebula
                        if random.random() > 0.3:  # 70% chance to draw a pixel
                            alpha = random.randint(20, nebula_color[3])
                            color = (nebula_color[0], nebula_color[1], nebula_color[2], alpha)
                            pygame.draw.rect(self.image, color, 
                                            (x - center_x + radius, y - center_y + radius, 
                                             self.pixel_size, self.pixel_size))
        
        # Add some stars inside the nebula
        for _ in range(5):
            x = random.randint(0, self.width - self.pixel_size)
            y = random.randint(0, self.height - self.pixel_size)
            pygame.draw.rect(self.image, WHITE, (x, y, self.pixel_size, self.pixel_size))
        
    def update(self):
        self.x -= self.speed
        if self.x < -self.width:
            clouds.remove(self)
            
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

def main():
    global game_speed, score, obstacles, clouds, high_score, stars, planets
    
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
        
        # Draw space background
        screen.fill(SPACE_BG)
        
        # Draw stars with twinkling effect
        for star in stars:
            # Twinkle effect - vary brightness
            brightness = int(255 * (star[3] + random.random() * 0.2))
            if brightness > 255:
                brightness = 255
            color = (brightness, brightness, brightness)
            pygame.draw.rect(screen, color, (star[0], star[1], star[2], star[2]))
            
            # Move stars for parallax effect
            star[0] -= star[2] // 2  # Smaller stars move slower
            if star[0] < 0:
                star[0] = SCREEN_WIDTH
                star[1] = random.randint(0, GROUND_HEIGHT - 20)
                star[3] = random.random() * 0.5 + 0.5  # New brightness
        
        # Draw planets
        for planet in planets:
            # Draw the planet
            draw_pixel_circle(screen, planet[3], (planet[0], planet[1]), planet[2], 3)
            
            # Move planets (slower than game objects)
            planet[0] -= planet[4]
            if planet[0] < -planet[2]:
                planet[0] = SCREEN_WIDTH + random.randint(50, 200)
                planet[1] = random.randint(50, GROUND_HEIGHT - 50)
                planet[2] = random.randint(15, 40)
                planet[3] = random.choice(PLANET_COLORS)
                planet[4] = random.randint(1, 3)
        
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
                if random.randint(0, 2) == 0:  # 1/3 chance for alien ship
                    obstacles.append(AlienShip())
                else:  # 2/3 chance for space rock
                    obstacles.append(SpaceRock())
                obstacle_timer = 0
                
            # Generate space clouds/nebulae
            cloud_timer += 1
            if cloud_timer >= random.randint(75, 150):
                clouds.append(SpaceCloud())
                cloud_timer = 0
            
            # Update and draw clouds
            for cloud in list(clouds):
                cloud.update()
                cloud.draw(screen)
            
            # Draw space ground (alien surface)
            for x in range(0, SCREEN_WIDTH, 4):  # 4-pixel blocks for ground
                height = 2 if x % 8 == 0 else 1  # Vary height for texture
                color = (
                    GROUND_COLOR[0] + random.randint(-10, 10),
                    GROUND_COLOR[1] + random.randint(-10, 10),
                    GROUND_COLOR[2] + random.randint(-10, 10)
                )
                pygame.draw.rect(screen, color, (x, GROUND_HEIGHT, 4, height))
            
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
            
            game_over_text = font.render("GAME OVER - Press SPACE to restart", True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 10))
        
        # Draw score in space theme style
        score_text = font.render(f"Score: {score}", True, WHITE)
        high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(high_score_text, (10, 30))
        
        # Update display
        pygame.display.update()
        clock.tick(30)

if __name__ == "__main__":
    main()

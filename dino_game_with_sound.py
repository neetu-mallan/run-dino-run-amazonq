#!/usr/bin/env python3
import pygame
import random
import sys
import os

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

# Game variables
score = 0
game_speed = 10
high_score = 0

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dino Runner")
clock = pygame.time.Clock()

# Load font
font = pygame.font.SysFont("Arial", 20)

# Create sound effects
jump_sound = pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), "jump.wav"))
collision_sound = pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), "collision.wav"))
point_sound = pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), "point.wav"))

# Create the sound files if they don't exist
def create_sound_files():
    # Create a simple jump sound (beep)
    if not os.path.exists(os.path.join(os.path.dirname(__file__), "jump.wav")):
        pygame.mixer.Sound.play(pygame.mixer.Sound(buffer=bytes([128] * 4000)))
        pygame.mixer.Sound.stop(pygame.mixer.Sound(buffer=bytes([128] * 4000)))
        
        # Create a simple jump sound
        sample_rate = 44100
        duration = 0.2  # seconds
        frequency = 800  # Hz
        
        # Generate a simple sine wave
        buf = []
        for i in range(int(duration * sample_rate)):
            t = i / sample_rate
            value = int(127 * (0.5 + 0.5 * pygame.math.sin(2 * 3.14159 * frequency * t)))
            buf.append(value)
        
        # Save the sound
        pygame.mixer.Sound(buffer=bytes(buf)).save(os.path.join(os.path.dirname(__file__), "jump.wav"))
    
    # Create a simple collision sound (lower tone)
    if not os.path.exists(os.path.join(os.path.dirname(__file__), "collision.wav")):
        # Create a simple collision sound
        sample_rate = 44100
        duration = 0.3  # seconds
        frequency = 200  # Hz
        
        # Generate a simple sine wave with decay
        buf = []
        for i in range(int(duration * sample_rate)):
            t = i / sample_rate
            decay = 1 - (t / duration)
            value = int(127 * decay * (0.5 + 0.5 * pygame.math.sin(2 * 3.14159 * frequency * t)))
            buf.append(value)
        
        # Save the sound
        pygame.mixer.Sound(buffer=bytes(buf)).save(os.path.join(os.path.dirname(__file__), "collision.wav"))
    
    # Create a simple point sound (high beep)
    if not os.path.exists(os.path.join(os.path.dirname(__file__), "point.wav")):
        # Create a simple point sound
        sample_rate = 44100
        duration = 0.1  # seconds
        frequency = 1200  # Hz
        
        # Generate a simple sine wave
        buf = []
        for i in range(int(duration * sample_rate)):
            t = i / sample_rate
            value = int(127 * (0.5 + 0.5 * pygame.math.sin(2 * 3.14159 * frequency * t)))
            buf.append(value)
        
        # Save the sound
        pygame.mixer.Sound(buffer=bytes(buf)).save(os.path.join(os.path.dirname(__file__), "point.wav"))

# Try to create sound files
try:
    create_sound_files()
except:
    print("Could not create sound files. Game will run without sound.")

# Load sound files
try:
    jump_sound = pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), "jump.wav"))
    collision_sound = pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), "collision.wav"))
    point_sound = pygame.mixer.Sound(os.path.join(os.path.dirname(__file__), "point.wav"))
except:
    print("Could not load sound files. Game will run without sound.")
    jump_sound = None
    collision_sound = None
    point_sound = None

class Dino:
    def __init__(self):
        # Create a simple dinosaur shape
        self.width = 44
        self.height = 48
        self.x = 80
        self.y = GROUND_HEIGHT - self.height
        self.jump_vel = 8.5
        self.is_jumping = False
        self.is_ducking = False
        self.vel_y = 0
        self.step_index = 0
        self.color = (50, 50, 50)  # Dark gray for dino
        
        # Create simple dino images for animation
        self.run_imgs = []
        for i in range(2):
            img = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(img, self.color, (0, 0, self.width, self.height))
            # Add leg detail
            leg_height = 10 if i == 0 else 15
            pygame.draw.rect(img, BLACK, (self.width-15, self.height-leg_height, 10, leg_height))
            self.run_imgs.append(img)
            
        # Jump image
        self.jump_img = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(self.jump_img, self.color, (0, 0, self.width, self.height))
        pygame.draw.rect(self.jump_img, BLACK, (self.width-15, self.height-5, 10, 5))
        
        # Duck image (shorter and longer)
        self.duck_img = pygame.Surface((self.width+10, self.height-20), pygame.SRCALPHA)
        pygame.draw.rect(self.duck_img, self.color, (0, 0, self.width+10, self.height-20))
        
        # Add eye
        for img in self.run_imgs + [self.jump_img, self.duck_img]:
            pygame.draw.circle(img, WHITE, (self.width-10, 15), 5)
            pygame.draw.circle(img, BLACK, (self.width-10, 15), 2)
        
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
            obstacles.pop()
            
    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Cactus(Obstacle):
    def __init__(self, image=None):
        self.type = random.randint(0, 2)
        
        # Create simple cactus images
        if self.type == 0:
            # Small cactus
            width, height = 20, 40
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (30, 100, 30), (0, 0, width, height))
        elif self.type == 1:
            # Medium cactus
            width, height = 30, 60
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (30, 100, 30), (0, 0, width, height))
        else:
            # Large cactus
            width, height = 40, 80
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (30, 100, 30), (0, 0, width, height))
            
        # Add some cactus details
        if self.type > 0:  # Medium and large cacti have arms
            arm_width = width // 2
            pygame.draw.rect(self.image, (30, 100, 30), (width-5, height//3, arm_width, 10))
            
        super().__init__(self.image, self.type)
        self.rect.y = GROUND_HEIGHT - height

class Bird(Obstacle):
    def __init__(self):
        self.type = 0
        
        # Create simple bird images for animation
        self.images = []
        for i in range(2):
            # Bird with wings up or down
            width, height = 40, 30
            img = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.ellipse(img, (100, 100, 100), (0, 0, width-10, height))  # Body
            
            # Wings
            if i == 0:
                pygame.draw.ellipse(img, (80, 80, 80), (width-20, 0, 20, 20))  # Wings up
            else:
                pygame.draw.ellipse(img, (80, 80, 80), (width-20, height-20, 20, 20))  # Wings down
                
            # Beak
            pygame.draw.polygon(img, (200, 150, 0), [(0, height//2), (10, height//2-5), (10, height//2+5)])
            
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
        
        # Create a simple cloud image
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for i in range(3):  # Draw multiple circles for cloud puffs
            radius = self.height // 2
            center_x = self.width // 4 + (i * self.width // 4)
            center_y = self.height // 2
            pygame.draw.circle(self.image, WHITE, (center_x, center_y), radius)
        
    def update(self):
        self.x -= self.speed
        if self.x < -self.width:
            clouds.remove(self)
            
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

def main():
    global game_speed, score, obstacles, clouds, high_score
    
    # Create game objects
    dino = Dino()
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
            
            # Draw ground
            pygame.draw.line(screen, BLACK, (0, GROUND_HEIGHT), (SCREEN_WIDTH, GROUND_HEIGHT), 1)
            
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
        
        # Draw score
        score_text = font.render(f"Score: {score}", True, BLACK)
        high_score_text = font.render(f"High Score: {high_score}", True, BLACK)
        screen.blit(score_text, (10, 10))
        screen.blit(high_score_text, (10, 30))
        
        # Update display
        pygame.display.update()
        clock.tick(30)

if __name__ == "__main__":
    main()

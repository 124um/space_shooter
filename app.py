import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Tile size
tile_width, tile_height = 40, 40  # Size of each map tile

# Load images and scale to tile size
spaceship_image = pygame.image.load('./resources/ships/ship.png')
spaceship_image = pygame.transform.scale(spaceship_image, (tile_width, tile_height))

stone_image = pygame.image.load('./resources/stone.webp')
stone_image = pygame.transform.scale(stone_image, (tile_width, tile_height))

asteroid_image = pygame.image.load('./resources/asteroid/a1.png')
asteroid_image = pygame.transform.scale(asteroid_image, (tile_width, tile_height))

powerup_image = pygame.image.load('./resources/power.png')
powerup_image = pygame.transform.scale(powerup_image, (tile_width, tile_height))

star_image = pygame.image.load('./resources/star.png')
star_image = pygame.transform.scale(star_image, (tile_width, tile_height))

# Load a sound file (make sure the path is correct)
laser_sound = pygame.mixer.Sound('./resources/retro-laser.mp3')  # Use your own sound file path
bg_sound = pygame.mixer.Sound('./resources/bg_music.mp3')  # Use your own sound file path

# Player ship settings
PLAYER_SPEED = 5

# Bullet settings
BULLET_WIDTH = 5
BULLET_HEIGHT = 10
BULLET_SPEED = 7

# Enemy settings
ENEMY_SPEED = 3

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Shooter")

def generate_random_size(image):
    w_rand_s = random.randint(1, 4)
    h_rand_s = random.randint(1, 4)
    return pygame.transform.scale(image, (tile_width * w_rand_s, tile_height * h_rand_s))

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = spaceship_image
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 2
        self.rect.y = SCREEN_HEIGHT - tile_height - 10

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED

        # Boundaries
        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.x > SCREEN_WIDTH - tile_width:
            self.rect.x = SCREEN_WIDTH - tile_width

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([BULLET_WIDTH, BULLET_HEIGHT])
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        laser_sound.play()

    def update(self):
        self.rect.y -= BULLET_SPEED
        if self.rect.y < 0:
            self.kill()

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_type):
        super().__init__()
        # Use different images based on the type
        if enemy_type == "asteroid":
            self.image = generate_random_size(asteroid_image)
        elif enemy_type == "stone":
            self.image = generate_random_size(stone_image)
        else:
            self.image = generate_random_size(asteroid_image)  # Default to asteroid
        self.enemy_type = enemy_type
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(50, 150)

    def update(self):
        self.rect.y += ENEMY_SPEED
        if self.rect.y > SCREEN_HEIGHT:
            self.kill()

# Star class
class Star(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = star_image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - tile_width)
        self.rect.y = random.randint(50, 150)

# Sprite groups
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
star_group = pygame.sprite.Group()

# Create player
player = Player()
all_sprites.add(player)

# Game variables
running = True
clock = pygame.time.Clock()
score = 0
game_over = False
game_won = False

# Main game loop
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over and not game_won:
                # Shoot a bullet
                bullet = Bullet(player.rect.centerx, player.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)

    if not game_over and not game_won:
        # Update sprites
        all_sprites.update()

        # Enemy and object spawning
        if random.randint(1, 50) == 1:
            enemy_type = random.choice(["asteroid", "stone"])
            enemy = Enemy(enemy_type)
            all_sprites.add(enemy)
            enemies.add(enemy)

        # Check for player collisions with enemies
        if pygame.sprite.spritecollideany(player, enemies):
            for enemy in enemies:
                if enemy.rect.colliderect(player.rect):
                    if enemy.enemy_type in ["asteroid", "stone"]:
                        game_over = True
                        print("Game Over! You collided with an enemy.")
                        break

        # Collision detection for bullets
        for bullet in bullets:
            hit_list = pygame.sprite.spritecollide(bullet, enemies, True)
            for hit in hit_list:
                if hit.enemy_type in ["asteroid", "stone"]:
                    score += 1  # Increment score for hitting asteroid or stone
                bullet.kill()  # Destroy the bullet after collision

        # Create a star if the score reaches 30
        if score == 30 and not star_group:
            star = Star()
            all_sprites.add(star)
            star_group.add(star)

        # Check if player collects the star
        if pygame.sprite.spritecollideany(player, star_group):
            game_won = True
            print("You Win!")

    # Drawing
    screen.fill(BLACK)
    all_sprites.draw(screen)

    # Display score
    font = pygame.font.SysFont(None, 36)
    text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(text, (10, 10))

    # Display game over message
    if game_over:
        font = pygame.font.SysFont(None, 72)
        game_over_text = font.render("you are a poop", True, WHITE)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50))

    # Display "You Win!" message
    if game_won:
        font = pygame.font.SysFont(None, 72)
        win_text = font.render("YOU WIN!", True, WHITE)
        screen.blit(win_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50))

    # Update display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()

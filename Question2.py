import pygame
import random

# Initialize Pygame
pygame.init()

# Game Window Settings
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Side-Scrolling Game with Levels and Boss Enemy")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Load Images for Human-like Characters
hero_image = pygame.image.load("hero.jpg")  # Replace with actual file path
enemy_image = pygame.image.load("enemy.jpg")  # Replace with actual file path
boss_image = pygame.image.load("boss.jpg")  # Replace with actual file path for the boss
collectible_image = pygame.Surface((20, 20))
collectible_image.fill(GREEN)

# Game Variables
clock = pygame.time.Clock()
player_speed = 5
enemy_speed = 3
projectile_speed = 10
gravity = 0.8
jump_height = 12
score = 0
level = 1
enemies_defeated = 0
game_over = False
boss_fight = False
won = False


# Camera Class to Follow the Player
class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(SCREEN_WIDTH / 2)
        y = -target.rect.centery + int(SCREEN_HEIGHT / 2)
        x = min(0, x)
        x = max(-(self.width - SCREEN_WIDTH), x)
        y = min(0, y)
        y = max(-(self.height - SCREEN_HEIGHT), y)
        self.camera = pygame.Rect(x, y, self.width, self.height)


# Player Class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(hero_image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = 100, SCREEN_HEIGHT - 150
        self.health = 100
        self.lives = 3
        self.jump = False
        self.vel_y = 0

    def update(self):
        if not game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and self.rect.x > 0:
                self.rect.x -= player_speed
            if keys[pygame.K_RIGHT] and self.rect.x < SCREEN_WIDTH - self.rect.width:
                self.rect.x += player_speed
            if keys[pygame.K_UP] and self.rect.y > 0:
                self.rect.y -= player_speed
            if keys[pygame.K_DOWN] and self.rect.y < SCREEN_HEIGHT - self.rect.height:
                self.rect.y += player_speed
            if keys[pygame.K_SPACE] and self.rect.bottom == SCREEN_HEIGHT - 50:
                self.vel_y = -jump_height
                self.jump = True

            if self.jump:
                self.vel_y += gravity
                self.rect.y += self.vel_y
                if self.rect.bottom >= SCREEN_HEIGHT - 50:
                    self.rect.bottom = SCREEN_HEIGHT - 50
                    self.jump = False

    def draw_health_bar(self):
        pygame.draw.rect(screen, RED, (self.rect.x, self.rect.y - 10, 50, 5))
        pygame.draw.rect(screen, GREEN, (self.rect.x, self.rect.y - 10, 50 * (self.health / 100), 5))


# Enemy Class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, is_boss=False):
        super().__init__()
        self.is_boss = is_boss
        self.image = pygame.transform.scale(boss_image if is_boss else enemy_image, (80, 80) if is_boss else (50, 50))
        self.rect = self.image.get_rect(center=(x, y))
        self.health = 300 if is_boss else 100

    def update(self):
        self.rect.x -= enemy_speed if not self.is_boss else enemy_speed / 2
        if self.rect.right < 0:
            self.kill()

    def draw_health_bar(self):
        width = 80 if self.is_boss else 50
        pygame.draw.rect(screen, RED, (self.rect.x, self.rect.y - 10, width, 5))
        pygame.draw.rect(screen, GREEN,
                         (self.rect.x, self.rect.y - 10, width * (self.health / (300 if self.is_boss else 100)), 5))


# Projectile Class
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((15, 5))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.x += projectile_speed
        if self.rect.x > SCREEN_WIDTH:
            self.kill()


# Collectible Class for Health and Extra Life
class Collectible(pygame.sprite.Sprite):
    def __init__(self, x, y, type_):
        super().__init__()
        self.image = collectible_image
        self.rect = self.image.get_rect(center=(x, y))
        self.type = type_

    def apply_effect(self, player):
        if self.type == 'health' and player.health < 100:
            player.health += 20
        elif self.type == 'life':
            player.lives += 1


# Initialize Player, Enemies, Projectiles, Collectibles, and Camera
player = Player()
player_group = pygame.sprite.GroupSingle(player)
enemy_group = pygame.sprite.Group()
projectile_group = pygame.sprite.Group()
collectible_group = pygame.sprite.Group()
camera = Camera(SCREEN_WIDTH * 2, SCREEN_HEIGHT)


# Spawn Enemies and Collectibles
def spawn_enemy():
    enemy = Enemy(SCREEN_WIDTH + random.randint(100, 500), random.randint(100, SCREEN_HEIGHT - 100))
    enemy_group.add(enemy)


def spawn_collectibles(num_collectibles):
    for i in range(num_collectibles):
        type_ = random.choice(['health', 'life'])
        collectible = Collectible(random.randint(100, SCREEN_WIDTH), random.randint(100, SCREEN_HEIGHT - 100), type_)
        collectible_group.add(collectible)


# Start Level
for _ in range(7):
    spawn_enemy()
spawn_collectibles(2)

# Game Loop
running = True
while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_f and not game_over:
            projectile = Projectile(player.rect.right, player.rect.centery)
            projectile_group.add(projectile)

    if not game_over and not won:
        player_group.update()
        enemy_group.update()
        projectile_group.update()
        collectible_group.update()
        camera.update(player)

        # Limit enemies to a maximum of 7
        if len(enemy_group) < 7:
            spawn_enemy()

        for entity in player_group:
            screen.blit(entity.image, camera.apply(entity))
            player.draw_health_bar()

        for entity in enemy_group:
            screen.blit(entity.image, camera.apply(entity))
            entity.draw_health_bar()

        for entity in collectible_group:
            screen.blit(entity.image, camera.apply(entity))

        projectile_hits = pygame.sprite.groupcollide(enemy_group, projectile_group, False, True)
        for enemy in projectile_hits:
            enemy.health -= 50
            if enemy.health <= 0:
                if enemy.is_boss:
                    won = True
                enemy.kill()
                score += 10
                enemies_defeated += 1

        if pygame.sprite.spritecollide(player, enemy_group, False):
            player.health -= 1
            if player.health <= 0:
                player.lives -= 1
                player.health = 100
                if player.lives <= 0:
                    game_over = True

        for collectible in pygame.sprite.spritecollide(player, collectible_group, True):
            collectible.apply_effect(player)

        # Level Management
        if enemies_defeated >= 10 * level and level < 3:
            level += 1
            enemies_defeated = 0
            if level == 3 and not boss_fight:
                boss_fight = True
                boss = Enemy(SCREEN_WIDTH + 300, SCREEN_HEIGHT // 2, is_boss=True)
                enemy_group.add(boss)
            spawn_collectibles(2)

    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Score: {score}  Lives: {player.lives}  Level: {level}", True, BLACK)
    screen.blit(score_text, (10, 10))

    if won:
        win_text = font.render("You WON! Press Esc to exit.", True, GREEN)
        screen.blit(win_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))

    if won:
        win_text = font.render("You WON! Press Esc to exit.", True, GREEN)
        screen.blit(win_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))
    elif game_over:
        game_over_text = font.render("Game Over! Press Esc to exit.", True, RED)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

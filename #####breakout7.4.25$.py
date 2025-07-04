import pygame
import sys
import math
from array import array

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=1)

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
PADDLE_WIDTH = 80
PADDLE_HEIGHT = 10
BALL_SIZE = 10
BRICK_WIDTH = 50
BRICK_HEIGHT = 20
BRICK_SPACING = 5
NUM_ROWS = 8
NUM_COLS = 10
LEFT_MARGIN = (SCREEN_WIDTH - (NUM_COLS * BRICK_WIDTH + (NUM_COLS - 1) * BRICK_SPACING)) // 2
TOP_MARGIN = 50

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Breakout")

def make_sound(freq, duration):
    sample_rate = 44100
    num_samples = int(sample_rate * duration)
    samples = array('h', [32767 if math.sin(2 * math.pi * freq * t / sample_rate) > 0 else -32768 for t in range(num_samples)])
    return pygame.mixer.Sound(samples)

paddle_hit_sound = make_sound(440, 0.1)
brick_hit_sound = make_sound(880, 0.1)
lose_life_sound = make_sound(220, 0.2)
win_sound = make_sound(660, 0.3)

paddle = pygame.Rect(SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2, SCREEN_HEIGHT - 30, PADDLE_WIDTH, PADDLE_HEIGHT)
ball = pygame.Rect(SCREEN_WIDTH // 2 - BALL_SIZE // 2, SCREEN_HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
ball_vx = 3
ball_vy = -3
bricks = [pygame.Rect(LEFT_MARGIN + col * (BRICK_WIDTH + BRICK_SPACING), TOP_MARGIN + row * (BRICK_HEIGHT + BRICK_SPACING), BRICK_WIDTH, BRICK_HEIGHT) for row in range(NUM_ROWS) for col in range(NUM_COLS)]
lives = 3
game_state = 'playing'

def reset_game():
    global paddle, ball, ball_vx, ball_vy, bricks, lives, game_state
    paddle.left = SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2
    ball.left = SCREEN_WIDTH // 2 - BALL_SIZE // 2
    ball.top = SCREEN_HEIGHT // 2 - BALL_SIZE // 2
    ball_vx = 3
    ball_vy = -3
    bricks = [pygame.Rect(LEFT_MARGIN + col * (BRICK_WIDTH + BRICK_SPACING), TOP_MARGIN + row * (BRICK_HEIGHT + BRICK_SPACING), BRICK_WIDTH, BRICK_HEIGHT) for row in range(NUM_ROWS) for col in range(NUM_COLS)]
    lives = 3
    game_state = 'playing'

clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if game_state in ['won', 'lost']:
                if event.key == pygame.K_r:
                    reset_game()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

    if game_state == 'playing':
        mouse_x = pygame.mouse.get_pos()[0]
        paddle.left = max(0, min(mouse_x - PADDLE_WIDTH // 2, SCREEN_WIDTH - PADDLE_WIDTH))

        ball.left += ball_vx
        ball.top += ball_vy

        if ball.left < 0 or ball.right > SCREEN_WIDTH:
            ball_vx = -ball_vx
            ball.left = max(0, min(ball.left, SCREEN_WIDTH - BALL_SIZE))
        if ball.top < 0:
            ball_vy = -ball_vy
            ball.top = max(0, ball.top)
        elif ball.bottom > SCREEN_HEIGHT:
            lives -= 1
            lose_life_sound.play()
            if lives > 0:
                ball.left = paddle.left + PADDLE_WIDTH // 2 - BALL_SIZE // 2
                ball.top = paddle.top - BALL_SIZE - 1
                ball_vy = -3
            else:
                game_state = 'lost'

        if ball.colliderect(paddle):
            ball_vy = -ball_vy
            ball.bottom = paddle.top
            paddle_hit_sound.play()

        for brick in bricks[:]:
            if ball.colliderect(brick):
                bricks.remove(brick)
                brick_hit_sound.play()
                dx = min(ball.right - brick.left, brick.right - ball.left)
                dy = min(ball.bottom - brick.top, brick.bottom - ball.top)
                if dx < dy:
                    ball_vx = -ball_vx
                else:
                    ball_vy = -ball_vy
                break

        if not bricks:
            game_state = 'won'
            win_sound.play()

    screen.fill(BLACK)
    if game_state == 'playing':
        pygame.draw.rect(screen, WHITE, paddle)
        pygame.draw.rect(screen, WHITE, ball)
        for brick in bricks:
            pygame.draw.rect(screen, RED, brick)
        font = pygame.font.Font(None, 36)
        lives_text = font.render(f"Lives: {lives}", True, WHITE)
        screen.blit(lives_text, (10, 10))
    else:
        font = pygame.font.Font(None, 72)
        if game_state == 'won':
            text = font.render("You Win!", True, WHITE)
        else:
            text = font.render("Game Over!", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
        font = pygame.font.Font(None, 36)
        instruction = font.render("Press R to restart or ESC to quit", True, WHITE)
        screen.blit(instruction, (SCREEN_WIDTH // 2 - instruction.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

    pygame.display.flip()
    clock.tick(60)

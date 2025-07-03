import pygame
import sys
import random
import numpy as np
from pygame import sndarray
import asyncio
import platform

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
speed = 5

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")
clock = pygame.time.Clock()

# Font setup
pygame.font.init()
font = pygame.font.Font(None, 36)

# Sound generation function
def make_beep(freq, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = 0.5 * np.sin(2 * np.pi * freq * t)
    sound_array = np.column_stack((wave * 32767, wave * 32767)).astype(np.int16)
    return sndarray.make_sound(sound_array)

# Sound effects
paddle_hit_sound = make_beep(440, 0.1)
wall_hit_sound = make_beep(220, 0.1)
score_sound = make_beep(330, 0.2)

# Game state variables
left_score = 0
right_score = 0
game_over = False
player_paddle = pygame.Rect(50, HEIGHT / 2 - 50, 20, 100)
ai_paddle = pygame.Rect(WIDTH - 50 - 20, HEIGHT / 2 - 50, 20, 100)
ball = pygame.Rect(WIDTH / 2 - 10, HEIGHT / 2 - 10, 20, 20)
ball_vx = -speed
ball_vy = 0
ai_vy = 0
winner = ""

def reset_game():
    global left_score, right_score, game_over, player_paddle, ai_paddle, ball, ball_vx, ball_vy, ai_vy, winner
    left_score = 0
    right_score = 0
    game_over = False
    player_paddle = pygame.Rect(50, HEIGHT / 2 - 50, 20, 100)
    ai_paddle = pygame.Rect(WIDTH - 50 - 20, HEIGHT / 2 - 50, 20, 100)
    ball = pygame.Rect(WIDTH / 2 - 10, HEIGHT / 2 - 10, 20, 20)
    ball_vx = -speed
    ball_vy = 0
    ai_vy = 0
    winner = ""

def setup():
    reset_game()

def update_loop():
    global left_score, right_score, game_over, ball_vx, ball_vy, ai_vy, winner

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if game_over:
                if event.key == pygame.K_y:
                    reset_game()
                elif event.key == pygame.K_n:
                    sys.exit()

    if not game_over:
        # Update player paddle with mouse
        mouse_x, mouse_y = pygame.mouse.get_pos()
        player_paddle.centery = mouse_y
        if player_paddle.top < 0:
            player_paddle.top = 0
        if player_paddle.bottom > HEIGHT:
            player_paddle.bottom = HEIGHT

        # Update AI paddle
        target_y = ball.centery
        if ai_paddle.centery < target_y - 10:
            ai_vy = 5
        elif ai_paddle.centery > target_y + 10:
            ai_vy = -5
        else:
            ai_vy = 0
        ai_paddle.y += ai_vy
        if ai_paddle.top < 0:
            ai_paddle.top = 0
        if ai_paddle.bottom > HEIGHT:
            ai_paddle.bottom = HEIGHT

        # Update ball
        ball.x += ball_vx
        ball.y += ball_vy

        # Wall collisions
        if ball.top < 0 or ball.bottom > HEIGHT:
            ball_vy = -ball_vy
            wall_hit_sound.play()

        # Paddle collisions
        if ball.colliderect(player_paddle):
            relative_hit = (ball.centery - player_paddle.centery) / (player_paddle.height / 2)
            ball_vy = relative_hit * speed
            ball_vx = speed
            paddle_hit_sound.play()
        elif ball.colliderect(ai_paddle):
            relative_hit = (ball.centery - ai_paddle.centery) / (ai_paddle.height / 2)
            ball_vy = relative_hit * speed
            ball_vx = -speed
            paddle_hit_sound.play()

        # Scoring
        if ball.right < 0:
            right_score += 1
            score_sound.play()
            ball.center = (WIDTH / 2, HEIGHT / 2)
            ball_vx = speed
            ball_vy = random.uniform(-speed, speed)
        elif ball.left > WIDTH:
            left_score += 1
            score_sound.play()
            ball.center = (WIDTH / 2, HEIGHT / 2)
            ball_vx = -speed
            ball_vy = random.uniform(-speed, speed)

        # Check game over
        if left_score >= 5 or right_score >= 5:
            game_over = True
            winner = "Left" if left_score >= 5 else "Right"

    # Draw
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, player_paddle)
    pygame.draw.rect(screen, WHITE, ai_paddle)
    pygame.draw.rect(screen, WHITE, ball)
    for y in range(0, HEIGHT, 20):
        pygame.draw.line(screen, WHITE, (WIDTH / 2, y), (WIDTH / 2, y + 10), 2)
    left_text = font.render(str(left_score), True, WHITE)
    screen.blit(left_text, (WIDTH / 4 - left_text.get_width() / 2, 50))
    right_text = font.render(str(right_score), True, WHITE)
    screen.blit(right_text, (3 * WIDTH / 4 - right_text.get_width() / 2, 50))

    if game_over:
        message = font.render(f"Game Over! {winner} player wins!", True, WHITE)
        screen.blit(message, (WIDTH / 2 - message.get_width() / 2, HEIGHT / 2 - 50))
        instruction = font.render("Press Y to restart, N to quit", True, WHITE)
        screen.blit(instruction, (WIDTH / 2 - instruction.get_width() / 2, HEIGHT / 2 + 50))

    pygame.display.flip()

async def main():
    setup()
    while True:
        update_loop()
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())

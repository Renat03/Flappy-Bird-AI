import pygame
import random

pygame.init()

WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")

bird_img = pygame.image.load('images/bird.png').convert_alpha()
pipe_img = pygame.image.load('images/pipe.png').convert_alpha()
bg_img = pygame.image.load('images/bg-image.png').convert()
bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))


BIRD_WIDTH, BIRD_HEIGHT = bird_img.get_width() // 10, bird_img.get_height() // 10
bird_img = pygame.transform.scale(bird_img, (BIRD_WIDTH, BIRD_HEIGHT))
bird_rect = bird_img.get_rect(center=(200, HEIGHT // 2))

PIPE_WIDTH, PIPE_HEIGHT = pipe_img.get_width() // 2, pipe_img.get_height() // 1.5
pipe_img = pygame.transform.scale(pipe_img, (PIPE_WIDTH, PIPE_HEIGHT))

pipe_height = [350, 400, 450, 500, 550]
pipe_list = []
PIPE_SPACING = 200
pipe_speed = 5

gravity = 0.5
bird_movement = 0
flap_strength = -10

clock = pygame.time.Clock()
running = True

def create_pipe():
    random_height = random.choice(pipe_height)
    bottom_pipe = pipe_img.get_rect(midtop=(WIDTH + 100, random_height))
    top_pipe = pipe_img.get_rect(midbottom=(WIDTH + 100, random_height - PIPE_SPACING))
    return bottom_pipe, top_pipe

def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= pipe_speed
    return pipes

def draw_pipes(pipes):
    for pipe in pipes:
        if pipe.bottom >= HEIGHT:
            screen.blit(pipe_img, pipe)
        else:
            flip_pipe = pygame.transform.rotate(pipe_img, 180)
            screen.blit(flip_pipe, pipe)

def check_collision(bird_rect, pipes):
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            return True
    return False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bird_movement = flap_strength

    bird_movement += gravity
    bird_rect.centery += bird_movement

    pipe_list = move_pipes(pipe_list)
    if len(pipe_list) == 0 or pipe_list[-1].centerx < WIDTH - 350:
        pipe_list.extend(create_pipe())

    screen.blit(bg_img, (0, 0))
    screen.blit(bird_img, bird_rect)
    draw_pipes(pipe_list)

    if check_collision(bird_rect, pipe_list):
        running = False

    pygame.display.update()
    clock.tick(60)

pygame.quit()

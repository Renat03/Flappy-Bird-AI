import pygame
import random
import neat
import os


class Bird:
    def __init__(self, img, x, y):
        self.image = img
        self.rect = img.get_rect(center=(x, y))
        self.movement = 0

    def update(self, gravity, flap_strength):
        if self.movement < 10:
            self.movement += gravity
        self.rect.centery += self.movement

    def flap(self, flap_strength):
        self.movement = flap_strength

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Pipe:
    def __init__(self, img, x, y, is_bottom):
        self.image = pygame.transform.rotate(img, 180) if not is_bottom else img
        self.rect = self.image.get_rect(midtop=(x, y)) if is_bottom else self.image.get_rect(midbottom=(x, y))
        self.scored = False

    def move(self, speed):
        self.rect.centerx -= speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)


pygame.init()
pygame.font.init()
score_font = pygame.font.SysFont('Pixelated', 70)

# Constants
WIDTH, HEIGHT = 1280, 720
GRAVITY = 0.5
FLAP_STRENGTH = -10
PIPE_SPEED = 5

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")

bird_img = pygame.image.load('images/bird.png').convert_alpha()
bird_img = pygame.transform.scale(bird_img, (bird_img.get_width() // 10, bird_img.get_height() // 10))
pipe_img = pygame.image.load('images/pipe.png').convert_alpha()
pipe_img = pygame.transform.scale(pipe_img, (pipe_img.get_width() // 2, pipe_img.get_height() // 1.5))
bg_img = pygame.image.load('images/bg-image.png').convert()
bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))

bird = Bird(bird_img, 200, HEIGHT // 2)
pipe_list = []
pipe_heights = [350, 400, 450, 500, 550]

score = 0
running = True
clock = pygame.time.Clock()

def create_pipe():
    height = random.randint(350, 550)
    bottom_pipe = Pipe(pipe_img, WIDTH + 100, height, True)
    top_pipe = Pipe(pipe_img, WIDTH + 100, height - 200, False)
    return bottom_pipe, top_pipe

def move_pipes(pipes):
    for pipe in pipes:
        pipe.move(PIPE_SPEED)
    return [pipe for pipe in pipes if pipe.rect.centerx > -50]

def draw_pipes(pipes):
    for pipe in pipes:
        pipe.draw(screen)

def check_collision(bird, pipes):
    for pipe in pipes:
        if bird.rect.colliderect(pipe.rect):
            return True
    return False

def eval_genomes(genomes, config):
    global screen, clock, bird_img, pipe_img, bg_img

    nets = []
    birds = []

    for genome_id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(bird_img, 200, HEIGHT // 2))

    pipe_list = []

    score = 0
    running = True
    while running and len(birds) > 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pipe_list = move_pipes(pipe_list)
        if not pipe_list or pipe_list[-1].rect.centerx < WIDTH - 350:
            pipe_list.extend(create_pipe())

        for i, bird in enumerate(birds):
            bird.update(GRAVITY, FLAP_STRENGTH)
            genome = genomes[i][1]
            genome.fitness += 0.1
            next_pipes = [pipe for pipe in pipe_list if not pipe.scored]
            output = nets[i].activate((bird.rect.centery, next_pipes[0].rect.top, next_pipes[0].rect.left, next_pipes[1].rect.bottom, next_pipes[1].rect.left))
            if output[0] > 0.5:
                bird.flap(FLAP_STRENGTH)

            if check_collision(bird, pipe_list) or bird.rect.top <= 0 or bird.rect.bottom >= HEIGHT:
                genome.fitness -= 1
                birds.pop(i)
                nets.pop(i)
                genomes.pop(i)

        for pipe in pipe_list:
            if pipe.rect.centerx < bird.rect.left and not pipe.scored:
                genome.fitness += 2
                score += 0.5
                pipe.scored = True

        screen.blit(bg_img, (0, 0))
        for bird in birds:
            bird.draw(screen)
        draw_pipes(pipe_list)
        score_surface = score_font.render(f'{int(score)}', True, (255, 255, 255))
        screen.blit(score_surface, (WIDTH // 2, 10))

        pygame.display.update()
        clock.tick(60)


def run_neat(config):
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(eval_genomes, 50)

if __name__ == "__main__":
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Flappy Bird AI")
    clock = pygame.time.Clock()

    bird_img = pygame.image.load('images/bird.png').convert_alpha()
    bird_img = pygame.transform.scale(bird_img, (bird_img.get_width() // 10, bird_img.get_height() // 10))
    pipe_img = pygame.image.load('images/pipe.png').convert_alpha()
    pipe_img = pygame.transform.scale(pipe_img, (pipe_img.get_width() // 2, pipe_img.get_height() // 1.5))
    bg_img = pygame.image.load('images/bg-image.png').convert()
    bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))

    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neat-config.txt')
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    run_neat(config)

pygame.quit()


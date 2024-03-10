import pygame
import random
import math
import argparse
import os
import configparser
import array as arr

# Constants
CONFIG_FILE = "corewar.cfg"
WIDTH, HEIGHT = 800, 800
SQUARE_SIZE = 25
DAY_COLOR = (51, 255, 255)
NIGHT_COLOR = (255, 153, 255)
DAY_BALL_COLOR = (200, 255, 255)
NIGHT_BALL_COLOR = (255, 0, 255)
DX = 14
DY = 14

class mem_struct:
    def __init__(self, A_value, B_value, opcode, A_mode, B_mode, debuginfo):
        self.A_value = A_value
        self.B_value = B_value
        self.opcode = opcode
        self.A_mode = A_mode
        self.B_mode = B_mode
        self.debuginfo = debuginfo

    def afficher_cell(self):
        print(f"A_value: {self.A_value}, B_value: {self.B_value}, opcode: {self.opcode}, A_mode: {self.A_mode}, B_mode: {self.B_mode}, debug: {self.debuginfo}")

class warrior_struct:
    def __init__(self, name, version, date, filename, authorname):
        self.pSpaceIDNumber = 0
        self.taskHead = 0
        self.taskTail = 0
        self.tasks = 0
        self.lastResult = 0
        self.pSpaceIndex = 0
        # load position in core
        self.position = 0
        # Length of instBank
        self.instLen = 0
        # Offset value specified by 'ORG' or 'END'
        self.offset = 0
        self.score = arr.array['i']
        self.name = name
        self.version = version
        self.date = date
        self.filename = filename
        self.authorname = authorname
        self.instBank = mem_struct(0, 0, 0, 0, 0, 0, "init")

def calculate_scores(squares):
    scores = {DAY_COLOR: 0, NIGHT_COLOR: 0}
    for row in squares:
        for color in row:
            if color in scores:
                scores[color] += 1
    return scores


def draw_score_panel(screen, scores, font):
    panel_height = 40
    panel_color = (50, 50, 50)  # Dark gray background for score panel

    # Draw the background panel at the bottom
    pygame.draw.rect(screen, panel_color, (0, HEIGHT - panel_height, WIDTH, panel_height))

    # Calculate the total width of the score texts for 2 players
    player_colors = [DAY_COLOR, NIGHT_COLOR]
    total_width = 0
    score_surfaces = []
    for color in player_colors:
        score_text = str(scores[color])
        score_surface = font.render(score_text, True, color)
        score_surfaces.append(score_surface)
        total_width += score_surface.get_width() + 30  # Include spacing

    # Start position for the first score text to center the block
    text_x = (WIDTH - total_width) // 2
    text_y = HEIGHT - panel_height + (panel_height - font.get_height()) // 2

    # Draw each score text
    for score_surface in score_surfaces:
        screen.blit(score_surface, (text_x, text_y))
        text_x += score_surface.get_width() + 30  # Adjust spacing between scores


def create_squares():
    squares = []
    for i in range(int(WIDTH / SQUARE_SIZE)):
        row = []
        for j in range(int(HEIGHT / SQUARE_SIZE)):
            color = DAY_COLOR if i < WIDTH / SQUARE_SIZE / 2 else NIGHT_COLOR
            row.append(color)
        squares.append(row)
    return squares


def draw_squares(squares, screen):
    for i in range(len(squares)):
        for j in range(len(squares[i])):
            color = squares[i][j]
            pygame.draw.rect(screen, color, (i * SQUARE_SIZE, j * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def draw_ball(x, y, color, screen):
    pygame.draw.circle(screen, color, (int(x), int(y)), SQUARE_SIZE // 2)


def update_square_and_bounce(x, y, dx, dy, color, squares):
    updated_dx, updated_dy = dx, dy
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        check_x = x + math.cos(rad) * (SQUARE_SIZE // 2)
        check_y = y + math.sin(rad) * (SQUARE_SIZE // 2)
        i, j = int(check_x // SQUARE_SIZE), int(check_y // SQUARE_SIZE)
        if 0 <= i < len(squares) and 0 <= j < len(squares[i]):
            if squares[i][j] != color:
                squares[i][j] = color
                if abs(math.cos(rad)) > abs(math.sin(rad)):
                    updated_dx = -updated_dx
                else:
                    updated_dy = -updated_dy
                updated_dx += random.uniform(-0.01, 0.01)
                updated_dy += random.uniform(-0.01, 0.01)
    return updated_dx, updated_dy


def check_boundary_collision(x, y, dx, dy):
    if x + dx > WIDTH - SQUARE_SIZE // 2 or x + dx < SQUARE_SIZE // 2:
        dx = -dx
    if y + dy > HEIGHT - SQUARE_SIZE // 2 or y + dy < SQUARE_SIZE // 2:
        dy = -dy
    return dx, dy



def main(args):
    if args.seed:
        random.seed(args.seed)
    if args.data_dir:
        for filename in os.listdir(args.data_dir):
            if os.path.isfile(os.path.join(args.data_dir, filename)):
                if filename == CONFIG_FILE:
                    # Créer un objet ConfigParser
                    config = configparser.ConfigParser()
                    config.read(os.path.join(args.data_dir, filename))
                    memory_size = config['Parametres']['MEMORY']
                    max_warrior = config['Parametres']['MAXWARRIOR']
                    print(f"Memory size : {memory_size}")
                    print(f"Max number of warrior : {max_warrior}")
                else:
                    with open(os.path.join(args.data_dir, filename), 'r') as file:
                        print(f"Contenu du fichier {filename}:")
                        content = file.read()
                        print(content)
                print("------------------------------")

    pygame.init()
    pygame.font.init()  # Initialize the font module

    font = pygame.font.SysFont('Consolas', 18)  # Or any other preferred font
    # Set up the display
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Core War")

    clock = pygame.time.Clock()
    squares = create_squares()
    x1, y1 = WIDTH / 4, HEIGHT / 2
    dx1, dy1 = DX, DY
    x2, y2 = WIDTH * 3 / 4, HEIGHT / 2
    dx2, dy2 = -DX, -DY

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        dx1, dy1 = update_square_and_bounce(x1, y1, dx1, dy1, DAY_COLOR, squares)
        dx2, dy2 = update_square_and_bounce(x2, y2, dx2, dy2, NIGHT_COLOR, squares)

        dx1, dy1 = check_boundary_collision(x1, y1, dx1, dy1)
        dx2, dy2 = check_boundary_collision(x2, y2, dx2, dy2)

        x1 += dx1
        y1 += dy1
        x2 += dx2
        y2 += dy2

        screen.fill((0, 0, 0))
        draw_squares(squares, screen)
        draw_ball(x1, y1, DAY_BALL_COLOR, screen)
        draw_ball(x2, y2, NIGHT_BALL_COLOR, screen)

        # Display scores
        scores = calculate_scores(squares)
        draw_score_panel(screen, scores, font)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--data_dir", help="Directory of warrior and config files", default=".")
    args.add_argument("--seed", type=int, help="Seed for random initial position of warriors", default=0)
    args = args.parse_args()
    main(args)

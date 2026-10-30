import pygame
import sys
import random
import os

# Global variables for the game
screen_width = 480
screen_height = 480
gridsize = 30
grid_width = screen_width // gridsize
grid_height = screen_height // gridsize
start_speed = 10        # moves per second at the start
max_speed = 20          # the snake speeds up by 1 for every speed_step points, up to this
speed_step = 3

up = (0, -1)
down = (0, 1)
left = (-1, 0)
right = (1, 0)

# Colours
white = (255, 255, 255)
yellow = (255, 255, 102)
red = (213, 50, 80)
blue = (50, 153, 213)
light_square = (93, 216, 228)
dark_square = (84, 194, 205)
snake_color = (17, 24, 47)
snake_head_color = (58, 74, 128)
food_color = (223, 163, 49)

# Score bar above the board
bar_height = 40
bar_color = (24, 32, 58)
bar_line_color = (58, 74, 128)
bar_label_color = (140, 156, 196)
bar_value_color = (220, 226, 240)

# The high score is kept in a file next to this script, so it survives restarts
high_score_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "highscore.txt")


def load_high_score():
    try:
        with open(high_score_file) as f:
            return int(f.read().strip() or 0)
    except (OSError, ValueError):
        return 0


def save_high_score(score):
    try:
        with open(high_score_file, "w") as f:
            f.write(str(score))
    except OSError:
        pass    # not being able to save the high score shouldn't stop the game


# original code: https://github.com/kiteco/python-youtube-code/blob/master/snake/snake.py
# Snake class to handle the snake's behavior
class Snake():
    def __init__(self):
        self.high_score = load_high_score()
        self.reset()

    def reset(self):
        self.length = 1
        # start in the middle cell (whole grid squares, so it lines up with the food)
        self.positions = [((grid_width // 2) * gridsize, (grid_height // 2) * gridsize)]
        self.direction = random.choice([up, down, left, right])
        self.last_moved = self.direction
        self.score = 0
        self.lost = False
        self.paused = False

    def get_head_position(self):
        return self.positions[0]

    def turn(self, point):
        # Compare with the direction the snake last moved in, not the last key pressed -
        # otherwise two quick presses (e.g. up then left while going right) turn it back into itself
        if self.length > 1 and (point[0] * -1, point[1] * -1) == self.last_moved:
            return
        self.direction = point

    def move(self):
        cur = self.get_head_position()
        x, y = self.direction
        new = (cur[0] + (x * gridsize), cur[1] + (y * gridsize))
        self.last_moved = self.direction

        # The last tail square moves away on this step (unless the snake is growing), so it's safe to enter
        body = self.positions[:-1] if len(self.positions) >= self.length else self.positions

        # If the snake hits itself or goes out of bounds, the game is lost
        if new in body:
            self.lost = True
        elif new[0] < 0 or new[0] >= screen_width or new[1] < 0 or new[1] >= screen_height:
            self.lost = True
        else:
            self.positions.insert(0, new)
            if len(self.positions) > self.length:
                self.positions.pop()

    def eat(self):
        self.length += 1
        self.score += 1
        if self.score > self.high_score:
            self.high_score = self.score
            save_high_score(self.high_score)

    def speed(self):
        return min(start_speed + self.score // speed_step, max_speed)

    def draw(self, surface):
        for i, p in enumerate(self.positions):
            r = pygame.Rect((p[0], p[1]), (gridsize, gridsize))
            pygame.draw.rect(surface, snake_head_color if i == 0 else snake_color, r)
            pygame.draw.rect(surface, light_square, r, 1)

    def handle_keys(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_c and self.lost:
                    self.reset()
                elif event.key in (pygame.K_p, pygame.K_SPACE) and not self.lost:
                    self.paused = not self.paused
                elif not self.paused and not self.lost:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.turn(up)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.turn(down)
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        self.turn(left)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.turn(right)


# Food class for snake food behavior
class Food():
    def __init__(self):
        self.position = (0, 0)
        self.color = food_color

    def randomize_position(self, snake_positions):
        # Only pick squares the snake isn't on
        free = [(x * gridsize, y * gridsize) for x in range(grid_width) for y in range(grid_height)
                if (x * gridsize, y * gridsize) not in snake_positions]
        if free:
            self.position = random.choice(free)

    def draw(self, surface):
        r = pygame.Rect((self.position[0], self.position[1]), (gridsize, gridsize))
        pygame.draw.rect(surface, self.color, r)
        pygame.draw.rect(surface, light_square, r, 1)


# Function to draw the checkerboard background
def drawGrid(surface):
    for y in range(grid_height):
        for x in range(grid_width):
            r = pygame.Rect((x * gridsize, y * gridsize), (gridsize, gridsize))
            pygame.draw.rect(surface, light_square if (x + y) % 2 == 0 else dark_square, r)


# Function to show lines of text in the middle of the board, over a dark see-through panel
def message(screen, lines, fonts):
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, bar_height))

    # the first line is the heading, in the bigger font
    rendered = []
    for i, (text, color) in enumerate(lines):
        font = fonts["big"] if i == 0 else fonts["small"]
        rendered.append(font.render(text, True, color))
    total_height = sum(r.get_height() for r in rendered) + 10 * (len(rendered) - 1)
    y = bar_height + (screen_height - total_height) // 2
    for r in rendered:
        screen.blit(r, ((screen_width - r.get_width()) // 2, y))
        y += r.get_height() + 10


# Function to draw the bar above the board: the score on the left, the best score on the right
def display_score(screen, score, high_score, fonts):
    pygame.draw.rect(screen, bar_color, (0, 0, screen_width, bar_height))
    pygame.draw.line(screen, bar_line_color, (0, bar_height - 1), (screen_width, bar_height - 1))

    def label_and_value(label, value, value_color, x, align_right):
        label_img = fonts["label"].render(label, True, bar_label_color)
        value_img = fonts["value"].render(str(value), True, value_color)
        width = label_img.get_width() + 8 + value_img.get_width()
        if align_right:
            x -= width
        # both pieces sit on the same baseline, centred in the bar
        value_y = (bar_height - value_img.get_height()) // 2
        label_y = value_y + value_img.get_height() - label_img.get_height() - 3
        screen.blit(label_img, (x, label_y))
        screen.blit(value_img, (x + label_img.get_width() + 8, value_y))

    label_and_value("SCORE", score, white, 14, False)
    # the best score turns yellow while you're beating it
    best_color = yellow if score > 0 and score == high_score else bar_value_color
    label_and_value("BEST", high_score, best_color, screen_width - 14, True)


# Main function
def main():
    pygame.init()
    pygame.display.set_caption("Snake")
    clock = pygame.time.Clock()
    # the window is the board plus the score bar above it
    screen = pygame.display.set_mode((screen_width, screen_height + bar_height), 0, 32)

    surface = pygame.Surface((screen_width, screen_height))
    surface = surface.convert()

    # fonts are created once - creating them every frame is slow
    fonts = {
        "label": pygame.font.SysFont("bahnschrift", 14),
        "value": pygame.font.SysFont("bahnschrift", 24, bold=True),
        "big": pygame.font.SysFont("bahnschrift", 36),
        "small": pygame.font.SysFont("bahnschrift", 22),
    }

    snake = Snake()
    food = Food()
    food.randomize_position(snake.positions)

    while True:
        clock.tick(snake.speed())
        snake.handle_keys()

        if not snake.lost and not snake.paused:
            snake.move()
            if snake.get_head_position() == food.position:
                snake.eat()
                food.randomize_position(snake.positions)

        drawGrid(surface)
        food.draw(surface)
        snake.draw(surface)
        screen.blit(surface, (0, bar_height))
        display_score(screen, snake.score, snake.high_score, fonts)

        if snake.lost:
            message(screen, [("Game Over!", red),
                             (f"Score: {snake.score}", white),
                             ("Press C to play again or Q to quit", white)], fonts)
        elif snake.paused:
            message(screen, [("Paused", white), ("Press P or Space to carry on", white)], fonts)

        pygame.display.update()


if __name__ == "__main__":
    main()

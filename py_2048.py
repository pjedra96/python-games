import pygame
import sys
import random
import os

# Board settings
size = 4 # 4 x 4 tiles
tile_size = 100
gap = 12
board_px = size * tile_size + (size + 1) * gap
bar_height = 56
screen_width = board_px
screen_height = board_px + bar_height
win_value = 2048
pop_ms = 110 # how long a new or merged tile takes to "pop" in

up = (0, -1)
down = (0, 1)
left = (-1, 0)
right = (1, 0)

# Colours
white = (255, 255, 255)
background = (187, 173, 160)
empty_tile = (205, 193, 180)
dark_text = (119, 110, 101)
light_text = (249, 246, 242)
bar_color = (24, 32, 58)
bar_line_color = (58, 74, 128)
bar_label_color = (140, 156, 196)
bar_value_color = (220, 226, 240)
yellow = (255, 255, 102)
tile_colors = {
    2: (238, 228, 218), 4: (237, 224, 200), 8: (242, 177, 121), 16: (245, 149, 99),
    32: (246, 124, 95), 64: (246, 94, 59), 128: (237, 207, 114), 256: (237, 204, 97),
    512: (237, 200, 80), 1024: (237, 197, 63), 2048: (237, 194, 46),
}
big_tile_color = (60, 58, 50)    # anything above 2048

# The best score is kept in a file next to this script, so it survives restarts
best_score_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bestscore.txt")


def load_best_score():
    try:
        with open(best_score_file) as f:
            return int(f.read().strip() or 0)
    except (OSError, ValueError):
        return 0


def save_best_score(score):
    try:
        with open(best_score_file, "w") as f:
            f.write(str(score))
    except OSError:
        pass    # not being able to save the best score shouldn't stop the game


def slide_line(values):
    """Slides one line of tiles towards its start and merges equal neighbours (each tile merges once).
    Returns the new line, the points scored and the indexes of the merged tiles."""
    tiles = [v for v in values if v]
    result, merged, gained = [], [], 0
    i = 0
    while i < len(tiles):
        if i + 1 < len(tiles) and tiles[i] == tiles[i + 1]:
            result.append(tiles[i] * 2)
            gained += tiles[i] * 2
            merged.append(len(result) - 1)
            i += 2
        else:
            result.append(tiles[i])
            i += 1
    return result + [0] * (len(values) - len(result)), gained, merged


# Board class to handle the game rules (no drawing here)
class Board():
    def __init__(self):
        self.best = load_best_score()
        self.reset()

    def reset(self):
        self.grid = [[0] * size for _ in range(size)]
        self.score = 0
        self.won = False # reached 2048
        self.keep_going = False # chose to carry on after winning
        self.lost = False
        self.undo_state = None
        self.popped = {} # (row, col) -> time it appeared/merged, for the pop animation
        self.add_tile()
        self.add_tile()

    def empty_cells(self):
        return [(r, c) for r in range(size) for c in range(size) if not self.grid[r][c]]

    def add_tile(self):
        cells = self.empty_cells()
        if cells:
            r, c = random.choice(cells)
            self.grid[r][c] = 4 if random.random() < 0.1 else 2
            self.popped[(r, c)] = pygame.time.get_ticks()

    def lines(self, direction):
        """The board's rows or columns as lists of cells, each starting at the side the tiles slide towards."""
        dx, dy = direction
        if dx:
            cols = range(size) if dx < 0 else range(size - 1, -1, -1)
            return [[(r, c) for c in cols] for r in range(size)]
        rows = range(size) if dy < 0 else range(size - 1, -1, -1)
        return [[(r, c) for r in rows] for c in range(size)]

    def move(self, direction):
        if self.lost or (self.won and not self.keep_going):
            return False
        before = [row[:] for row in self.grid]
        before_score = self.score
        now = pygame.time.get_ticks()
        self.popped = {}
        for line in self.lines(direction):
            new_values, gained, merged = slide_line([self.grid[r][c] for r, c in line])
            for (r, c), value in zip(line, new_values):
                self.grid[r][c] = value
            for i in merged:
                self.popped[line[i]] = now
            self.score += gained

        if self.grid == before:
            return False    # nothing moved, so no new tile either
        self.undo_state = (before, before_score, self.won)
        self.add_tile()
        if self.score > self.best:
            self.best = self.score
            save_best_score(self.best)
        if not self.won and any(v >= win_value for row in self.grid for v in row):
            self.won = True
        self.lost = not self.can_move()
        return True

    def can_move(self):
        if self.empty_cells():
            return True
        for r in range(size):
            for c in range(size):
                if c + 1 < size and self.grid[r][c] == self.grid[r][c + 1]:
                    return True
                if r + 1 < size and self.grid[r][c] == self.grid[r + 1][c]:
                    return True
        return False

    def undo(self):
        # one step back (the best score stays - it was really reached)
        if self.undo_state:
            grid, self.score, self.won = self.undo_state
            self.grid = [row[:] for row in grid]
            self.lost = False
            self.undo_state = None
            self.popped = {}


def handle_keys(board):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_r:
                board.reset()
            elif event.key == pygame.K_u:
                board.undo()
            elif event.key == pygame.K_c and board.won:
                board.keep_going = True
            elif event.key in (pygame.K_UP, pygame.K_w):
                board.move(up)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                board.move(down)
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                board.move(left)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                board.move(right)


# Function to draw the board and its tiles below the score bar
def draw_board(screen, board, fonts):
    pygame.draw.rect(screen, background, (0, bar_height, board_px, board_px))
    now = pygame.time.get_ticks()
    for r in range(size):
        for c in range(size):
            x = gap + c * (tile_size + gap)
            y = bar_height + gap + r * (tile_size + gap)
            pygame.draw.rect(screen, empty_tile, (x, y, tile_size, tile_size), border_radius=6)
            value = board.grid[r][c]
            if not value:
                continue

            # new and merged tiles grow from 60% to full size
            scale = 1.0
            started = board.popped.get((r, c))
            if started is not None and now - started < pop_ms:
                scale = 0.6 + 0.4 * (now - started) / pop_ms
            s = int(tile_size * scale)
            rect = pygame.Rect(x + (tile_size - s) // 2, y + (tile_size - s) // 2, s, s)
            pygame.draw.rect(screen, tile_colors.get(value, big_tile_color), rect, border_radius=6)

            digits = len(str(value))
            font = fonts["tile"] if digits <= 2 else fonts["tile3"] if digits == 3 else fonts["tile4"]
            text = font.render(str(value), True, dark_text if value <= 4 else light_text)
            screen.blit(text, text.get_rect(center=rect.center))


# Function to draw the bar above the board: the score on the left, the best score on the right
def display_score(screen, score, best, fonts):
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
        label_y = value_y + value_img.get_height() - label_img.get_height() - 4
        screen.blit(label_img, (x, label_y))
        screen.blit(value_img, (x + label_img.get_width() + 8, value_y))

    label_and_value("SCORE", score, white, 16, False)
    # the best score turns yellow while you're beating it
    best_color = yellow if score > 0 and score == best else bar_value_color
    label_and_value("BEST", best, best_color, screen_width - 16, True)


# Function to show lines of text in the middle of the board, over a see-through panel
def message(screen, lines, fonts):
    overlay = pygame.Surface((board_px, board_px), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, bar_height))

    # the first line is the heading, in the bigger font
    rendered = []
    for i, (text, color) in enumerate(lines):
        font = fonts["big"] if i == 0 else fonts["small"]
        rendered.append(font.render(text, True, color))
    total_height = sum(r.get_height() for r in rendered) + 10 * (len(rendered) - 1)
    y = bar_height + (board_px - total_height) // 2
    for r in rendered:
        screen.blit(r, ((screen_width - r.get_width()) // 2, y))
        y += r.get_height() + 10


# Main function
def main():
    pygame.init()
    pygame.display.set_caption("2048")
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((screen_width, screen_height))

    # fonts are created once - creating them every frame is slow
    fonts = {
        "label": pygame.font.SysFont("bahnschrift", 14),
        "value": pygame.font.SysFont("bahnschrift", 26, bold=True),
        "tile": pygame.font.SysFont("bahnschrift", 46, bold=True),
        "tile3": pygame.font.SysFont("bahnschrift", 38, bold=True),
        "tile4": pygame.font.SysFont("bahnschrift", 30, bold=True),
        "big": pygame.font.SysFont("bahnschrift", 40, bold=True),
        "small": pygame.font.SysFont("bahnschrift", 20),
    }

    board = Board()

    while True:
        clock.tick(60)
        handle_keys(board)

        draw_board(screen, board, fonts)
        display_score(screen, board.score, board.best, fonts)

        if board.lost:
            message(screen, [("Game Over!", white), (f"Score: {board.score}", white), ("U to undo, R for a new game, Q to quit", white)], fonts)
        elif board.won and not board.keep_going:
            message(screen, [("You made 2048!", yellow), ("C to keep going, R for a new game", white)], fonts)

        pygame.display.update()


if __name__ == "__main__":
    main()

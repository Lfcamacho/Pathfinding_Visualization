import pygame
from queue import PriorityQueue
import math

# Settings
SQUARE_SIZE = 15
COLUMNS = 50
ROWS = 40
GRID_POS_X = 0
GRID_POS_Y = 0
GRID_WIDTH = COLUMNS * SQUARE_SIZE 
GRID_HEIGHT = ROWS * SQUARE_SIZE
WIDTH = GRID_WIDTH 
HEIGHT = GRID_HEIGHT

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Path Finding")

# Colors
WHITE = [255,255,255]
BLACK = [0,0,0]
RED = [255,0,0]
GREEN = [0,255,0]
BLUE = [0,0,255]
PURPLE = [128,0,128]

# Fonts
pygame.font.init()
NUMBER_FONT = pygame.font.SysFont("comicsans", 35)
TITLE_FONT = pygame.font.SysFont("comicsans", 50)
BUTTON_FONT = pygame.font.SysFont("comicsans", 20)


class Board:
    def __init__(self, rows, columns):
        self.rows = rows
        self.columns = columns
        self.create_grid()

    def create_grid(self):
        self.grid = []
        x = 0
        y = 0

        for i in range(self.rows):
            row = []
            for j in range(self.columns):
                row.append(Square(i, j, SQUARE_SIZE))
                x += 1
            self.grid.append(row)
            x = 0
            y += 1
            
    def draw_grid(self, win):
        thickness = 1
        # Draw vertical lines
        for i in range(self.columns):
            pygame.draw.line(win, BLACK, (i * SQUARE_SIZE + GRID_POS_X, GRID_POS_Y), (i * SQUARE_SIZE + GRID_POS_X, GRID_POS_Y + GRID_HEIGHT), thickness)
        # Draw horizontal lines
        for i in range(self.rows):
            pygame.draw.line(win, BLACK, (GRID_POS_X, i * SQUARE_SIZE + GRID_POS_Y), (GRID_POS_X + GRID_WIDTH, i * SQUARE_SIZE + GRID_POS_Y), thickness)

    def draw_squares(self, win):
        for i in range(self.rows):
            for j in range(self.columns):
                self.grid[i][j].draw_square(win)

    def get_grid_position(self, pos):
        col = int((pos[0] - GRID_POS_X) // SQUARE_SIZE)
        row = int((pos[1] - GRID_POS_Y) // SQUARE_SIZE)
        return row, col

    def create_neighbors(self):
        for row in self.grid:
            for square in row:
                square.update_neighbors(self.grid) 


class Square:
    def __init__(self, row, col, size):
        self.x = col * size + GRID_POS_X
        self.y = row * size + GRID_POS_Y
        self.row = row
        self.col = col
        self.size = size
        self.color = WHITE
        self.obstacle = False
        self.neighbors = []
        self.visited = False
        self.parent = None
        self.f_score = float("inf")
        self.g_score = 0
        

    
    def draw_square(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.size, self.size))

    def __lt__ (self, other):
        return False

    def make_start(self):
        self.color = BLUE
    
    def make_end(self):
        self.color = BLUE
    
    def make_obstacle(self):
        self.color = BLACK
        self.obstacle = True

    def make_open(self):
        self.color = GREEN

    def make_visited(self):
        self.color = RED
        self.visited = True

    def make_path(self):
        self.color = PURPLE

    def reset(self):
        self.color = WHITE
        self.obstacle = False

    def update_neighbors(self, grid):
        for i in range(-1, 2):
            for j in range(-1, 2):
                if self.valid_neighbor(grid, self.row + i, self.col + j):
                    self.neighbors.append(grid[self.row + i][self.col + j])

    def valid_neighbor(self, grid, row, col):
        if row >= 0 and row < len(grid) and col >= 0 and col < len(grid[0]):
            if self.row != row or self.col != col:                        
                if not grid[row][col].obstacle:
                    return True
        return False                        


def draw_window(board):
    WIN.fill(WHITE)
    board.draw_squares(WIN)
    board.draw_grid(WIN)
    pygame.display.update()

def heuristic(p1, p2):
    x1, y1 = p1[0], p1[1]
    x2, y2 = p2[0], p2[1]
    h = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    return h

def find_path(board, start, end):
    open_nodes = PriorityQueue()
    open_nodes.put((0, 0, start))

    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        current = open_nodes.get()[2]
        if current == end:
            return True

        current.make_visited()
        if current == start:
            current.color = BLUE

        for node in current.neighbors:
            if not node.visited:
                h_score = heuristic((node.col, node.row), (end.col, end.row))
                g_score = current.g_score + heuristic((node.col, node.row), (current.col, current.row))
                f_score = h_score + g_score
                if f_score < node.f_score:
                    node.make_open()
                    node.f_score = f_score
                    node.g_score = g_score
                    node.parent = current
                    open_nodes.put((f_score, h_score, node))
        draw_window(board)

def draw_path(board, start, end):
    current = end
    while True:
        current = current.parent
        if current == start:
            return True
        current.make_path()



def main():
    run = True
    FPS = 60
    start = None
    end = None
    board = Board(ROWS, COLUMNS)
    clock = pygame.time.Clock()

    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

            if pygame.mouse.get_pressed()[0]:
                mouse_pos = pygame.mouse.get_pos()
                row, col = board.get_grid_position(mouse_pos)
                square = board.grid[row][col]

                if not start and square != end:
                    square.make_start()
                    start = square
                if not end and square != start:
                    square.make_end()
                    end = square
                if square != start and square != end:
                    square.make_obstacle()

            if pygame.mouse.get_pressed()[2]:
                mouse_pos = pygame.mouse.get_pos()
                row, col = board.get_grid_position(mouse_pos)
                square = board.grid[row][col]
                square.reset()

                if square == start:
                    start = None
                if square == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    board.create_neighbors()
                    find_path(board, start, end)
                    draw_path(board, start, end)



        draw_window(board)


main()
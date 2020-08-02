import sys
import math
import pygame
from queue import PriorityQueue

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Path Finding Visualizer")
algorithms = set(["a_star", "djikstra"])

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)


class Node:
    def __init__(self, row, col, width, row_count):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.row_count = row_count

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = ORANGE

    def make_open(self):
        self.color = GREEN

    def make_closed(self):
        self.color = RED

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.row_count - 1 and not grid[self.row + 1][self.col].is_barrier(): # down
            self.neighbors.append(grid[self.row + 1][self.col])
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # up
            self.neighbors.append(grid[self.row - 1][self.col])
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # left
            self.neighbors.append(grid[self.row][self.col - 1])
        if self.col < self.row_count - 1 and not grid[self.row][self.col + 1].is_barrier(): # right
            self.neighbors.append(grid[self.row][self.col + 1])

    def __lt__(self, other):
        return False


def distance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def reconstruct_path(prev_nodes, current, draw):
    while current in prev_nodes:
        current = prev_nodes[current]
        current.make_path()
        draw()


def a_star_algorithm(draw, grid, start, end):
    count = 0
    queue = PriorityQueue()
    queue.put((0, count, start))
    previous_node = {}
    g_score = {node: float('inf') for row in grid for node in row}
    g_score[start] = 0
    f_score = {node: float('inf') for row in grid for node in row}
    f_score[start] = distance(start.get_pos(), end.get_pos())

    queue_hash = {start}

    while queue:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = queue.get()[2]
        queue_hash.remove(current)

        if current == end: # makes the necessary path
            reconstruct_path(previous_node, end, draw)
            start.make_start()
            end.make_end()
            return True

        for neighbor in current.neighbors:
            n_g_score = g_score[current] + 1 # adds weight of path assuming it is 1

            if n_g_score < g_score[neighbor]:
                previous_node[neighbor] = current
                g_score[neighbor] = n_g_score
                f_score[neighbor] = n_g_score + distance(neighbor.get_pos(), end.get_pos())
                if neighbor not in queue_hash:
                    count += 1
                    queue.put((f_score[neighbor], count, neighbor))
                    queue_hash.add(neighbor)
                    neighbor.make_open()
        draw()
        if current != start:
            current.make_closed()
    return False


def djikstra_algorithm(draw, grid, start, end):
    count = 0
    queue = PriorityQueue()
    queue.put((0, count, start))
    previous_node = {}
    g_score = {node: float('inf') for row in grid for node in row}
    g_score[start] = 0
    queue_hash = {start}

    while queue:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = queue.get()[2]
        queue_hash.remove(current)

        if current == end: # makes the necessary path
            reconstruct_path(previous_node, end, draw)
            start.make_start()
            end.make_end()
            return True

        for neighbor in current.neighbors:
            n_g_score = g_score[current] + 1 # adds weight of path assuming it is 1

            if n_g_score < g_score[neighbor]:
                previous_node[neighbor] = current
                g_score[neighbor] = n_g_score
                if neighbor not in queue_hash:
                    count += 1
                    queue.put((g_score[neighbor], count, neighbor))
                    queue_hash.add(neighbor)
                    neighbor.make_open()
        draw()
        if current != start:
            current.make_closed()
    return False

def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            grid[i].append(Node(i, j, gap, rows))
    return grid


def draw_grid(window, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(window, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(window, GREY, (j * gap, 0), (j * gap, width))


def draw(window, grid, rows, width):
    window.fill(WHITE)
    for row in grid:
        for node in row:
            node.draw(window)

    draw_grid(window, rows, width)
    pygame.display.update()


def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos
    row = y // gap
    col = x // gap
    return row, col


def visualize(window, width, rows, algorithm):
    ROWS = rows
    grid = make_grid(ROWS, width)

    start = end = None
    run = True
    path_made = False
    while run:
        draw(window, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if not path_made and pygame.mouse.get_pressed()[0]: # if left mouse button is clicked
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                if not start:
                    start = node
                    start.make_start()

                elif not end and node != start:
                    end = node
                    end.make_end()

                elif node != start and node != end:
                    node.make_barrier()

            elif not path_made and pygame.mouse.get_pressed()[2]: # if right mouse button is clicked
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                node = grid[row][col]
                node.reset()
                if node == start:
                    start = None
                if node == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if not path_made and event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)

                    if algorithm == "a_star":
                        a_star_algorithm(lambda: draw(window, grid, ROWS, width), grid, start, end)
                    elif algorithm == "djikstra":
                        djikstra_algorithm(lambda: draw(window, grid, ROWS, width), grid, start, end)
                    path_made = True
                if event.key == pygame.K_c:
                    path_made = False
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    pygame.quit()


def main():
    args = sys.argv[1:]
    rows = int(args[0])
    algorithm = args[1]
    if rows < 2 or rows > 50:
        raise Exception("Invalid row count!")
    elif algorithm not in algorithms:
        raise Exception("Invalid algorithm name! Current valid algorithms are: " + str(algorithms))
    visualize(WIN, WIDTH, rows, algorithm)


if __name__ == '__main__':
    main()




from tkinter import Grid, Tk, messagebox as msg
from queue import PriorityQueue
import pygame
import sys
from pygame.locals import *

pygame.init()
font = pygame.font.SysFont(None, 50)
mainClock = pygame.time.Clock()
WIDTH = 700
SCREEN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption('Path Finding Visualization')

# Required colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
SHADOW = (0, 0, 255)
TURQUOISE = (64, 224, 208)


class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row*width
        self.y = col*width
        self.neighbor = []
        self.width = width
        self.color = WHITE
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    def is_Barrier(self):
        return self.color == BLACK

    def is_valid(self):
        return self.color == WHITE

    def make_open(self):
        self.color = GREEN

    def make_closed(self):
        self.color = RED

    def make_start(self):
        self.color = ORANGE

    def make_end(self):
        self.color = TURQUOISE

    def make_Barrier(self):
        self.color = BLACK

    def make_path(self):
        self.color = PURPLE

    def Reset(self):
        self.color = WHITE

    def draw(self, win):
        pygame.draw.rect(
            win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbor(self, grid, diagonals=False):
        # Down
        if self.row < self.total_rows-1 and not grid[self.row+1][self.col].is_Barrier():
            self.neighbor.append(grid[self.row+1][self.col])

        if self.row > 0 and not grid[self.row-1][self.col].is_Barrier():  # UP
            self.neighbor.append(grid[self.row-1][self.col])

        # Right
        if self.col < self.total_rows-1 and not grid[self.row][self.col+1].is_Barrier():
            self.neighbor.append(grid[self.row][self.col+1])

        if self.col > 0 and not grid[self.row][self.col-1].is_Barrier():  # Left
            self.neighbor.append(grid[self.row][self.col-1])
        # Diagonal's
        if diagonals:
            # Main Diagonal Down
            if 0 < self.row < self.total_rows-1 and 0 < self.col < self.total_rows-1 and not grid[self.row+1][self.col+1].is_Barrier():
                self.neighbor.append(grid[self.row+1][self.col+1])
            # Main Diagonal Up
            if 0 < self.row < self.total_rows-1 and 0 < self.col < self.total_rows-1 and not grid[self.row-1][self.col-1].is_Barrier():
                self.neighbor.append(grid[self.row-1][self.col-1])
            # Anti Diagonal Up
            if 0 < self.row < self.total_rows-1 and 0 < self.col < self.total_rows-1 and not grid[self.row-1][self.col+1].is_Barrier():
                self.neighbor.append(grid[self.row-1][self.col+1])
            # Anti Diagonal Down
            if 0 < self.row < self.total_rows-1 and 0 < self.col < self.total_rows-1 and not grid[self.row+1][self.col-1].is_Barrier():
                self.neighbor.append(grid[self.row+1][self.col-1])


def showInfo():
    root = Tk()
    root.withdraw()
    msg.showerror('No Solution!', 'There was no Possible Solution!')
    print('NO Possible Solution!')


def reconstruct_path(draw, parent, current):
    while current in parent:
        current = parent[current]
        current.make_path()
        draw()


def get_clicked_pos(pos, rows, width):
    gap = width // rows
    x, y = pos
    row = x // gap
    col = y // gap
    return row, col


def make_grid(rows, width):
    grid = []
    gap = width//rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)
    return grid


def draw_grid(win, rows, width):
    gap = width//rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i*gap), (width, i*gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j*gap, 0), (j*gap, width))


def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for spot in row:
            spot.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()


def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1-x2)+abs(y1-y2)

# * Main Algorithms


def Astar(draw, grid, start, end):
    count = 0
    parent = {}
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    # The actual value if the node
    g_score = {spot: float('inf') for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float('inf') for row in grid for spot in row}
    # The heuristic value or the predicted distance form the start and the end
    f_score[start] = h(start.get_pos(), end.get_pos())
    open_set_hash = {start}
    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        current = open_set.get()[2]
        open_set_hash.remove(current)
        if current == end:
            reconstruct_path(draw, parent, current)
            start.make_start()
            end.make_end()
            return True
        for neighbor in current.neighbor:
            temp_g_score = g_score[current]+1
            if temp_g_score < g_score[neighbor]:
                parent[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + \
                    h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()
        draw()
        if current != start:
            current.make_closed()
    if open_set.empty():
        showInfo()
    return False


def Dijsktra(draw, grid, start, end):
    count = 0
    shortest_distance = {spot: float('inf') for row in grid for spot in row}
    shortest_distance[start] = 0
    parent = {}
    open_set = PriorityQueue()
    open_set.put((count, start))
    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        minNode = open_set.get()[1]
        if minNode == end:
            reconstruct_path(draw, parent, minNode)
            start.make_start()
            end.make_end()
            return True
        for neighbor in minNode.neighbor:
            temp_node = shortest_distance[minNode]+1
            if temp_node < shortest_distance[neighbor]:
                shortest_distance[neighbor] = temp_node
                parent[neighbor] = minNode
                count += 1
                open_set.put((count, neighbor))
                neighbor.make_open()
        draw()
        if minNode != start:
            minNode.make_closed()
    if open_set.empty():
        showInfo()
    return False


def BFS(draw, start, end):
    queue = [start]
    parent = {}
    open_set = {start}
    while queue:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        current = queue.pop(0)
        if current == end:
            reconstruct_path(draw, parent, current)
            start.make_start()
            end.make_end()
            return True
        for neighbor in current.neighbor:
            if neighbor not in open_set:
                parent[neighbor] = current
                queue.append(neighbor)
                open_set.add(neighbor)
                neighbor.make_open()
        draw()
        if current != start:
            current.make_closed()
    if not queue:
        showInfo()
    return False


def DFS(draw, start, end):
    stack = [start]
    parent = {}
    open_set = {start}
    while stack:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        current = stack.pop()
        if current == end:
            reconstruct_path(draw, parent, current)
            start.make_start()
            end.make_end()
            return True
        for neighbor in current.neighbor:
            if neighbor not in open_set:
                parent[neighbor] = current
                stack.append(neighbor)
                open_set.add(neighbor)
                neighbor.make_open()
        draw()
        if current != start:
            current.make_closed()
    if not stack:
        showInfo()
        return False


def main(win, width, Algorithm):
    Rows = 50
    grid = make_grid(Rows, width)
    start = None
    end = None
    run = True
    while run:
        draw(win, grid, Rows, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, Rows, width)
                spot = grid[row][col]
                if not start and spot != end:
                    start = spot
                    start.make_start()
                elif not end and spot != start:
                    end = spot
                    end.make_end()
                elif spot != start and spot != end and spot.is_valid():
                    spot.make_Barrier()
            if pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, Rows, width)
                spot = grid[row][col]
                spot.Reset()
                if spot == start:
                    start = None
                if spot == end:
                    end = None
            if event.type == pygame.KEYDOWN:
                try:
                    if event.key == pygame.K_SPACE and start and end:
                        for row in grid:
                            for spot in row:
                                spot.update_neighbor(grid, False)
                        Algorithm(lambda: draw(win, grid, Rows, width), start, end)
                    elif event.key == pygame.K_RETURN:
                        for row in grid:
                            for spot in row:
                                spot.update_neighbor(grid, False)
                        Algorithm(lambda: draw(win, grid, Rows, width), grid, start, end)
                except:
                    print('Wrong Button!')
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(Rows, width)
                if event.key == K_ESCAPE:
                    run = False
            mainClock.tick(60)


# Options Menu---------------------------------------- #
    


def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)


def Algorithm_menu(screen, width):
    picture=pygame.image.load('Images/start.JPG').convert_alpha()
    picture = pygame.transform.scale(picture, (width, width))
    click = False
    while True:
        screen.fill(BLACK)
        screen.blit(picture,(0,0))
        draw_text('Choose One Algorithm', font, BLACK, screen, 40, 20)

        mx, my = pygame.mouse.get_pos()
        x_axis=80
        button_1 = pygame.Rect(x_axis, 100, 200, 50)
        button_2 = pygame.Rect(x_axis, 200, 200, 50)
        button_3 = pygame.Rect(x_axis, 300, 200, 50)
        button_4 = pygame.Rect(x_axis, 400, 200, 50)
        if button_1.collidepoint((mx, my)):
            if click:
                main(screen, width, lambda draw, start, end: BFS(draw, start, end))

        if button_2.collidepoint((mx, my)):
            if click:
                main(screen, width, lambda draw, start, end: DFS(draw, start, end))
        if button_3.collidepoint((mx, my)):
            if click:
                main(screen, width, lambda draw, grid, start, end: Dijsktra(draw, grid,start, end))
        if button_4.collidepoint((mx, my)):
            if click:
                main(screen, width, lambda draw, grid, start, end: Astar(draw, grid, start, end))
        pygame.draw.rect(screen, (255, 0, 0), button_1)
        pygame.draw.rect(screen, (255, 0, 0), button_2)
        pygame.draw.rect(screen, (255, 0, 0), button_3)
        pygame.draw.rect(screen, (255, 0, 0), button_4)
        draw_text('BFS', font, (255, 255, 255), screen, x_axis, 100)
        draw_text('DFS', font, (255, 255, 255), screen, x_axis, 200)
        draw_text('Dijsktra', font, (255, 255, 255), screen, x_axis,300)
        draw_text('Astar', font, (255, 255, 255), screen, x_axis, 400)

        click = False
        for event in pygame.event.get():

            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        pygame.display.update()
        mainClock.tick(60)


Algorithm_menu(SCREEN, WIDTH)

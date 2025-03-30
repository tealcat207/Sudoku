import pygame
import random

pygame.init()

WIDTH, HEIGHT = 540, 640 # Increased height for button
GRID_SIZE = WIDTH // 9
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BUTTON_COLOR = (100, 100, 255)
BUTTON_TEXT_COLOR = (255, 255, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku Game")
font = pygame.font.Font(None, 40)
button_font = pygame.font.Font(None, 50)

selected_cell = None
solve_button_rect = pygame.Rect(300, 810, 200, 40)


def is_valid(board, row, col, num):
    for x in range(9):
        if board[row][x] == num or board[x][col] == num:
            return False
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True


def solve_sudoku(board):
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                for num in range(1, 10):
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        if solve_sudoku(board):
                            return True
                        board[row][col] = 0
                return False
    return True


def generate_full_sudoku():
    board = [[0] * 9 for _ in range(9)]
    numbers = list(range(1, 10))

    def fill_board():
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    random.shuffle(numbers)
                    for num in numbers:
                        if is_valid(board, row, col, num):
                            board[row][col] = num
                            if fill_board():
                                return True
                            board[row][col] = 0
                    return False
        return True

    fill_board()
    return board


def remove_numbers(board, difficulty=40):
    attempts = difficulty
    puzzle_board = [row[:] for row in board]
    while attempts > 0:
        row, col = random.randint(0, 8), random.randint(0, 8)
        while puzzle_board[row][col] == 0:
            row, col = random.randint(0, 8), random.randint(0, 8)
        puzzle_board[row][col] = 0
        attempts -= 1
    return puzzle_board


def draw_board(board):
    screen.fill(WHITE)
    for i in range(10):
        thickness = 3 if i % 3 == 0 else 1
        pygame.draw.line(screen, BLACK, (i * GRID_SIZE, 0), (i * GRID_SIZE, WIDTH), thickness)
        pygame.draw.line(screen, BLACK, (0, i * GRID_SIZE), (WIDTH, i * GRID_SIZE), thickness)

    if selected_cell:
        pygame.draw.rect(screen, RED,
                         (selected_cell[1] * GRID_SIZE, selected_cell[0] * GRID_SIZE, GRID_SIZE, GRID_SIZE), 3)

    for row in range(9):
        for col in range(9):
            num = board[row][col]
            if num != 0:
                color = BLACK if original_board[row][col] != 0 else BLUE  # Player-inputted numbers are blue
                text = font.render(str(num), True, color)
                screen.blit(text, (col * GRID_SIZE + 20, row * GRID_SIZE + 15))

    pygame.draw.rect(screen, BUTTON_COLOR, solve_button_rect)
    button_text = button_font.render("Solve", True, BUTTON_TEXT_COLOR)
    screen.blit(button_text, (solve_button_rect.x + 50, solve_button_rect.y + 5))

    pygame.display.flip()


def get_cell(pos):
    x, y = pos
    return y // GRID_SIZE, x // GRID_SIZE


def main():
    global selected_cell, original_board
    full_board = generate_full_sudoku()
    sudoku_board = remove_numbers(full_board)
    original_board = [row[:] for row in sudoku_board]  # Store the original board to prevent modifications
    running = True

    while running:
        draw_board(sudoku_board)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if solve_button_rect.collidepoint(event.pos):
                    solve_sudoku(sudoku_board)  # Solve puzzle when button is clicked
                else:
                    selected_cell = get_cell(event.pos)
            elif event.type == pygame.KEYDOWN and selected_cell:
                row, col = selected_cell
                if original_board[row][col] == 0:  # Allow modification only if cell was originally empty
                    if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                        sudoku_board[row][col] = 0
                    elif event.unicode.isdigit():
                        num = int(event.unicode)
                        if 1 <= num <= 9:
                            sudoku_board[row][col] = num

    pygame.quit()


if __name__ == "__main__":
    main()


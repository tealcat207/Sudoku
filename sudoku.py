import pygame
import random
import time
import io
import sys

pygame.init()

WIDTH, HEIGHT = 540, 640
GRID_SIZE = WIDTH // 9
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BUTTON_COLOR = (100, 100, 255)
BUTTON_TEXT_COLOR = (255, 255, 255)
BUTTON_HOVER_COLOR = (75, 75, 200)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku Game")
font = pygame.font.Font(None, 40)
button_font = pygame.font.Font(None, 50)
congrats_font = pygame.font.Font(None, 60)

selected_cell = None
solve_button_rect = pygame.Rect(320, 590, 200, 40)  # Moved Solve Button
show_solution = False
button_hovered = False
original_board = []
game_over = False
play_again_button_rect = pygame.Rect(170, 490, 200, 40)
play_again_button_hovered = False
current_board = []
display_congrats = False
clock = pygame.time.Clock()
start_time = 0
end_time = 0


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
    """Solves the Sudoku board using backtracking."""

    def find_empty_cell(board):
        """Finds the first empty cell (0) in the board."""
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    return row, col
        return None, None  # No empty cells

    row, col = find_empty_cell(board)
    if row is None:
        return True  # Board is solved

    for num in range(1, 10):
        if is_valid(board, row, col, num):
            board[row][col] = num
            if solve_sudoku(board):
                return True  # Solution found
            board[row][col] = 0  # Backtrack
    return False  # No solution found


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
    # Draw the 9x9 grid
    for i in range(10):
        thickness = 3 if i % 3 == 0 else 1
        pygame.draw.line(screen, BLACK, (i * GRID_SIZE, 0), (i * GRID_SIZE, 9 * GRID_SIZE), thickness)
        pygame.draw.line(screen, BLACK, (0, i * GRID_SIZE), (WIDTH, i * GRID_SIZE), thickness)

    if selected_cell:
        pygame.draw.rect(screen, RED,
                         (selected_cell[1] * GRID_SIZE, selected_cell[0] * GRID_SIZE, GRID_SIZE, GRID_SIZE), 3)

    for row in range(9):
        for col in range(9):
            num = board[row][col]
            if num != 0:
                color = BLACK if original_board[row][col] != 0 else BLUE
                text = font.render(str(num), True, color)
                screen.blit(text, (col * GRID_SIZE + 20, row * GRID_SIZE + 15))
    # Draw the Solve Button
    button_color = BUTTON_HOVER_COLOR if button_hovered else BUTTON_COLOR
    pygame.draw.rect(screen, button_color, solve_button_rect)
    button_text = button_font.render("Solve", True, BUTTON_TEXT_COLOR)
    screen.blit(button_text, (solve_button_rect.x + 50, solve_button_rect.y + 5))

    # display timer
    if start_time != 0 and not game_over:  # timer does not display on congrats screen
        current_time = pygame.time.get_ticks()
        time_taken_ms = current_time - start_time
        hours = time_taken_ms // (60 * 60 * 1000)
        minutes = (time_taken_ms % (60 * 60 * 1000)) // (60 * 1000)
        seconds = (time_taken_ms % (60 * 1000)) / 1000
        time_text = font.render(f"Time: {hours}h {minutes}m {int(seconds)}s", True, BLACK)
        screen.blit(time_text, (10, HEIGHT - 40))

    pygame.display.flip()


def get_cell(pos):
    x, y = pos
    if y < HEIGHT - 50:  # Only return cell if click is within the grid area
        return y // GRID_SIZE, x // GRID_SIZE
    return None  # Return None if the click is outside the grid


def check_win(board):
    """Checks if the Sudoku board is completely and correctly filled."""
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                return False  # Empty cell found, game not over
    # Check for validity (optional, but good practice)
    for row in range(9):
        for col in range(9):
            num = board[row][col]
            board[row][col] = 0  # Temporarily remove the number to check validity
            if not is_valid(board, row, col, num):
                board[row][col] = num  # Restore the number
                return False  # Invalid placement found
            board[row][col] = num  # Restore the number
    return True  # All cells filled and valid


def reset_game():
    """Resets the game to start a new puzzle."""
    global selected_cell, show_solution, original_board, game_over, current_board, display_congrats, start_time, end_time
    selected_cell = None
    show_solution = False
    game_over = False
    display_congrats = False
    start_time = 0  # Reset timer
    end_time = 0
    full_board = generate_full_sudoku()
    sudoku_board = remove_numbers(full_board)
    original_board = [row[:] for row in sudoku_board]
    current_board = [row[:] for row in sudoku_board]


def main():
    global selected_cell, show_solution, button_hovered, original_board, game_over, play_again_button_hovered, current_board, display_congrats, start_time, end_time
    try:
        full_board = generate_full_sudoku()
        sudoku_board = remove_numbers(full_board)
        original_board = [row[:] for row in sudoku_board]
        current_board = [row[:] for row in sudoku_board]
        running = True
        solve_board = [row[:] for row in full_board]
        display_congrats = False
        clock = pygame.time.Clock()
        redraw_board = True
        start_time = pygame.time.get_ticks()

        while running:
            clock.tick(60)
            redraw_board = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    redraw_board = True
                    if game_over:
                        if play_again_button_rect.collidepoint(event.pos):
                            reset_game()
                            redraw_board = True
                            start_time = pygame.time.get_ticks()  # restart timer
                    elif solve_button_rect.collidepoint(event.pos):
                        show_solution = True
                        current_board = solve_board
                        game_over = True
                        display_congrats = True
                        end_time = pygame.time.get_ticks()
                        redraw_board = True
                    else:
                        cell = get_cell(event.pos)
                        if cell:
                            selected_cell = cell
                            redraw_board = True
                        else:
                            selected_cell = None
                            redraw_board = True
                elif event.type == pygame.MOUSEMOTION:
                    button_hovered = solve_button_rect.collidepoint(event.pos)
                    play_again_button_hovered = game_over and play_again_button_rect.collidepoint(event.pos)
                elif event.type == pygame.KEYDOWN and selected_cell:
                    row, col = selected_cell
                    if original_board[row][col] == 0:
                        if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                            current_board[row][col] = 0
                            redraw_board = True
                        elif event.unicode.isdigit():
                            num = int(event.unicode)
                            if 1 <= num <= 9:
                                current_board[row][col] = num
                                redraw_board = True

            if check_win(current_board) and not game_over:
                game_over = True
                end_time = pygame.time.get_ticks()
                redraw_board = True

            if redraw_board:
                if display_congrats:
                    screen.fill(GREEN)
                    congrats_text = congrats_font.render("Congratulations!", True, WHITE)
                    text_rect = congrats_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
                    screen.blit(congrats_text, text_rect)

                    # Calculate and display the time taken
                    time_taken_ms = end_time - start_time
                    hours = time_taken_ms // (60 * 60 * 1000)
                    minutes = (time_taken_ms % (60 * 60 * 1000)) // (60 * 1000)
                    seconds = (time_taken_ms % (60 * 1000)) / 1000
                    time_text = font.render(f"Time: {hours}h {minutes}m {int(seconds)}s", True, YELLOW)
                    text_rect = time_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
                    screen.blit(time_text, text_rect)

                    # draw play again button
                    play_again_button_color = BUTTON_HOVER_COLOR if play_again_button_hovered else BUTTON_COLOR
                    pygame.draw.rect(screen, play_again_button_color, play_again_button_rect)
                    play_again_text = button_font.render("Play Again", True, BUTTON_TEXT_COLOR)
                    text_rect = play_again_text.get_rect()
                    text_x = play_again_button_rect.centerx - text_rect.width // 2
                    text_y = play_again_button_rect.centery - text_rect.height // 2
                    screen.blit(play_again_text, (text_x, text_y))
                    pygame.display.flip()
                else:
                    draw_board(current_board)
                    pygame.display.flip()
                redraw_board = False
    except Exception as e:
        print(f"An error occurred: {e}")
        print(f"Error details: {sys.exc_info()}")

    finally:
        pygame.quit()


if __name__ == "__main__":
    main()


import pygame
import random
import time
import io
import sys

pygame.init()

WIDTH, HEIGHT = 540, 700
GRID_SIZE = WIDTH // 9
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
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
menu_font = pygame.font.Font(None, 60)  # Font for menu text

selected_cell = None
solve_button_rect = pygame.Rect(310, 640, 200, 40)
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
game_state = "menu"
difficulty = 40
exit_button_rect = pygame.Rect(10, 6, 40, 40)

def is_valid(board, row, col, num):
    for i in range(9):
        if board[row][i] == num or board[i][col] == num or board[row // 3 * 3 + i // 3][col // 3 * 3 + i % 3] == num:
            return False
    return True

def solve_sudoku(board):
    def find_empty_cell(board):
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    return row, col
        return None, None

    row, col = find_empty_cell(board)
    if row is None:
        return True

    for num in range(1, 10):
        if is_valid(board, row, col, num):
            board[row][col] = num
            if solve_sudoku(board):
                return True
            board[row][col] = 0
    return False

def generate_full_sudoku():
    board = [[0 for _ in range(9)] for _ in range(9)]
    solve_sudoku(board)
    return board

def remove_numbers(board, difficulty=40):
    board_copy = [row[:] for row in board]
    cells = list(range(81))
    random.shuffle(cells)
    for i in range(difficulty):
        row, col = cells[i] // 9, cells[i] % 9
        board_copy[row][col] = 0
    return board_copy

def draw_board(board):
    screen.fill(WHITE)
    for i in range(10):
        thickness = 3 if i % 3 == 0 else 1
        pygame.draw.line(screen, BLACK, (i * GRID_SIZE, 50), (i * GRID_SIZE, 50 + WIDTH), thickness)
        pygame.draw.line(screen, BLACK, (0, 50 + i * GRID_SIZE), (WIDTH, 50 + i * GRID_SIZE), thickness)

    if selected_cell:
        row, col = selected_cell
        pygame.draw.rect(screen, RED, (col * GRID_SIZE, 50 + row * GRID_SIZE, GRID_SIZE, GRID_SIZE), 3)

    for row in range(9):
        for col in range(9):
            num = board[row][col]
            if num != 0:
                color = BLACK if original_board[row][col] != 0 else BLUE
                text = font.render(str(num), True, color)
                screen.blit(text, (col * GRID_SIZE + 20, 50 + row * GRID_SIZE + 15))

    button_color = BUTTON_HOVER_COLOR if button_hovered else BUTTON_COLOR
    pygame.draw.rect(screen, button_color, solve_button_rect)
    button_text = button_font.render("New Game", True, BUTTON_TEXT_COLOR)
    screen.blit(button_text, (solve_button_rect.x + 15, solve_button_rect.y + 5))

    # Draw exit button
    pygame.draw.rect(screen, RED, exit_button_rect)
    exit_text = font.render("X", True, WHITE)
    exit_text_rect = exit_text.get_rect(center=exit_button_rect.center)
    screen.blit(exit_text, exit_text_rect)

    if start_time != 0 and not game_over:
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
    if  50 < y < 50 + WIDTH:
        return (y - 50) // GRID_SIZE, x // GRID_SIZE
    return None

def check_win(board):
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                return False
    for row in range(9):
        for col in range(9):
            num = board[row][col]
            board[row][col] = 0
            if not is_valid(board, row, col, num):
                board[row][col] = num
                return False
            board[row][col] = num
    return True

def reset_game():
    global selected_cell, show_solution, original_board, game_over, current_board, display_congrats, start_time, end_time
    selected_cell = None
    show_solution = False
    game_over = False
    display_congrats = False
    start_time = 0
    end_time = 0
    full_board = generate_full_sudoku()
    sudoku_board = remove_numbers(full_board, difficulty)
    original_board = [row[:] for row in sudoku_board]
    current_board = [row[:] for row in sudoku_board]
    return current_board

def draw_menu():
    screen.fill(WHITE)
    menu_text = menu_font.render("Select Difficulty", True, BLACK)
    text_rect = menu_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    screen.blit(menu_text, text_rect)

    button_y_start = HEIGHT // 2
    button_height = 50
    button_width = 200
    button_x = (WIDTH - button_width) // 2

    easy_button_rect = pygame.Rect(button_x, button_y_start, button_width, button_height)
    medium_button_rect = pygame.Rect(button_x, button_y_start + button_height + 10, button_width, button_height)
    hard_button_rect = pygame.Rect(button_x, button_y_start + 2 * (button_height + 10), button_width, button_height)

    pygame.draw.rect(screen, BUTTON_COLOR, easy_button_rect)
    pygame.draw.rect(screen, BUTTON_COLOR, medium_button_rect)
    pygame.draw.rect(screen, BUTTON_COLOR, hard_button_rect)

    easy_text = button_font.render("Easy", True, BUTTON_TEXT_COLOR)
    medium_text = button_font.render("Medium", True, BUTTON_TEXT_COLOR)
    hard_text = button_font.render("Hard", True, BUTTON_TEXT_COLOR)

    easy_text_rect = easy_text.get_rect(center=easy_button_rect.center)
    medium_text_rect = medium_text.get_rect(center=medium_button_rect.center)
    hard_text_rect = hard_text.get_rect(center=hard_button_rect.center)

    screen.blit(easy_text, easy_text_rect)
    screen.blit(medium_text, medium_text_rect)
    screen.blit(hard_text, hard_text_rect)

    # Draw exit button on menu
    pygame.draw.rect(screen, RED, exit_button_rect)
    exit_text = font.render("X", True, WHITE)
    exit_text_rect = exit_text.get_rect(center=exit_button_rect.center)
    screen.blit(exit_text, exit_text_rect)

    pygame.display.flip()

def main():
    global selected_cell, show_solution, button_hovered, original_board, game_over, play_again_button_hovered, current_board, display_congrats, start_time, end_time, game_state, difficulty
    try:
        running = True
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
                    if game_state == "menu":
                        mouse_pos = event.pos
                        button_y_start = HEIGHT // 2
                        button_height = 50
                        button_width = 200
                        button_x = (WIDTH - button_width) // 2

                        easy_button_rect = pygame.Rect(button_x, button_y_start, button_width, button_height)
                        medium_button_rect = pygame.Rect(button_x, button_y_start + button_height + 10, button_width, button_height)
                        hard_button_rect = pygame.Rect(button_x, button_y_start + 2 * (button_height + 10), button_width, button_height)
                        if exit_button_rect.collidepoint(mouse_pos):
                            running = False
                        elif easy_button_rect.collidepoint(mouse_pos):
                            difficulty = 20  # Easy difficulty (fewer numbers removed)
                            game_state = "game"
                            current_board = reset_game()
                            start_time = pygame.time.get_ticks()
                        elif medium_button_rect.collidepoint(mouse_pos):
                            difficulty = 40  # Medium difficulty
                            game_state = "game"
                            current_board = reset_game()
                            start_time = pygame.time.get_ticks()
                        elif hard_button_rect.collidepoint(mouse_pos):
                            difficulty = 60  # Hard difficulty (more numbers removed)
                            game_state = "game"
                            current_board = reset_game()
                            start_time = pygame.time.get_ticks()
                    elif game_state == "game":
                        if exit_button_rect.collidepoint(event.pos):
                            game_state = "menu"
                            game_over = False
                            start_time = 0
                            selected_cell = None
                            redraw_board = True
                        elif solve_button_rect.collidepoint(event.pos):
                            current_board = reset_game()
                            start_time = pygame.time.get_ticks()
                        else:
                            cell = get_cell(event.pos)
                            if cell:
                                selected_cell = cell
                            else:
                                selected_cell = None
                elif event.type == pygame.MOUSEMOTION:
                    button_hovered = solve_button_rect.collidepoint(event.pos)
                elif event.type == pygame.KEYDOWN and selected_cell and game_state == "game":
                    row, col = selected_cell
                    if original_board[row][col] == 0:
                        if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                            current_board[row][col] = 0
                        elif event.unicode.isdigit():
                            num = int(event.unicode)
                            if 1 <= num <= 9:
                                current_board[row][col] = num

            if game_state == "menu":
                draw_menu()
                redraw_board = False
            elif game_state == "game":
                if check_win(current_board) and not game_over:
                    game_over = True
                    end_time = pygame.time.get_ticks()
                    redraw_board = True

                if redraw_board:
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

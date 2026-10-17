import os
import pygame
import random
import sys

# Установка позиции окна
os.environ['SDL_VIDEO_WINDOW_POS'] = "50,50"

# Цвета
WHITE = (255, 255, 255)
GRAY = (192, 192, 192)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

NUMBER_COLORS = {
    1: (0, 0, 255),
    2: (0, 128, 0),
    3: (255, 0, 0),
    4: (0, 0, 128),
    5: (128, 0, 0),
    6: (64, 224, 208),
    7: (0, 0, 0),
    8: (128, 128, 128)
}

CELL_SIZE = 30
TOP_MARGIN = 50

# Фиксированный размер окна под 20x20 поле
FIXED_WIDTH = 600
FIXED_HEIGHT = 700

def draw_text(screen, text, font, color, x, y):
    render = font.render(text, True, color)
    screen.blit(render, (x, y))

def draw_text_centered(screen, text, font, color, rect):
    render = font.render(text, True, color)
    text_rect = render.get_rect(center=rect.center)
    screen.blit(render, text_rect)

def settings_screen():
    pygame.init()
    screen = pygame.display.set_mode((400, 300))
    pygame.display.set_caption("Настройки игры")
    font = pygame.font.SysFont(None, 30)

    width_input = ""
    height_input = ""
    mines_input = ""

    input_active = None
    running = True

    while running:
        screen.fill(WHITE)
        draw_text(screen, "Размер поля (макс 30x30):", font, BLACK, 20, 50)
        draw_text(screen, "Количество мин (макс 899):", font, BLACK, 20, 150)

        pygame.draw.rect(screen, GREEN if input_active == "width" else GRAY, (20, 80, 80, 30), 2)
        pygame.draw.rect(screen, GREEN if input_active == "height" else GRAY, (140, 80, 80, 30), 2)
        draw_text(screen, "x", font, BLACK, 110, 85)
        draw_text(screen, width_input, font, BLACK, 30, 85)
        draw_text(screen, height_input, font, BLACK, 150, 85)

        pygame.draw.rect(screen, GREEN if input_active == "mines" else GRAY, (20, 180, 200, 30), 2)
        draw_text(screen, mines_input, font, BLACK, 30, 185)

        play_button = pygame.Rect(250, 220, 120, 40)
        pygame.draw.rect(screen, BLUE, play_button)
        draw_text_centered(screen, "Играть", font, WHITE, play_button)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 20 <= x <= 100 and 80 <= y <= 110:
                    input_active = "width"
                elif 140 <= x <= 220 and 80 <= y <= 110:
                    input_active = "height"
                elif 20 <= x <= 220 and 180 <= y <= 210:
                    input_active = "mines"
                elif play_button.collidepoint(event.pos):
                    try:
                        width = int(width_input)
                        height = int(height_input)
                        mines = int(mines_input)
                        if width < 1 or width > 30 or height < 1 or height > 30:
                            raise ValueError("Неверный размер поля.")
                        max_mines = width * height - 1
                        if mines < 1 or mines > max_mines or mines > 899:
                            raise ValueError("Неверное количество мин.")
                        return (height, width), mines
                    except ValueError:
                        print("Ошибка ввода. Попробуйте снова.")

            if event.type == pygame.KEYDOWN:
                if input_active == "width":
                    if event.key == pygame.K_BACKSPACE:
                        width_input = width_input[:-1]
                    elif event.unicode.isdigit():
                        width_input += event.unicode
                elif input_active == "height":
                    if event.key == pygame.K_BACKSPACE:
                        height_input = height_input[:-1]
                    elif event.unicode.isdigit():
                        height_input += event.unicode
                elif input_active == "mines":
                    if event.key == pygame.K_BACKSPACE:
                        mines_input = mines_input[:-1]
                    elif event.unicode.isdigit():
                        mines_input += event.unicode

def generate_grid(grid_size, mines_count, safe_cell):
    grid = [[0 for _ in range(grid_size[1])] for _ in range(grid_size[0])]
    mines = set()

    while len(mines) < mines_count:
        x, y = random.randint(0, grid_size[0] - 1), random.randint(0, grid_size[1] - 1)
        if (x, y) != safe_cell and (x, y) not in mines:
            mines.add((x, y))

    for x, y in mines:
        grid[x][y] = -1
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < grid_size[0] and 0 <= ny < grid_size[1] and grid[nx][ny] != -1:
                    grid[nx][ny] += 1

    return grid, mines

def reveal_empty_cells(grid, revealed, x, y):
    stack = [(x, y)]
    while stack:
        cx, cy = stack.pop()
        if not revealed[cx][cy]:
            revealed[cx][cy] = True
            if grid[cx][cy] == 0:
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]):
                            stack.append((nx, ny))

def draw_flag(screen, rect):
    center = rect.center
    pole_top = (center[0], rect.top + 5)
    pole_bottom = (center[0], rect.bottom - 5)
    flag_tip = (center[0] + 10, rect.top + 15)
    pygame.draw.line(screen, BLACK, pole_top, pole_bottom, 2)
    pygame.draw.polygon(screen, RED, [pole_top, flag_tip, (center[0], center[1])])

def check_win_conditions(grid_size, revealed, flagged, mines, mines_count, first_click):
    if first_click:
        return False
    flagged_positions = {(x, y) for x in range(grid_size[0]) for y in range(grid_size[1]) if flagged[x][y]}
    if mines_count > 0 and flagged_positions == mines:
        return True
    return False

def main():
    grid_size, mines_count = settings_screen()

    rows, cols = grid_size
    board_width = cols * CELL_SIZE
    board_height = rows * CELL_SIZE

    WIDTH = FIXED_WIDTH
    HEIGHT = FIXED_HEIGHT

    scrolling = (rows > 20 or cols > 20)

    if not scrolling:
        board_x_offset = (WIDTH - board_width) // 2
        available_height = HEIGHT - TOP_MARGIN - 50
        board_y_offset = TOP_MARGIN + (available_height - board_height) // 2
    else:
        board_x_offset = 0
        board_y_offset = TOP_MARGIN

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Сапёр")
    font = pygame.font.SysFont(None, 80)
    small_font = pygame.font.SysFont(None, 40)

    grid = [[0] * cols for _ in range(rows)]
    revealed = [[False] * cols for _ in range(rows)]
    flagged = [[False] * cols for _ in range(rows)]
    mines = set()
    first_click = True
    game_over = False
    win = False

    scroll_x = 0
    scroll_y = 0

    base_speed = 5
    scroll_acceleration_frames = 0  # Счётчик кадров удержания клавиш

    def reset_game():
        nonlocal grid, revealed, flagged, first_click, mines, game_over, win, scroll_x, scroll_y, scroll_acceleration_frames
        grid = [[0] * cols for _ in range(rows)]
        revealed = [[False] * cols for _ in range(rows)]
        flagged = [[False] * cols for _ in range(rows)]
        mines = set()
        first_click = True
        game_over = False
        win = False
        scroll_x = 0
        scroll_y = 0
        scroll_acceleration_frames = 0

    menu_button = pygame.Rect(10, HEIGHT - 40, 100, 30)
    reset_button = pygame.Rect(WIDTH // 2 - 50, HEIGHT - 40, 100, 30)
    exit_button = pygame.Rect(WIDTH - 110, HEIGHT - 40, 100, 30)

    running = True
    clock = pygame.time.Clock()

    while running:
        clock.tick(30)
        screen.fill(WHITE)

        keys = pygame.key.get_pressed()
        # Проверяем, нажаты ли клавиши для скролла
        arrow_pressed = False
        if scrolling:
            if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_UP] or keys[pygame.K_DOWN]:
                arrow_pressed = True

        # Если стрелки удерживаются, увеличиваем счётчик, иначе сбрасываем
        if arrow_pressed:
            scroll_acceleration_frames += 1
        else:
            scroll_acceleration_frames = 0

        # Чем дольше удерживаем, тем быстрее скорость
        # Например, каждые 30 кадров увеличиваем скорость на 1 пиксель
        # или можно использовать линейную формулу
        scroll_speed = base_speed + scroll_acceleration_frames // 30

        if scrolling:
            if keys[pygame.K_LEFT]:
                scroll_x -= scroll_speed
            if keys[pygame.K_RIGHT]:
                scroll_x += scroll_speed
            if keys[pygame.K_UP]:
                scroll_y -= scroll_speed
            if keys[pygame.K_DOWN]:
                scroll_y += scroll_speed

        closed_count = sum(not revealed[x][y] for x in range(rows) for y in range(cols))
        flagged_count = sum(flagged[x][y] for x in range(rows) for y in range(cols))
        mines_left = mines_count - flagged_count if mines_count - flagged_count >= 0 else 0

        draw_text(screen, f"Закрыто: {closed_count}", small_font, BLACK, 10, 10)
        draw_text(screen, f"Мин осталось: {mines_left}", small_font, BLACK, 250, 10)

        if scrolling:
            max_scroll_x = max(0, board_width - 600)
            max_scroll_y = max(0, board_height - 600)
            scroll_x = max(0, min(scroll_x, max_scroll_x))
            scroll_y = max(0, min(scroll_y, max_scroll_y))
            visible_cols = 20
            visible_rows = 20
            row_start = scroll_y // CELL_SIZE
            col_start = scroll_x // CELL_SIZE
            row_end = min(rows, row_start + visible_rows)
            col_end = min(cols, col_start + visible_cols)
        else:
            row_start = 0
            col_start = 0
            row_end = rows
            col_end = cols

        # Отрисовка поля
        for x in range(row_start, row_end):
            for y in range(col_start, col_end):
                rect_x = board_x_offset + (y - col_start) * CELL_SIZE
                rect_y = board_y_offset + (x - row_start) * CELL_SIZE
                rect = pygame.Rect(rect_x, rect_y, CELL_SIZE, CELL_SIZE)
                if revealed[x][y]:
                    pygame.draw.rect(screen, GRAY, rect)
                    if grid[x][y] > 0:
                        num = grid[x][y]
                        color = NUMBER_COLORS.get(num, BLACK)
                        draw_text_centered(screen, str(num), small_font, color, rect)
                    elif grid[x][y] == -1:
                        pygame.draw.circle(screen, RED, rect.center, CELL_SIZE // 4)
                elif flagged[x][y]:
                    pygame.draw.rect(screen, WHITE, rect)
                    draw_flag(screen, rect)
                else:
                    pygame.draw.rect(screen, WHITE, rect)
                pygame.draw.rect(screen, BLACK, rect, 1)

        # Отрисовка интерфейса внизу
        pygame.draw.rect(screen, BLUE, menu_button)
        draw_text_centered(screen, "Меню", small_font, WHITE, menu_button)

        pygame.draw.rect(screen, GREEN, reset_button)
        draw_text_centered(screen, "Заново", small_font, WHITE, reset_button)

        pygame.draw.rect(screen, RED, exit_button)
        draw_text_centered(screen, "Выход", small_font, WHITE, exit_button)

        # Отрисовываем надпись о победе после поля и интерфейса
        if win:
            win_text = "Вы победили!"
            render = font.render(win_text, True, RED)
            text_rect = render.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(render, text_rect)

        pygame.display.flip()

        if not game_over:
            if check_win_conditions(grid_size, revealed, flagged, mines, mines_count, first_click):
                win = True
                game_over = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if game_over:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if menu_button.collidepoint(event.pos):
                        return main()
                    elif reset_button.collidepoint(event.pos):
                        reset_game()
                    elif exit_button.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()
                continue

            if scrolling and event.type == pygame.MOUSEWHEEL:
                scroll_x += event.x * CELL_SIZE
                scroll_y -= event.y * CELL_SIZE

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos

                if menu_button.collidepoint(event.pos):
                    return main()
                elif reset_button.collidepoint(event.pos):
                    reset_game()
                    continue
                elif exit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

                if scrolling:
                    cell_x = (mouse_y - board_y_offset) // CELL_SIZE + (scroll_y // CELL_SIZE)
                    cell_y = (mouse_x - board_x_offset) // CELL_SIZE + (scroll_x // CELL_SIZE)
                else:
                    cell_x = (mouse_y - board_y_offset) // CELL_SIZE
                    cell_y = (mouse_x - board_x_offset) // CELL_SIZE

                if 0 <= cell_x < rows and 0 <= cell_y < cols:
                    if event.button == 1:  # ЛКМ
                        if not flagged[cell_x][cell_y]:
                            if first_click:
                                grid, mines = generate_grid(grid_size, mines_count, (cell_x, cell_y))
                                reveal_empty_cells(grid, revealed, cell_x, cell_y)
                                first_click = False
                            else:
                                if not revealed[cell_x][cell_y]:
                                    if grid[cell_x][cell_y] == -1:
                                        game_over = True
                                        for mx, my in mines:
                                            revealed[mx][my] = True
                                    else:
                                        reveal_empty_cells(grid, revealed, cell_x, cell_y)
                    elif event.button == 3:  # ПКМ (флаг)
                        if not revealed[cell_x][cell_y]:
                            flagged[cell_x][cell_y] = not flagged[cell_x][cell_y]

    pygame.quit()

if __name__ == "__main__":
    main()
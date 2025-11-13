import pygame
from copy import deepcopy

from classes.GameUI import BLACK

pygame.init()

BOARDER_BUFFER = 30
ROWS, COLS = 11, 10
CELL_SIZE = 50
GREEN = (0, 80, 10, 150)
RED = (250, 0, 0, 128)
BOARD_WIDTH, BOARD_HEIGHT = (COLS - 1) * CELL_SIZE, (ROWS - 1) * CELL_SIZE
SCREEN_WIDTH, SCREEN_HEIGHT = BOARD_WIDTH + 60, BOARD_HEIGHT + 60
BOARD_COLOR = (242, 204, 143)
LINE_COLOR = (0, 0, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Xiangqi")

pieces = {}


def load_pieces():
    piece_names = {
        "rg": "red_general",
        "rh": "red_horse",
        "ra": "red_advisor",
        "re": "red_elephant",
        "rp": "red_pawn",
        "rc": "red_cannon",
        "rr": "red_rook",
        "bg": "black_general",
        "bh": "black_horse",
        "ba": "black_advisor",
        "be": "black_elephant",
        "bp": "black_pawn",
        "bc": "black_cannon",
        "br": "black_rook"
    }
    for name in piece_names:
        img = pygame.image.load(f"images/{piece_names[name]}.png")  # Load image
        img = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))  # Resize
        pieces[name] = img
    return pieces


pieces = load_pieces()

validMoves = pygame.image.load(f"images/valid.png")


def draw_board():
    screen.fill(BOARD_COLOR)

    pygame.draw.rect(screen, LINE_COLOR, (BOARDER_BUFFER, BOARDER_BUFFER, BOARD_WIDTH, BOARD_HEIGHT))
    pygame.draw.rect(screen, BOARD_COLOR, (BOARDER_BUFFER + 2, BOARDER_BUFFER + 2, BOARD_WIDTH - 4, BOARD_HEIGHT - 4))

    for row in range(ROWS - 1):
        for col in range(COLS - 1):
            x, y = col * CELL_SIZE + BOARDER_BUFFER, row * CELL_SIZE + BOARDER_BUFFER
            pygame.draw.line(screen, LINE_COLOR, (x + CELL_SIZE / 2, y), (x + CELL_SIZE / 2, y + CELL_SIZE), 2)
            pygame.draw.line(screen, LINE_COLOR, (x, y + CELL_SIZE / 2), (x + CELL_SIZE, y + CELL_SIZE / 2), 2)

    river_y_start = 4.5 * CELL_SIZE + BOARDER_BUFFER + 1
    pygame.draw.rect(screen, BOARD_COLOR, (BOARDER_BUFFER + 2, river_y_start, BOARD_WIDTH - 4, CELL_SIZE))

    pygame.draw.line(screen, LINE_COLOR, (3.5 * CELL_SIZE + BOARDER_BUFFER, 0.5 * CELL_SIZE + BOARDER_BUFFER),
                     (5.5 * CELL_SIZE + BOARDER_BUFFER, 2.5 * CELL_SIZE + BOARDER_BUFFER), 2)
    pygame.draw.line(screen, LINE_COLOR, (3.5 * CELL_SIZE + BOARDER_BUFFER, 7.5 * CELL_SIZE + BOARDER_BUFFER),
                     (5.5 * CELL_SIZE + BOARDER_BUFFER, 9.5 * CELL_SIZE + BOARDER_BUFFER), 2)
    pygame.draw.line(screen, LINE_COLOR, (5.5 * CELL_SIZE + BOARDER_BUFFER, 0.5 * CELL_SIZE + BOARDER_BUFFER),
                     (3.5 * CELL_SIZE + BOARDER_BUFFER, 2.5 * CELL_SIZE + BOARDER_BUFFER), 2)
    pygame.draw.line(screen, LINE_COLOR, (5.5 * CELL_SIZE + BOARDER_BUFFER, 7.5 * CELL_SIZE + BOARDER_BUFFER),
                     (3.5 * CELL_SIZE + BOARDER_BUFFER, 9.5 * CELL_SIZE + BOARDER_BUFFER), 2)


def draw_pieces():
    global board

    for y in range(len(board)):
        for x in range(len(board[0])):
            if (board[y][x] == "—"):
                continue
            screen.blit(pieces[board[y][x]], (x * CELL_SIZE + BOARDER_BUFFER, y * CELL_SIZE + BOARDER_BUFFER))


def draw_valid():
    alertScreen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    for move in valid_moves:
        x, y = move
        pygame.draw.circle(alertScreen, GREEN,
                           ((x + 0.5) * CELL_SIZE + BOARDER_BUFFER, (y + 0.5) * CELL_SIZE + BOARDER_BUFFER), 15)

    screen.blit(alertScreen, (0, 0))


def draw_check():
    global in_check, current_turn

    if (not in_check):
        return

    alertScreen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    x, y = general_positions[current_turn]
    if (is_checkmate()):
        pygame.draw.circle(alertScreen, GREEN,
                           ((x + 0.5) * CELL_SIZE + BOARDER_BUFFER, (y + 0.5) * CELL_SIZE + BOARDER_BUFFER), 20)
        screen.blit(alertScreen, (0, 0))

    else:

        pygame.draw.circle(alertScreen, RED,
                       ((x + 0.5) * CELL_SIZE + BOARDER_BUFFER, (y + 0.5) * CELL_SIZE + BOARDER_BUFFER), 20)
        screen.blit(alertScreen, (0, 0))

    if (is_checkmate()):
        pygame.draw.circle(alertScreen, GREEN,
                           ((x + 0.5) * CELL_SIZE + BOARDER_BUFFER, (y + 0.5) * CELL_SIZE + BOARDER_BUFFER), 20)


def is_occupied(x, y, board):
    global current_turn

    return board[y][x] != "—"


def is_enemy(x, y, color, board):
    return board[y][x][0] != color


def is_pinned(x, y, nx, ny, raw):
    global board

    if (raw):
        return False

    general_x, general_y = None, None

    if (board[y][x][1] != "g"):
        general_x, general_y = general_positions[current_turn]
    else:
        general_x, general_y = nx, ny

    concept_board = deepcopy(board)
    concept_board[ny][nx] = board[y][x]
    concept_board[y][x] = "—"

    return is_in_check(concept_board, (general_x, general_y))


def get_possible_moves(x, y, board, raw):
    moves = []
    piece = board[y][x][1]
    color = board[y][x][0]

    # For rook / chariot
    if (piece == "r"):

        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy  # Start in the direction

            while 0 <= nx < 9 and 0 <= ny < 10:  # Ensure within board limits

                # Check if there's a piece at (nx, ny)
                if (is_occupied(nx, ny, board)):
                    if (is_enemy(nx, ny, color, board)):  # Check if enemy
                        if (not is_pinned(x, y, nx, ny, raw)):  # Add if different and not pinned
                            moves.append((nx, ny))
                    break

                if (not is_pinned(x, y, nx, ny, raw)):  # Check for pins
                    moves.append((nx, ny))
                nx, ny = nx + dx, ny + dy

                # For soldier / pawn
    elif (piece == "p"):

        possible_moves = []

        if (color == "r"):
            if y > 4:  # pre-River
                possible_moves.append((x, y - 1))
            else:  # Post-river
                possible_moves.append((x, y - 1))
                if x > 0: possible_moves.append((x - 1, y))
                if x < 8: possible_moves.append((x + 1, y))
        else:
            if y < 5:  # Pre-River
                possible_moves.append((x, y + 1))
            else:  # Post-river
                possible_moves.append((x, y + 1))
                if x > 0: possible_moves.append((x - 1, y))
                if x < 8: possible_moves.append((x + 1, y))

        for nx, ny in possible_moves:
            if 0 <= nx < 9 and 0 <= ny < 10 and (not is_occupied(nx, ny, board) or is_enemy(nx, ny, color, board)):
                if (not is_pinned(x, y, nx, ny, raw)):
                    moves.append((nx, ny))

    # For elephant
    elif (piece == "e"):

        # Define all possible moves
        possible_moves = [
            (x - 2, y - 2), (x - 2, y + 2),
            (x + 2, y - 2), (x + 2, y + 2)
        ]

        # Define mid-points to check for blocking
        blocking_points = {
            (x - 2, y - 2): (x - 1, y - 1),
            (x - 2, y + 2): (x - 1, y + 1),
            (x + 2, y - 2): (x + 1, y - 1),
            (x + 2, y + 2): (x + 1, y + 1)
        }

        if color == "r":
            valid_zone = lambda y: y >= 5
        else:
            valid_zone = lambda y: y <= 4

        for (nx, ny) in possible_moves:
            if 0 <= nx < 9 and 0 <= ny < 10 and valid_zone(ny):
                block_x, block_y = blocking_points[(nx, ny)]
                if not is_occupied(block_x, block_y, board):
                    if not is_occupied(nx, ny, board) or is_enemy(nx, ny, color, board):
                        if (not is_pinned(x, y, nx, ny, raw)):
                            moves.append((nx, ny))

    # For advisor
    elif (piece == "a"):
        palace_positions = {
            "b": [(3, 0), (5, 0), (4, 1), (3, 2), (5, 2)],
            "r": [(3, 9), (5, 9), (4, 8), (3, 7), (5, 7)]
        }

        for nx, ny in palace_positions[color]:
            if abs(nx - x) == 1 and abs(ny - y) == 1:
                if not is_occupied(nx, ny, board) or is_enemy(nx, ny, color, board):
                    if (not is_pinned(x, y, nx, ny, raw)):
                        moves.append((nx, ny))

    # For general / king
    elif (piece == "g"):

        palace_positions = {
            'b': [(3, 0), (4, 0), (5, 0), (3, 1), (4, 1), (5, 1), (3, 2), (4, 2), (5, 2)],
            'r': [(3, 9), (4, 9), (5, 9), (3, 8), (4, 8), (5, 8), (3, 7), (4, 7), (5, 7)]
        }

        for (nx, ny) in palace_positions[color]:
            if abs(nx - x) + abs(ny - y) == 1:
                if not is_occupied(nx, ny, board) or is_enemy(nx, ny, color, board):
                    if (not is_pinned(x, y, nx, ny, raw)):
                        moves.append((nx, ny))

    # For cannon
    elif (piece == "c"):

        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        for dx, dy in directions:
            jumped = False
            nx, ny = x + dx, y + dy

            while 0 <= nx < 9 and 0 <= ny < 10:
                if is_occupied(nx, ny, board):
                    if not jumped:
                        jumped = True
                    else:
                        if is_enemy(nx, ny, color, board):
                            if (not is_pinned(x, y, nx, ny, raw)):
                                moves.append((nx, ny))
                        break
                else:
                    if not jumped:
                        if (not is_pinned(x, y, nx, ny, raw)):
                            moves.append((nx, ny))
                nx += dx
                ny += dy

    # For horse
    elif (piece == "h"):

        directions = [
            ((1, 0), [(2, 1), (2, -1)]),
            ((-1, 0), [(-2, 1), (-2, -1)]),
            ((0, 1), [(1, 2), (-1, 2)]),
            ((0, -1), [(1, -2), (-1, -2)])
        ]

        for (dx_leg, dy_leg), horse_moves in directions:
            leg_x, leg_y = x + dx_leg, y + dy_leg
            if 0 <= leg_x < 9 and 0 <= leg_y < 10 and not is_occupied(leg_x, leg_y, board):
                for dx, dy in horse_moves:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < 9 and 0 <= ny < 10:
                        if not is_occupied(nx, ny, board) or is_enemy(nx, ny, color, board):
                            if (not is_pinned(x, y, nx, ny, raw)):
                                moves.append((nx, ny))

    # Handle being in check

    if (in_check and not raw):

        check_moves = []

        for move in moves:
            nx, ny = move
            concept_board = deepcopy(board)
            concept_board[ny][nx] = board[y][x]
            concept_board[y][x] = "—"

            general_x, general_y = None, None

            if (board[y][x][1] != "g"):
                general_x, general_y = general_positions[current_turn]
            else:
                general_x, general_y = nx, ny

            if (not is_in_check(concept_board, (general_x, general_y))):
                check_moves.append(move)

        return check_moves

    return moves


def handle_click(pos):
    global selected_piece, selected_position, current_turn, valid_moves, board, in_check

    x, y = (pos[0] - BOARDER_BUFFER) // CELL_SIZE, (pos[1] - BOARDER_BUFFER) // CELL_SIZE

    if selected_piece is None:

        piece = board[y][x]

        if (piece != "—" and not is_enemy(x, y, current_turn, board)):
            selected_piece = piece
            selected_position = (x, y)
            valid_moves = get_possible_moves(x, y, board, False)

    elif (x, y) in valid_moves:

        # Move logic
        ox, oy = selected_position
        board[y][x] = selected_piece
        board[oy][ox] = "—"

        # Update the position if any of the two generals moved
        if (selected_piece[1] == "g"):
            general_positions[current_turn] = (x, y)
            print(current_turn.capitalize() + " general moved to " + str(general_positions[current_turn]))

        print(f"{current_turn.capitalize()} moved {selected_piece} to {x}, {y}")

        # Switch turn
        current_turn = "b" if current_turn == "r" else "r"
        print(f"Now it's {current_turn.capitalize()}'s turn.")

        # Reset selection & Valid Moves
        selected_piece = None
        selected_position = None
        valid_moves = []

        # Check if new player is in check
        in_check = is_in_check(board, general_positions[current_turn])

        if (in_check and is_checkmate()):
            print("Checkmate.")

    else:

        piece = board[y][x]

        if (piece != "—" and not is_enemy(x, y, current_turn, board) and piece != selected_piece):
            selected_piece = piece
            selected_position = (x, y)
            valid_moves = get_possible_moves(x, y, board, False)
        else:
            selected_piece = None
            selected_position = None
            valid_moves = []


def is_in_check(board, general_coords):
    global current_turn

    for y in range(len(board)):
        for x in range(len(board[0])):

            piece = board[y][x]

            if (piece == "—" or piece[0] == current_turn):
                continue

            if (general_coords in get_possible_moves(x, y, board, True)):
                return True
    return False


def is_checkmate():
    global current_turn, board

    total_moves = []

    for y in range(len(board)):
        for x in range(len(board[0])):

            piece = board[y][x]

            if (piece == "—" or piece[0] != current_turn):
                continue

            total_moves.extend(get_possible_moves(x, y, board, False))

    return len(total_moves) == 0


# Global Variables

selected_piece = None  # Tracks currently selected piece
selected_position = None  # Tracks the position of the currently selected piece

board = [
    ["br", "bh", "be", "ba", "bg", "ba", "be", "bh", "br"],
    ["—", "—", "—", "—", "—", "—", "—", "—", "—"],
    ["—", "bc", "—", "—", "—", "—", "—", "bc", "—"],
    ["bp", "—", "bp", "—", "bp", "—", "bp", "—", "bp"],
    ["—", "—", "—", "—", "—", "—", "—", "—", "—"],
    ["—", "—", "—", "—", "—", "—", "—", "—", "—"],  # Tracks the state of the board
    ["rp", "—", "rp", "—", "rp", "—", "rp", "—", "rp"],
    ["—", "rc", "—", "—", "—", "—", "—", "rc", "—"],
    ["—", "—", "—", "—", "—", "—", "—", "—", "—"],
    ["rr", "rh", "re", "ra", "rg", "ra", "re", "rh", "rr"],
]

current_turn = "r"  # Tracks the current turn color
valid_moves = []  # Tracks valid moves of currently selected piece
in_check = False  # Tracks whether the general of the current turn is in check
general_positions = {  # Tracks the position of the two generals
    "b": (4, 0),
    "r": (4, 9)
}


def main():
    running = True
    clock = pygame.time.Clock()

    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_click(pygame.mouse.get_pos())

        draw_board()
        draw_pieces()
        draw_valid()
        draw_check()
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
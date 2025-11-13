import pygame
pygame.init()

BOARDER_BUFFER = 30
ROWS, COLS = 11, 10
CELL_SIZE = 50
BOARD_WIDTH, BOARD_HEIGHT = (COLS - 1) * CELL_SIZE, (ROWS - 1) * CELL_SIZE
SCREEN_WIDTH, SCREEN_HEIGHT = BOARD_WIDTH +60, BOARD_HEIGHT +60
BOARD_COLOR = (242, 204, 143)
LINE_COLOR = (0, 0, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Xiangqi")

selected_piece = None
selected_position = None

pieces = {}

def load_pieces():
    piece_names = ["red_general", "black_general", "red_soldier", "black_soldier",
                   "red_cannon", "black_cannon", "red_chariot", "black_chariot",
                   "red_horse", "black_horse", "red_elephant", "black_elephant",
                   "red_advisor", "black_advisor"]
    for name in piece_names:
        img = pygame.image.load(f"images/{name}.png")  # Load image
        img = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))  # Resize
        pieces[name] = img
    return pieces

pieces = load_pieces()

starting_positions = {
    "black_general": (4, 0),
    "red_general": (4, 9),
    "black_chariot": [(0, 0), (8, 0)],
    "red_chariot": [(0, 9), (8, 9)],
    "black_horse": [(1, 0), (7, 0)],
    "red_horse": [(1, 9), (7, 9)],
    "black_elephant": [(2, 0), (6, 0)],
    "red_elephant": [(2, 9), (6, 9)],
    "black_advisor": [(3, 0), (5, 0)],
    "red_advisor": [(3, 9), (5, 9)],
    "black_cannon": [(1, 2), (7, 2)],
    "red_cannon": [(1, 7), (7, 7)],
    "black_soldier": [(0, 3), (2, 3), (4, 3), (6, 3), (8, 3)],
    "red_soldier": [(0, 6), (2, 6), (4, 6), (6, 6), (8, 6)]
}

def draw_board():
    screen.fill(BOARD_COLOR)

    pygame.draw.rect(screen, LINE_COLOR, (BOARDER_BUFFER, BOARDER_BUFFER, BOARD_WIDTH, BOARD_HEIGHT))
    pygame.draw.rect(screen, BOARD_COLOR, (BOARDER_BUFFER+2, BOARDER_BUFFER+2, BOARD_WIDTH-4, BOARD_HEIGHT-4))


    for row in range(ROWS - 1):
        for col in range(COLS - 1):
            x, y = col * CELL_SIZE+BOARDER_BUFFER, row * CELL_SIZE+BOARDER_BUFFER
            pygame.draw.line(screen, LINE_COLOR, (x+CELL_SIZE/2,y),(x+CELL_SIZE/2,y+CELL_SIZE),2)
            pygame.draw.line(screen, LINE_COLOR, (x,y+CELL_SIZE/2),(x+CELL_SIZE,y+CELL_SIZE/2),2)

    river_y_start = 4.5 * CELL_SIZE + BOARDER_BUFFER+1
    pygame.draw.rect(screen, BOARD_COLOR, (BOARDER_BUFFER+ 2, river_y_start, BOARD_WIDTH-4, CELL_SIZE))

    pygame.draw.line(screen, LINE_COLOR, (3.5 * CELL_SIZE+ BOARDER_BUFFER, 0.5 * CELL_SIZE + BOARDER_BUFFER), (5.5 * CELL_SIZE+BOARDER_BUFFER, 2.5 * CELL_SIZE+BOARDER_BUFFER),2)
    pygame.draw.line(screen, LINE_COLOR, (3.5 * CELL_SIZE + BOARDER_BUFFER, 7.5 * CELL_SIZE+BOARDER_BUFFER), (5.5 * CELL_SIZE+BOARDER_BUFFER, 9.5 * CELL_SIZE+BOARDER_BUFFER), 2)
    pygame.draw.line(screen, LINE_COLOR, (5.5 * CELL_SIZE+ BOARDER_BUFFER, 0.5 * CELL_SIZE + BOARDER_BUFFER), (3.5 * CELL_SIZE+BOARDER_BUFFER, 2.5 * CELL_SIZE+BOARDER_BUFFER),2)
    pygame.draw.line(screen, LINE_COLOR, (5.5 * CELL_SIZE+ BOARDER_BUFFER, 7.5 * CELL_SIZE + BOARDER_BUFFER), (3.5 * CELL_SIZE+ BOARDER_BUFFER, 9.5 * CELL_SIZE+BOARDER_BUFFER), 2)

def draw_pieces():
    for piece, positions in starting_positions.items():
        if isinstance(positions, tuple):  # Single piece (General)
            x, y = positions
            screen.blit(pieces[piece], (x * CELL_SIZE + BOARDER_BUFFER, y * CELL_SIZE + BOARDER_BUFFER))
        else:  # List of positions (e.g., Soldiers, Chariots)
            for x, y in positions:
                screen.blit(pieces[piece], (x * CELL_SIZE + BOARDER_BUFFER, y * CELL_SIZE + BOARDER_BUFFER))

def is_occupied(position, board):
    for positions in board.values():
        if isinstance(positions, tuple):
            if positions == position:
                return True
        else:
            if position in positions:
                return True
    return False

def is_enemy(target_pos, board, source_pos):
    src_piece = None
    tgt_piece = None
    for piece, positions in board.items():
        if isinstance(positions, tuple):
            if positions == source_pos:
                src_piece = piece
            elif positions == target_pos:
                tgt_piece = piece
        else:
            for pos in positions:
                if pos == source_pos:
                    src_piece = piece
                elif pos == target_pos:
                    tgt_piece = piece
    if src_piece and tgt_piece:
        return src_piece[:3] != tgt_piece[:3]
    return False

def get_possible_moves_chariot(position, board):
    x, y = position
    moves = []
    # Possible directions: right, left, down, up
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    for dx, dy in directions:
        nx, ny = x + dx, y + dy  # Start in the direction
        while 0 <= nx < 9 and 0 <= ny < 10:  # Ensure within board limits
            # Check if there's a piece at (nx, ny)
            occupied_piece = None
            for piece, positions in starting_positions.items():
                if isinstance(positions, tuple) and positions == (nx, ny):
                    occupied_piece = piece
                    break
                elif isinstance(positions, list):
                    for p in positions:
                        if p == (nx, ny):
                            occupied_piece = piece
                            break

            if occupied_piece:  # If there's a piece
                if occupied_piece.startswith("black") and position in starting_positions["red_chariot"]:
                    moves.append((nx, ny))  # Capture black piece
                elif occupied_piece.startswith("red") and position in starting_positions["black_chariot"]:
                    moves.append((nx, ny))  # Capture red piece
                break  # Stop moving after hitting a piece

            moves.append((nx, ny))  # Otherwise, it's a valid move
            nx, ny = nx + dx, ny + dy  # Move further in the same direction

    return moves

def get_possible_moves_horse(position, board):
    x, y = position
    moves = []

    directions = [
        ((1, 0), [(2, 1), (2, -1)]),  # Right leg clear → move like ┐ or ┘
        ((-1, 0), [(-2, 1), (-2, -1)]),  # Left leg clear
        ((0, 1), [(1, 2), (-1, 2)]),  # Down leg clear
        ((0, -1), [(1, -2), (-1, -2)])  # Up leg clear
    ]

    for (dx_leg, dy_leg), horse_moves in directions:
        leg_x, leg_y = x + dx_leg, y + dy_leg
        # Check if the leg is blocked
        if not is_occupied((leg_x, leg_y), board):
            for dx, dy in horse_moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < 9 and 0 <= ny < 10:
                    if not is_occupied((nx, ny), board) or is_enemy((nx, ny), board, position):
                        moves.append((nx, ny))
    return moves

def get_possible_moves_elephant(position, board, team):
    x, y = position
    moves = []

    # Define all possible diagonal "elephant" moves (2 steps diagonal)
    possible_moves = [
        (x - 2, y - 2), (x - 2, y + 2),
        (x + 2, y - 2), (x + 2, y + 2)
    ]

    # Define mid-points to check for blocking (like a "leg" in Xiangqi)
    blocking_points = {
        (x - 2, y - 2): (x - 1, y - 1),
        (x - 2, y + 2): (x - 1, y + 1),
        (x + 2, y - 2): (x + 1, y - 1),
        (x + 2, y + 2): (x + 1, y + 1)
    }

    # Elephants can't cross the river
    if team == "red":
        valid_zone = lambda y: y >= 5
    else:
        valid_zone = lambda y: y <= 4

    for (nx, ny) in possible_moves:
        if 0 <= nx < 9 and 0 <= ny < 10 and valid_zone(ny):
            block_x, block_y = blocking_points[(nx, ny)]
            if not is_occupied((block_x, block_y), board):
                if not is_occupied((nx, ny), board) or is_enemy((nx, ny), board, position):
                    moves.append((nx, ny))

    return moves

def get_possible_moves_advisor(position, board, team):
    x, y = position
    moves = []

    palace_positions = {
        "black": [(3, 0), (5, 0), (4, 1), (3, 2), (5, 2)],
        "red": [(3, 9), (5, 9), (4, 8), (3, 7), (5, 7)]
    }

    for nx, ny in palace_positions[team]:
        if abs(nx - x) == 1 and abs(ny - y) == 1:
            if not is_occupied((nx, ny), board) or is_enemy((nx, ny), board, position):
                moves.append((nx, ny))

    return moves

def get_possible_moves_cannon(position, board):
    x, y = position
    moves = []
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    for dx, dy in directions:
        jumped = False
        nx, ny = x + dx, y + dy

        while 0 <= nx < 9 and 0 <= ny < 10:
            if is_occupied((nx, ny), board):
                if not jumped:
                    jumped = True  # Found the screen
                else:
                    # Found a piece after a screen → check if it's an enemy
                    if is_enemy((nx, ny), board, position):
                        moves.append((nx, ny))
                    break  # Stop regardless after trying to capture
            else:
                if not jumped:
                    moves.append((nx, ny))  # Only add non-jump moves before a screen
            nx += dx
            ny += dy

    return moves

def get_possible_moves_soldier(position, board, team):
    x, y = position
    moves = []

    if team == 'red':
        if y > 4:  # Before crossing the river
            moves.append((x, y - 1))  # Move up
        else:  # After crossing the river
            moves.append((x, y - 1))  # Move up
            if x > 0: moves.append((x - 1, y))  # Move left
            if x < 8: moves.append((x + 1, y))  # Move right
    else:
        if y < 5:  # Before crossing the river
            moves.append((x, y + 1))  # Move down
        else:  # After crossing the river
            moves.append((x, y + 1))  # Move down
            if x > 0: moves.append((x - 1, y))  # Move left
            if x < 8: moves.append((x + 1, y))  # Move right
    valid_moves = []
    for nx, ny in moves:
        if 0 <= nx < 9 and 0 <= ny < 10 and (not is_occupied((nx, ny), board) or is_enemy((nx, ny), board, position)):
            valid_moves.append((nx, ny))
    return valid_moves

def get_possible_moves_general(position, board, team):
    moves = []
    palace_positions = {'black': [(3, 0), (4, 0), (5, 0), (3, 1), (4, 1), (5, 1), (3, 2), (4, 2), (5, 2)],
                 'red': [(3, 9), (4, 9), (5, 9), (3, 8), (4, 8), (5, 8), (3, 7), (4, 7), (5, 7)]}

    x, y = position
    for (nx, ny) in palace_positions[team]:
        if abs(nx - x) + abs(ny - y) == 1:  # Check if the move is adjacent
            if not is_occupied((nx, ny), board) or is_enemy((nx, ny), board, position):
                moves.append((nx, ny))

    return moves

def generals_facing(starting_positions):
    red_pos = None
    black_pos = None
    # Find the positions of both generals
    for (x, y), name in starting_positions.items():
        if name == "red_general":
            red_pos = (x, y)
        elif name == "black_general":
            black_pos = (x, y)
    # Check if they are on the same file
    if red_pos and black_pos and red_pos[0] == black_pos[0]:
        # Check if there are any pieces between the two generals
        x = red_pos[0]
        y_range = range(min(red_pos[1], black_pos[1]) + 1, max(red_pos[1], black_pos[1]))
        for y in y_range:
            if (x, y) in starting_positions:
                return False  # There is a piece between, so they are not facing
        return True  # No pieces in between, generals are facing
    return False  # Not on the same file

def handle_click(pos):
    global selected_piece, selected_piece_pos, current_turn

    x, y = pos[0] // CELL_SIZE, pos[1] // CELL_SIZE

    if selected_piece:
        if (x, y) in get_valid_moves(selected_piece_pos, selected_piece, starting_positions):
            # Save the current state to restore in case of invalid move
            captured_piece = starting_positions.get((x, y))

            # Make the move
            starting_positions[(x, y)] = selected_piece
            del starting_positions[selected_piece_pos]

            # Check for flying generals rule
            if generals_facing(starting_positions):
                # Invalid move: revert
                print("Invalid move: Generals cannot face each other!")
                starting_positions[selected_piece_pos] = selected_piece
                if captured_piece:
                    starting_positions[(x, y)] = captured_piece
                else:
                    starting_positions.pop((x, y), None)
            else:
                # Move is valid, switch turns
                current_turn = "black" if current_turn == "red" else "red"
                selected_piece = None
                selected_piece_pos = None
        else:
            # Deselect if clicked invalid square
            selected_piece = None
            selected_piece_pos = None
    else:
        if (x, y) in starting_positions and starting_positions[(x, y)].startswith(current_turn):
            selected_piece = starting_positions[(x, y)]
            selected_piece_pos = (x, y)

def get_valid_moves(position, piece, board):
    x, y = position
    moves = []

    if "general" in piece:
        # Generals can only move within the palace (3x3 area)
        palace_x = range(3, 6)
        palace_y = range(0, 3) if "red" in piece else range(7, 10)

        # Possible moves: up, down, left, right
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if nx in palace_x and ny in palace_y:
                target_piece = board.get((nx, ny))
                if not target_piece or not target_piece.startswith(piece.split("_")[0]):
                    moves.append((nx, ny))

    elif "chariot" in piece:
        # Chariot moves like a rook in chess: straight lines
        moves.extend(get_possible_moves_general(position, board, piece))

    elif "horse" in piece:
        moves.extend(get_possible_moves_horse(position, board))

    elif "cannon" in piece:
        moves.extend(get_possible_moves_cannon(position, board, piece))

    elif "advisor" in piece:
        moves.extend(get_possible_moves_advisor(position, board, piece))

    elif "elephant" in piece:
        moves.extend(get_possible_moves_elephant(position, board, piece))

    elif "soldier" in piece:
        moves.extend(get_possible_moves_soldier(position, board, piece))

    return moves


current_turn = "red"

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
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
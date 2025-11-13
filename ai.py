import random
from copy import deepcopy

# Basic piece values for evaluation (higher = stronger)
PIECE_VALUES = {
    "g": 5000,  # General is king (don’t lose this)
    "r": 900,  # Rook is super strong
    "h": 450,  # Horse is mobile
    "e": 250,  # Elephant = defense mostly
    "a": 200,  # Advisor guards general
    "c": 500,  # Cannon is tricky, strong if lined up
    "p": 150  # Pawn, gets more dangerous later
}

# Little bonuses based on where pawns are positioned
PAWN_POSITION_BONUS = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 5, 5, 10, 10, 10, 5, 5, 0],
    [0, 5, 10, 15, 20, 15, 10, 5, 0],
    [5, 10, 15, 20, 25, 20, 15, 10, 5],
    [5, 15, 20, 30, 35, 30, 20, 15, 5],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0]
]


# Evaluation function — scores the board from the POV of `turn`
def evaluate_board(board, general_positions, turn, get_possible_moves):
    flat = [p for row in board for p in row]
    if flat.count("rc") > 1 or flat.count("bg") > 1:
        return -50

    total = 0

    for y in range(10):
        for x in range(9):
            piece = board[y][x]
            if piece == "_":
                continue

            color, ptype = piece[0], piece[1]
            value = PIECE_VALUES.get(ptype, 0)

            # Bonus for advancing pawns
            if ptype == "p":
                bonus = PAWN_POSITION_BONUS[y][x] if color == "r" else PAWN_POSITION_BONUS[9 - y][x]
                value += bonus

            # Slight penalty if general leaves his palace area
            if ptype == "g":
                if (color == "r" and y < 7) or (color == "b" and y > 2):
                    value -= 100

            dist = abs(x - 4) + abs(y - 4)
            value -= dist * 2

            if ptype != "p":
                mobility = len(get_possible_moves(x, y, board, True))
                value += mobility * 5

            # Add or subtract based on whose side it is
            total += value if color == turn else -value

    return total


# Generate all valid moves for the current player
def get_all_moves(board, turn, general_positions, get_possible_moves):
    moves = []
    for y in range(10):
        for x in range(9):
            piece = board[y][x]
            if piece != "_" and piece[0] == turn:
                for nx, ny in get_possible_moves(x, y, board, False):
                    moves.append(((x, y), (nx, ny)))
    return moves


# Recursive alpha-beta pruning — core of the AI
def alpha_beta_search(board, general_positions, depth, alpha, beta, maximizing, turn, get_possible_moves, seen = None , tt = None):
    if seen is None:
        seen = set()
    if tt is None:
        tt = {}

    # hash position , could be better like a Zobrist
    board_hash = tuple(tuple(row) for row in board)

    if board_hash in seen:
        return 0 , None # prevents reps

    # transposition table

    if(board_hash , depth , maximizing) in tt:
        return tt[(board_hash, depth, maximizing)]

    seen.add(board_hash)

    if depth == 0:
        score = evaluate_board(board, general_positions, turn, get_possible_moves)
        tt[(board_hash, depth, maximizing)] = (score, None)
        return score, None

    enemy_turn = "b" if turn == "r" else "r"
    best_move = None
    moves = get_all_moves(board, turn if maximizing else enemy_turn, general_positions, get_possible_moves)

    if maximizing:
        max_eval = float('-inf')
        for (x, y), (nx, ny) in moves:
            new_board = deepcopy(board)
            moved_piece = new_board[y][x]
            new_board[y][x] = '_'
            new_board[ny][nx] = moved_piece
            new_general_pos = general_positions.copy()
            if moved_piece[1] == "g" and moved_piece[0] == turn:
                new_general_pos[turn] = (nx, ny)

            score, _ = alpha_beta_search(new_board, new_general_pos, depth - 1, alpha, beta, False, turn, get_possible_moves,seen.copy() , tt)

            if score > max_eval:
                max_eval = score
                best_move = ((x, y), (nx, ny))

            alpha = max(alpha, score)
            if beta <= alpha:
                break  # prune the rest
        tt[(board_hash, depth, maximizing)] = (max_eval, best_move)
        return max_eval, best_move

    else:
        min_eval = float('inf')
        for (x, y), (nx, ny) in moves:
            new_board = deepcopy(board)
            moved_piece = new_board[y][x]
            new_board[y][x] = "_"
            new_board[ny][nx] = moved_piece

            new_general_pos = general_positions.copy()
            if moved_piece[1] == "g" and moved_piece[0] == enemy_turn:
                new_general_pos[enemy_turn] = (nx, ny)

            score, _ = alpha_beta_search(new_board, new_general_pos, depth - 1, alpha, beta, True, turn, get_possible_moves ,seen.copy() , tt )

            if score < min_eval:
                min_eval = score
                best_move = ((x, y), (nx, ny))

            beta = min(beta, score)
            if beta <= alpha:
                break  # prune


        tt[(board_hash, depth, maximizing)] = (min_eval, best_move)
        return min_eval, best_move


def get_ai_move(board, turn, general_positions, get_possible_moves, depth=3):
    tt = {}
    seen = set()
    score, best_move = alpha_beta_search(board, general_positions, depth, float('-inf'), float('inf'),
                                         True, turn, get_possible_moves, seen, tt)

    if best_move is None:
        return None

    
    all_moves = get_all_moves(board, turn, general_positions, get_possible_moves)
    top_moves = []

    for move in all_moves:
        (x1, y1), (x2, y2) = move
        new_board = deepcopy(board)
        moved_piece = new_board[y1][x1]
        new_board[y1][x1] = "_"
        new_board[y2][x2] = moved_piece

        new_general_pos = general_positions.copy()
        if moved_piece[1] == "g" and moved_piece[0] == turn:
            new_general_pos[turn] = (x2, y2)

        score_i, _ = alpha_beta_search(
            new_board, new_general_pos, depth - 1, float('-inf'), float('inf'),
            False, turn, get_possible_moves, set(), tt
        )

        if score_i == score:
            top_moves.append(move)

    return random.choice(top_moves) if top_moves else best_move

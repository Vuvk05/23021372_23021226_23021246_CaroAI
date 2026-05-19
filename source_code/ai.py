import time
from game import HUMAN, AI, EMPTY, WIN_LENGTH
from evaluate import evaluate_board

INF = float('inf')


class AIStats:
    def __init__(self):
        self.reset()

    def reset(self):
        self.states_explored = 0
        self.time_elapsed = 0.0
        self.best_move = None
        self.best_score = 0
        self.depth = 0
        self.algorithm = ""

    def __str__(self):
        return (f"[{self.algorithm}] depth={self.depth} | "
                f"states={self.states_explored:,} | "
                f"time={self.time_elapsed:.4f}s | "
                f"move={self.best_move} | score={self.best_score}")


# ---------- LEVEL 1: MINIMAX ----------

def minimax(board, size, depth, is_maximizing, last_move, stats):
 
    stats.states_explored += 1

    if last_move is not None:
        r, c = last_move
        player = board[r][c]
        if _check_win(board, r, c, player, size):
            return (100_000 + depth) if player == AI else -(100_000 + depth)

    if depth == 0 or _board_full(board, size):
        return evaluate_board(board, size)

    moves = _order_moves(_get_candidates(board, size), board, size)
    if not moves:
        return evaluate_board(board, size)

    if is_maximizing:
        best = -INF
        for (r, c) in moves:
            board[r][c] = AI
            val = minimax(board, size, depth - 1, False, (r, c), stats)
            board[r][c] = EMPTY
            best = max(best, val)
        return best
    else:
        best = INF
        for (r, c) in moves:
            board[r][c] = HUMAN
            val = minimax(board, size, depth - 1, True, (r, c), stats)
            board[r][c] = EMPTY
            best = min(best, val)
        return best


def get_best_move_minimax(game, depth):
    """Trả về nước đi tốt nhất cho AI dùng Minimax."""
    stats = AIStats()
    stats.algorithm = "Minimax"
    stats.depth = depth

    start = time.time()
    best_score = -INF
    best_move = None

    board = [row[:] for row in game.board]
    moves = _order_moves(game.get_candidate_moves(), board, game.size)

    for (r, c) in moves:
        board[r][c] = AI
        stats.states_explored += 1
        val = minimax(board, game.size, depth - 1, False, (r, c), stats)
        board[r][c] = EMPTY
        if val > best_score:
            best_score = val
            best_move = (r, c)

    stats.time_elapsed = time.time() - start
    stats.best_move = best_move
    stats.best_score = best_score
    return best_move, stats


# ---------- LEVEL 2: ALPHA-BETA ----------

def alpha_beta(board, size, depth, alpha, beta, is_maximizing, last_move, stats):
    stats.states_explored += 1

    if last_move is not None:
        r, c = last_move
        player = board[r][c]
        if _check_win(board, r, c, player, size):
            return (100_000 + depth) if player == AI else -(100_000 + depth)

    if depth == 0 or _board_full(board, size):
        return evaluate_board(board, size)

    moves = _order_moves(_get_candidates(board, size), board, size)
    if not moves:
        return evaluate_board(board, size)

    if is_maximizing:
        best = -INF
        for (r, c) in moves:
            board[r][c] = AI
            val = alpha_beta(board, size, depth - 1, alpha, beta, False, (r, c), stats)
            board[r][c] = EMPTY
            best = max(best, val)
            alpha = max(alpha, best)
            if beta <= alpha:
                break
        return best
    else:
        best = INF
        for (r, c) in moves:
            board[r][c] = HUMAN
            val = alpha_beta(board, size, depth - 1, alpha, beta, True, (r, c), stats)
            board[r][c] = EMPTY
            best = min(best, val)
            beta = min(beta, best)
            if beta <= alpha:
                break
        return best


def get_best_move_alphabeta(game, depth):
    stats = AIStats()
    stats.algorithm = "Alpha-Beta"
    stats.depth = depth

    start = time.time()
    best_score = -INF
    best_move = None
    alpha = -INF
    beta = INF

    board = [row[:] for row in game.board]
    moves = _order_moves(game.get_candidate_moves(), board, game.size)

    for (r, c) in moves:
        board[r][c] = AI
        stats.states_explored += 1
        val = alpha_beta(board, game.size, depth - 1, alpha, beta, False, (r, c), stats)
        board[r][c] = EMPTY
        if val > best_score:
            best_score = val
            best_move = (r, c)
        alpha = max(alpha, best_score)

    stats.time_elapsed = time.time() - start
    stats.best_move = best_move
    stats.best_score = best_score
    return best_move, stats


# ---------- HELPERS ----------

def _check_win(board, r, c, player, size):
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for dr, dc in directions:
        count = 1
        for sign in [1, -1]:
            rr, cc = r + sign * dr, c + sign * dc
            while 0 <= rr < size and 0 <= cc < size and board[rr][cc] == player:
                count += 1
                rr += sign * dr
                cc += sign * dc
        if count >= WIN_LENGTH:
            return True
    return False


def _board_full(board, size):
    return all(board[r][c] != EMPTY for r in range(size) for c in range(size))


def _get_candidates(board, size, radius=2):
    has_piece = any(board[r][c] != EMPTY for r in range(size) for c in range(size))
    if not has_piece:
        center = size // 2
        return [(center, center)]
    candidates = set()
    for r in range(size):
        for c in range(size):
            if board[r][c] != EMPTY:
                for dr in range(-radius, radius + 1):
                    for dc in range(-radius, radius + 1):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < size and 0 <= nc < size and board[nr][nc] == EMPTY:
                            candidates.add((nr, nc))
    return list(candidates)


def _order_moves(moves, board, size):
    wins, blocks, rest = [], [], []
    for (r, c) in moves:
        board[r][c] = AI
        if _check_win(board, r, c, AI, size):
            board[r][c] = EMPTY
            wins.append((r, c))
            continue
        board[r][c] = EMPTY

        board[r][c] = HUMAN
        if _check_win(board, r, c, HUMAN, size):
            board[r][c] = EMPTY
            blocks.append((r, c))
            continue
        board[r][c] = EMPTY

        rest.append((r, c))

    def quick_score(rc):
        r, c = rc
        board[r][c] = AI
        s = evaluate_board(board, size)
        board[r][c] = EMPTY
        return s

    rest.sort(key=quick_score, reverse=True)
    return wins + blocks + rest

BOARD_SIZE = 9
WIN_LENGTH = 4
HUMAN = 1
AI = -1
EMPTY = 0


class CaroGame:
    def __init__(self, size=BOARD_SIZE):
        self.size = size
        self.board = [[EMPTY] * size for _ in range(size)]
        self.current_player = HUMAN
        self.move_count = 0
        self.last_move = None
        self.winner = None
        self.game_over = False

    def copy(self):
        g = CaroGame(self.size)
        g.board = [row[:] for row in self.board]
        g.current_player = self.current_player
        g.move_count = self.move_count
        g.last_move = self.last_move
        g.winner = self.winner
        g.game_over = self.game_over
        return g

    def is_valid_move(self, row, col):
        return (0 <= row < self.size and
                0 <= col < self.size and
                self.board[row][col] == EMPTY)

    def make_move(self, row, col, player=None):
        if player is None:
            player = self.current_player
        if not self.is_valid_move(row, col):
            return False
        self.board[row][col] = player
        self.last_move = (row, col)
        self.move_count += 1
        if self.check_win(row, col, player):
            self.winner = player
            self.game_over = True
        elif self.move_count == self.size * self.size:
            self.game_over = True  
        else:
            self.current_player = -player
        return True

    def check_win(self, row, col, player):
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            for sign in [1, -1]:
                r, c = row + sign * dr, col + sign * dc
                while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
                    count += 1
                    r += sign * dr
                    c += sign * dc
            if count >= WIN_LENGTH:
                return True
        return False

    def get_candidate_moves(self, radius=2):
        """Return moves near existing pieces to reduce search space."""
        if self.move_count == 0:
            center = self.size // 2
            return [(center, center)]

        candidates = set()
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] != EMPTY:
                    for dr in range(-radius, radius + 1):
                        for dc in range(-radius, radius + 1):
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < self.size and 0 <= nc < self.size and self.board[nr][nc] == EMPTY:
                                candidates.add((nr, nc))
        return list(candidates) if candidates else self._all_empty()

    def _all_empty(self):
        return [(r, c) for r in range(self.size) for c in range(self.size) if self.board[r][c] == EMPTY]

    def get_winner_line(self):
        """Return the winning 4-cell line for display."""
        if self.winner is None or self.last_move is None:
            return []
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        row, col = self.last_move
        player = self.winner
        for dr, dc in directions:
            line = [(row, col)]
            for sign in [1, -1]:
                r, c = row + sign * dr, col + sign * dc
                while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
                    line.append((r, c))
                    r += sign * dr
                    c += sign * dc
            if len(line) >= WIN_LENGTH:
                return line
        return []

    def print_board(self):
        symbols = {HUMAN: 'X', AI: 'O', EMPTY: '.'}
        header = '   ' + ' '.join(f'{c:2}' for c in range(self.size))
        print(header)
        for r in range(self.size):
            row_str = f'{r:2} ' + ' '.join(f' {symbols[self.board[r][c]]}' for c in range(self.size))
            print(row_str)

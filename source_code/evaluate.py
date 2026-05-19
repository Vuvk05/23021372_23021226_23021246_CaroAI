from game import HUMAN, AI, EMPTY, WIN_LENGTH
SCORE_TABLE = {
    4: 100_000,  
    3: 50_000,   
    2: 500,       
    1: 10,        
}

BLOCK_TABLE = {
    4: 80_000,    
    3: 40_000,    
    2: 400,
    1: 8,
}


def count_sequence(board, r, c, dr, dc, player, size):
    length = 0
    rr, cc = r, c
    while 0 <= rr < size and 0 <= cc < size and board[rr][cc] == player:
        length += 1
        rr += dr
        cc += dc
    # kiểm tra đầu sau
    end_open = (0 <= rr < size and 0 <= cc < size and board[rr][cc] == EMPTY)

    # kiểm tra đầu trước
    pr, pc = r - dr, c - dc
    start_open = (0 <= pr < size and 0 <= pc < size and board[pr][pc] == EMPTY)

    open_ends = int(start_open) + int(end_open)
    return length, open_ends


def evaluate_board(board, size):
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    visited = [[{} for _ in range(size)] for _ in range(size)]
    score = 0

    for r in range(size):
        for c in range(size):
            if board[r][c] == EMPTY:
                continue
            player = board[r][c]
            for idx, (dr, dc) in enumerate(directions):
                # Chỉ tính theo hướng xuôi để tránh đếm trùng
                pr, pc = r - dr, c - dc
                if 0 <= pr < size and 0 <= pc < size and board[pr][pc] == player:
                    continue  # đã được tính từ ô trước

                length, open_ends = count_sequence(board, r, c, dr, dc, player, size)

                if length >= WIN_LENGTH:
                    seq_score = SCORE_TABLE[4]
                elif open_ends == 0:
                    seq_score = 0  # bị chặn 2 đầu, vô nghĩa
                elif open_ends == 1:
                    seq_score = BLOCK_TABLE.get(length, 0)
                else:  # open_ends == 2
                    seq_score = SCORE_TABLE.get(length, 0)

                if player == AI:
                    score += seq_score
                else:
                    score -= seq_score

    return score

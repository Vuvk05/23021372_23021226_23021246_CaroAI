import time
from game import CaroGame, HUMAN, AI, EMPTY
from ai import get_best_move_minimax, get_best_move_alphabeta


# ========== 5 TRẠNG THÁI KIỂM THỬ ==========
# Board 9x9: 1=X (người), -1=O (AI), 0=trống

def make_board(moves_x, moves_o, size=9):
    b = [[EMPTY] * size for _ in range(size)]
    for r, c in moves_x:
        b[r][c] = HUMAN
    for r, c in moves_o:
        b[r][c] = AI
    return b


TEST_STATES = [
    {
        "name": "Trạng thái 1 - Đầu ván (chỉ 1 quân)",
        "board": make_board([(4, 4)], []),
        "desc": "Người vừa đánh trung tâm, AI đi đầu tiên phản công."
    },
    {
        "name": "Trạng thái 2 - Giữa ván",
        "board": make_board(
            [(4, 4), (4, 5), (3, 3), (5, 6)],
            [(4, 3), (5, 5), (3, 4), (6, 5)]
        ),
        "desc": "Ván đang diễn ra, hai bên có chuỗi 2 quân."
    },
    {
        "name": "Trạng thái 3 - AI sắp thắng (3 quân liên tiếp)",
        "board": make_board(
            [(0, 0), (1, 1), (7, 7)],
            [(4, 4), (4, 5), (4, 6)]
        ),
        "desc": "AI có 3 quân liên tiếp hàng ngang, cần đánh thêm 1 để thắng."
    },
    {
        "name": "Trạng thái 4 - Người sắp thắng, AI cần chặn",
        "board": make_board(
            [(3, 3), (3, 4), (3, 5)],
            [(5, 5), (6, 6), (7, 7)]
        ),
        "desc": "Người có 3 quân hàng ngang, AI phải chặn (3,2) hoặc (3,6)."
    },
    {
        "name": "Trạng thái 5 - Hai bên tấn công, nhiều nhánh",
        "board": make_board(
            [(4, 4), (4, 5), (3, 4), (5, 3)],
            [(5, 5), (5, 6), (4, 6), (3, 5)]
        ),
        "desc": "Cả hai đều có cơ hội, không gian tìm kiếm rộng."
    },
]


def run_benchmark(depths=(1, 2, 3)):
    results = []
    sep = "-" * 100

    print("\n" + "=" * 100)
    print("  BENCHMARK: MINIMAX vs ALPHA-BETA - CỜ CARO 9x9 (4 quân liên tiếp)")
    print("=" * 100)

    for state in TEST_STATES:
        print(f"\n{sep}")
        print(f"  {state['name']}")
        print(f"  Mô tả: {state['desc']}")
        print(f"{sep}")
        print(f"  {'Depth':>5} | {'Algorithm':>12} | {'States':>10} | {'Time(s)':>10} | {'Move':>10} | {'Score':>10}")
        print(f"  {'-'*5} | {'-'*12} | {'-'*10} | {'-'*10} | {'-'*10} | {'-'*10}")

        for depth in depths:
            for algo_name, algo_fn in [("Minimax", get_best_move_minimax),
                                        ("Alpha-Beta", get_best_move_alphabeta)]:
                game = CaroGame()
                game.board = [row[:] for row in state["board"]]
                game.current_player = AI
                # Đếm số quân đã đánh
                game.move_count = sum(
                    1 for r in range(game.size) for c in range(game.size)
                    if game.board[r][c] != EMPTY
                )

                move, stats = algo_fn(game, depth)

                row = {
                    "state": state["name"],
                    "depth": depth,
                    "algorithm": algo_name,
                    "states": stats.states_explored,
                    "time": stats.time_elapsed,
                    "move": str(move),
                    "score": stats.best_score,
                }
                results.append(row)

                print(f"  {depth:>5} | {algo_name:>12} | {stats.states_explored:>10,} | "
                      f"{stats.time_elapsed:>10.4f} | {str(move):>10} | {stats.best_score:>10}")

    # Tổng hợp hiệu quả
    print(f"\n{'=' * 100}")
    print("  PHÂN TÍCH TỔNG HỢP")
    print(f"{'=' * 100}")
    print(f"\n  {'State':>2} | {'Depth':>5} | {'MM States':>12} | {'AB States':>12} | "
          f"{'Giảm (%)':>10} | {'MM Time':>10} | {'AB Time':>10} | {'Same move?':>12}")
    print(f"  {'-'*2} | {'-'*5} | {'-'*12} | {'-'*12} | {'-'*10} | {'-'*10} | {'-'*10} | {'-'*12}")

    state_names = [s["name"][:20] for s in TEST_STATES]

    for si, state in enumerate(TEST_STATES):
        for depth in depths:
            mm = next(r for r in results if r["state"] == state["name"] and r["depth"] == depth and r["algorithm"] == "Minimax")
            ab = next(r for r in results if r["state"] == state["name"] and r["depth"] == depth and r["algorithm"] == "Alpha-Beta")

            reduction = ((mm["states"] - ab["states"]) / mm["states"] * 100) if mm["states"] > 0 else 0
            same_move = "✓ Giống" if mm["move"] == ab["move"] else "✗ Khác"

            print(f"  {si+1:>2} | {depth:>5} | {mm['states']:>12,} | {ab['states']:>12,} | "
                  f"{reduction:>9.1f}% | {mm['time']:>10.4f} | {ab['time']:>10.4f} | {same_move:>12}")

    print(f"\n{'=' * 100}")
    _print_analysis(results, depths)
    return results


def _print_analysis(results, depths):
    print("\n  NHẬN XÉT VÀ PHÂN TÍCH:")
    print()

    # Tính số liệu tổng hợp
    reductions = []
    same_moves = 0
    total = 0
    mm_times_by_depth = {d: [] for d in depths}
    ab_times_by_depth = {d: [] for d in depths}
    mm_states_by_depth = {d: [] for d in depths}
    ab_states_by_depth = {d: [] for d in depths}

    for state in TEST_STATES:
        for depth in depths:
            mm = next(r for r in results if r["state"] == state["name"] and r["depth"] == depth and r["algorithm"] == "Minimax")
            ab = next(r for r in results if r["state"] == state["name"] and r["depth"] == depth and r["algorithm"] == "Alpha-Beta")
            if mm["states"] > 0:
                reductions.append((mm["states"] - ab["states"]) / mm["states"] * 100)
            total += 1
            if mm["move"] == ab["move"]:
                same_moves += 1
            mm_times_by_depth[depth].append(mm["time"])
            ab_times_by_depth[depth].append(ab["time"])
            mm_states_by_depth[depth].append(mm["states"])
            ab_states_by_depth[depth].append(ab["states"])

    avg_red = sum(reductions) / len(reductions) if reductions else 0
if __name__ == "__main__":
    run_benchmark(depths=[1, 2, 3])

import sys
import threading
import pygame
from game import CaroGame, HUMAN, AI, EMPTY
from ai import get_best_move_minimax, get_best_move_alphabeta

# ─── CONSTANTS ───────────────────────────────────────────────────────────────
BOARD_SIZE = 9
CELL = 62          
MARGIN = 48         
BOARD_PX = CELL * BOARD_SIZE + MARGIN * 2
PANEL_W = 320
WIN_W = BOARD_PX + PANEL_W
WIN_H = BOARD_PX

FPS = 60

# Colors
BG          = (245, 235, 210)
BOARD_BG    = (255, 248, 225)
LINE_COL    = (160, 130,  80)
DARK_LINE   = ( 80,  50,  20)
X_COL       = ( 30,  80, 200)
O_COL       = (200,  40,  40)
WIN_LINE    = (255, 200,   0)
PANEL_BG    = ( 40,  40,  55)
TEXT_WHITE  = (240, 240, 240)
TEXT_GRAY   = (180, 180, 190)
TEXT_YELLOW = (255, 215,   0)
TEXT_GREEN  = (100, 220, 120)
TEXT_RED    = (255, 100, 100)
BTN_NORMAL  = ( 70,  70,  95)
BTN_HOVER   = (100, 100, 140)
BTN_ACTIVE  = ( 60, 120, 200)
HIGHLIGHT   = (255, 255, 100, 120)
LAST_MOVE   = (100, 200, 100, 160)

AI_THINKING_COL = (255, 180, 50)


def rc_to_px(r, c):
    return MARGIN + c * CELL + CELL // 2, MARGIN + r * CELL + CELL // 2


def px_to_rc(x, y):
    c = (x - MARGIN) // CELL
    r = (y - MARGIN) // CELL
    return r, c


class Button:
    def __init__(self, rect, text, active=False):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.active = active
        self.hovered = False

    def draw(self, surf, font):
        col = BTN_ACTIVE if self.active else (BTN_HOVER if self.hovered else BTN_NORMAL)
        pygame.draw.rect(surf, col, self.rect, border_radius=8)
        pygame.draw.rect(surf, (120, 120, 160), self.rect, 1, border_radius=8)
        txt = font.render(self.text, True, TEXT_WHITE)
        surf.blit(txt, txt.get_rect(center=self.rect.center))

    def handle(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            return True
        return False


class CaroApp:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Caro AI – Minimax & Alpha-Beta")
        self.screen = pygame.display.set_mode((WIN_W, WIN_H))
        self.clock = pygame.time.Clock()

        self.font_lg = pygame.font.SysFont("Segoe UI", 20, bold=True)
        self.font_md = pygame.font.SysFont("Segoe UI", 15)
        self.font_sm = pygame.font.SysFont("Segoe UI", 13)
        self.font_mono = pygame.font.SysFont("Consolas", 12)

        self.game = CaroGame(BOARD_SIZE)
        self.ai_mode = "alphabeta"   # "minimax" | "alphabeta"
        self.depth = 3
        self.stats_log = []          # list of AIStats
        self.ai_thinking = False
        self.status_msg = "Lượt của bạn (X)"
        self.winner_line = []

        px = BOARD_PX + 18
        self._build_buttons(px)

    def _build_buttons(self, px):
        # Title chiếm ~60px, label "Thuật toán" tại y=65
        y = 80   # nút algo bắt đầu từ y=80 (dưới label)
        self.btn_mm   = Button((px,      y, 138, 36), "Minimax",    self.ai_mode == "minimax")
        self.btn_ab   = Button((px+146,  y, 138, 36), "Alpha-Beta", self.ai_mode == "alphabeta")
        y += 54  # label "Độ sâu" tại y=134
        self.btn_d1   = Button((px,      y, 62, 32), "D=1", self.depth == 1)
        self.btn_d2   = Button((px+70,   y, 62, 32), "D=2", self.depth == 2)
        self.btn_d3   = Button((px+140,  y, 62, 32), "D=3", self.depth == 3)
        self.btn_d4   = Button((px+210,  y, 62, 32), "D=4", self.depth == 4)
        y += 50  # nút Ván mới / Benchmark
        self.btn_new   = Button((px,      y, 138, 34), "Ván mới",   False)
        self.btn_bench = Button((px+146,  y, 138, 34), "Benchmark", False)
        self.all_buttons = [self.btn_mm, self.btn_ab,
                            self.btn_d1, self.btn_d2, self.btn_d3, self.btn_d4,
                            self.btn_new, self.btn_bench]

    def _set_mode(self, mode):
        self.ai_mode = mode
        self.btn_mm.active = (mode == "minimax")
        self.btn_ab.active = (mode == "alphabeta")

    def _set_depth(self, d):
        self.depth = d
        for b, v in zip([self.btn_d1, self.btn_d2, self.btn_d3, self.btn_d4], [1, 2, 3, 4]):
            b.active = (v == d)

    def new_game(self):
        self.game = CaroGame(BOARD_SIZE)
        self.stats_log.clear()
        self.winner_line = []
        self.status_msg = "Lượt của bạn (X)"
        self.ai_thinking = False

    def run_benchmark_thread(self):
        """Chạy benchmark ở terminal, không block GUI."""
        import benchmark
        benchmark.run_benchmark(depths=[1, 2, 3])

    # ── EVENT HANDLING ────────────────────────────────────────────────────────

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            for btn in self.all_buttons:
                btn.handle(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos

                # Button clicks
                if self.btn_mm.rect.collidepoint(x, y):
                    self._set_mode("minimax")
                elif self.btn_ab.rect.collidepoint(x, y):
                    self._set_mode("alphabeta")
                elif self.btn_d1.rect.collidepoint(x, y): self._set_depth(1)
                elif self.btn_d2.rect.collidepoint(x, y): self._set_depth(2)
                elif self.btn_d3.rect.collidepoint(x, y): self._set_depth(3)
                elif self.btn_d4.rect.collidepoint(x, y): self._set_depth(4)
                elif self.btn_new.rect.collidepoint(x, y): self.new_game()
                elif self.btn_bench.rect.collidepoint(x, y):
                    t = threading.Thread(target=self.run_benchmark_thread, daemon=True)
                    t.start()
                    self.status_msg = "Benchmark đang chạy trong terminal..."

                # Board click
                elif (not self.game.game_over and
                      not self.ai_thinking and
                      self.game.current_player == HUMAN and
                      x < BOARD_PX):
                    r, c = px_to_rc(x, y)
                    if self.game.is_valid_move(r, c):
                        self.game.make_move(r, c, HUMAN)
                        if self.game.game_over:
                            self._end_game()
                        else:
                            self.status_msg = "AI đang suy nghĩ..."
                            self.ai_thinking = True
                            threading.Thread(target=self._ai_move, daemon=True).start()

    def _ai_move(self):
        algo = get_best_move_alphabeta if self.ai_mode == "alphabeta" else get_best_move_minimax
        move, stats = algo(self.game, self.depth)
        if move:
            self.game.make_move(move[0], move[1], AI)
            self.stats_log.append(stats)
            if len(self.stats_log) > 6:
                self.stats_log.pop(0)
        self.ai_thinking = False
        if self.game.game_over:
            self._end_game()
        else:
            self.status_msg = "Lượt của bạn (X)"

    def _end_game(self):
        self.winner_line = self.game.get_winner_line()
        if self.game.winner == HUMAN:
            self.status_msg = "🎉 Bạn thắng!"
        elif self.game.winner == AI:
            self.status_msg = "🤖 AI thắng!"
        else:
            self.status_msg = "🤝 Hòa!"

    # ── DRAWING ───────────────────────────────────────────────────────────────

    def draw(self):
        self.screen.fill(BG)
        self._draw_board()
        self._draw_pieces()
        self._draw_winner_line()
        self._draw_last_move()
        self._draw_panel()
        pygame.display.flip()

    def _draw_board(self):
        pygame.draw.rect(self.screen, BOARD_BG, (0, 0, BOARD_PX, WIN_H))
        for i in range(BOARD_SIZE + 1):
            x = MARGIN + i * CELL
            y = MARGIN + i * CELL
            thick = 2 if i == 0 or i == BOARD_SIZE else 1
            col = DARK_LINE if i == 0 or i == BOARD_SIZE else LINE_COL
            pygame.draw.line(self.screen, col, (x, MARGIN), (x, MARGIN + BOARD_SIZE * CELL), thick)
            pygame.draw.line(self.screen, col, (MARGIN, y), (MARGIN + BOARD_SIZE * CELL, y), thick)

    def _draw_pieces(self):
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                p = self.game.board[r][c]
                if p == EMPTY:
                    continue
                cx, cy = rc_to_px(r, c)
                radius = CELL // 2 - 6
                if p == HUMAN:
                    pygame.draw.line(self.screen, X_COL,
                                     (cx - radius, cy - radius), (cx + radius, cy + radius), 4)
                    pygame.draw.line(self.screen, X_COL,
                                     (cx + radius, cy - radius), (cx - radius, cy + radius), 4)
                else:
                    pygame.draw.circle(self.screen, O_COL, (cx, cy), radius, 4)

    def _draw_winner_line(self):
        if not self.winner_line:
            return
        surf = pygame.Surface((BOARD_PX, WIN_H), pygame.SRCALPHA)
        for r, c in self.winner_line:
            cx, cy = rc_to_px(r, c)
            pygame.draw.circle(surf, (*WIN_LINE, 160), (cx, cy), CELL // 2 - 4)
        self.screen.blit(surf, (0, 0))

    def _draw_last_move(self):
        if self.game.last_move is None:
            return
        r, c = self.game.last_move
        cx, cy = rc_to_px(r, c)
        surf = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
        pygame.draw.rect(surf, (*LAST_MOVE,), (0, 0, CELL, CELL), border_radius=4)
        self.screen.blit(surf, (cx - CELL // 2, cy - CELL // 2))

    def _draw_panel(self):
        px = BOARD_PX
        pad = 12  # padding trái
        pygame.draw.rect(self.screen, PANEL_BG, (px, 0, PANEL_W, WIN_H))
        pygame.draw.line(self.screen, (80, 80, 110), (px, 0), (px, WIN_H), 2)

        # ── TITLE (y=10..55) ──────────────────────────────────────────────────
        title = self.font_lg.render("CARO AI", True, TEXT_YELLOW)
        self.screen.blit(title, (px + pad, 10))
        sub = self.font_sm.render("Minimax & Alpha-Beta Pruning", True, TEXT_GRAY)
        self.screen.blit(sub, (px + pad, 34))

        # divider
        pygame.draw.line(self.screen, (70, 70, 95), (px+pad, 56), (px+PANEL_W-pad, 56), 1)

        # ── LABELS (y=60, y=118) ──────────────────────────────────────────────
        self.screen.blit(self.font_sm.render("Thuật toán:", True, TEXT_GRAY), (px + pad, 62))
        # nút algo tại y=80 (do _build_buttons)

        self.screen.blit(self.font_sm.render("Độ sâu:", True, TEXT_GRAY), (px + pad, 120))
        # nút depth tại y=134

        # ── BUTTONS (vẽ sau labels) ───────────────────────────────────────────
        for btn in self.all_buttons:
            btn.draw(self.screen, self.font_md)

        # divider sau các nút (nút cuối kết thúc ~y=218)
        pygame.draw.line(self.screen, (70, 70, 95), (px+pad, 222), (px+PANEL_W-pad, 222), 1)

        # ── STATUS (y=225..270) ───────────────────────────────────────────────
        col = (TEXT_GREEN   if ("thắng" in self.status_msg.lower() and "AI" not in self.status_msg) else
               TEXT_RED     if "AI thắng" in self.status_msg else
               AI_THINKING_COL if "đang" in self.status_msg else
               TEXT_WHITE)
        status = self.font_md.render(self.status_msg, True, col)
        self.screen.blit(status, (px + pad, 228))

        if self.ai_thinking:
            dots = "." * ((pygame.time.get_ticks() // 400) % 4)
            thinking = self.font_sm.render(f"Đang tính{dots}", True, AI_THINKING_COL)
            self.screen.blit(thinking, (px + pad, 250))

        # divider
        pygame.draw.line(self.screen, (70, 70, 95), (px+pad, 270), (px+PANEL_W-pad, 270), 1)

        # ── STATS LOG (y=274..) ───────────────────────────────────────────────
        self.screen.blit(self.font_sm.render("Thống kê nước đi", True, TEXT_GRAY), (px + pad, 274))

        # header
        y = 294
        # cột: Nước | Algo | D | States | Time
        cols = [(pad,   "No",     TEXT_YELLOW),
                (38,    "Algo",   TEXT_YELLOW),
                (80,    "D",      TEXT_YELLOW),
                (100,   "States", TEXT_YELLOW),
                (200,   "Time",   TEXT_YELLOW)]
        for ox, label, c in cols:
            self.screen.blit(self.font_mono.render(label, True, c), (px + ox, y))
        y += 16
        pygame.draw.line(self.screen, (70, 70, 95), (px+pad, y-2), (px+PANEL_W-pad, y-2), 1)

        for i, st in enumerate(self.stats_log):
            algo_short = "MM" if st.algorithm == "Minimax" else "AB"
            row_col = TEXT_WHITE if i % 2 == 0 else TEXT_GRAY
            items = [
                (pad,   str(i + 1)),
                (38,    algo_short),
                (80,    str(st.depth)),
                (100,   f"{st.states_explored:,}"),
                (200,   f"{st.time_elapsed:.3f}s"),
            ]
            for ox, text in items:
                self.screen.blit(self.font_mono.render(text, True, row_col), (px + ox, y))
            y += 18

        # ── SCORE (bottom area) ───────────────────────────────────────────────
        score_y = WIN_H - 110
        pygame.draw.line(self.screen, (70, 70, 95), (px+pad, score_y), (px+PANEL_W-pad, score_y), 1)
        if self.stats_log:
            last = self.stats_log[-1]
            score_col = TEXT_GREEN if last.best_score > 0 else TEXT_RED if last.best_score < 0 else TEXT_WHITE
            self.screen.blit(self.font_sm.render("Điểm đánh giá:", True, TEXT_GRAY), (px+pad, score_y+8))
            self.screen.blit(self.font_md.render(f"{last.best_score:+,}", True, score_col), (px+pad, score_y+26))
            self.screen.blit(self.font_sm.render(f"Nước đi: {last.best_move}", True, TEXT_WHITE), (px+pad, score_y+50))

        # ── FOOTER ────────────────────────────────────────────────────────────
        pygame.draw.line(self.screen, (70, 70, 95), (px+pad, WIN_H-42), (px+PANEL_W-pad, WIN_H-42), 1)
        self.screen.blit(self.font_sm.render("Click ô trống để đánh", True, TEXT_GRAY), (px+pad, WIN_H-34))
        self.screen.blit(self.font_sm.render("'Benchmark' chạy phân tích", True, TEXT_GRAY), (px+pad, WIN_H-18))

    # ── MAIN LOOP ─────────────────────────────────────────────────────────────

    def run(self):
        while True:
            self.handle_events()
            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    CaroApp().run()

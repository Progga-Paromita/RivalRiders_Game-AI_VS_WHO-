import pygame

from game_state import (
    BOARD_SIZE,
    ROAD,
    BUILDING,
    TRAFFIC,
    ROADBLOCK,
    MOVE,
    BLOCK,
)


class GameGUI:
    """
    Pygame interface.

    Supports:
        AI vs AI
        Human vs AI
    """

    WIDTH = 1000
    HEIGHT = 760

    BOARD_X = 40
    BOARD_Y = 100
    CELL = 75

    def __init__(self, state, ai_a=None, ai_b=None, human_player=None):
        pygame.init()

        pygame.display.set_caption(
            "Rival Riders: Delivery War"
        )

        self.screen = pygame.display.set_mode(
            (self.WIDTH, self.HEIGHT)
        )

        self.clock = pygame.time.Clock()

        self.state = state

        self.ai = {
            0: ai_a,
            1: ai_b
        }

        self.human_player = human_player

        self.running = True
        self.paused = False

        # AI speed:
        # lower value = faster
        self.ai_delay = 0.35
        self.last_ai_time = 0

        self.logs = []

        self.last_thinking_time = {
            0: 0.0,
            1: 0.0
        }

        self.font = pygame.font.SysFont(
            "arial",
            20
        )

        self.small_font = pygame.font.SysFont(
            "arial",
            16
        )

        self.title_font = pygame.font.SysFont(
            "arial",
            28,
            bold=True
        )

        # Speed slider.
        self.slider_x = 700
        self.slider_y = 55
        self.slider_w = 200

    # ------------------------------------------------------------------
    # TEXT
    # ------------------------------------------------------------------

    def draw_text(self, text, x, y, font=None):
        if font is None:
            font = self.font

        surface = font.render(
            text,
            True,
            (30, 30, 30)
        )

        self.screen.blit(
            surface,
            (x, y)
        )

    # ------------------------------------------------------------------
    # BOARD
    # ------------------------------------------------------------------

    def draw_board(self):
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x = self.BOARD_X + c * self.CELL
                y = self.BOARD_Y + r * self.CELL

                cell = self.state.board[r][c]

                if cell == ROAD:
                    color = (235, 235, 235)

                elif cell == BUILDING:
                    color = (90, 90, 90)

                elif cell == TRAFFIC:
                    color = (240, 190, 80)

                elif cell == ROADBLOCK:
                    color = (120, 60, 60)

                pygame.draw.rect(
                    self.screen,
                    color,
                    (x, y, self.CELL, self.CELL)
                )

                pygame.draw.rect(
                    self.screen,
                    (180, 180, 180),
                    (x, y, self.CELL, self.CELL),
                    1
                )

                # Building icon.
                if cell == BUILDING:
                    self.draw_text(
                        "■",
                        x + 27,
                        y + 20,
                        self.title_font
                    )

                # Traffic icon.
                elif cell == TRAFFIC:
                    self.draw_text(
                        "!",
                        x + 31,
                        y + 20,
                        self.title_font
                    )

                # Roadblock icon.
                elif cell == ROADBLOCK:
                    self.draw_text(
                        "X",
                        x + 27,
                        y + 20,
                        self.title_font
                    )

        # Orders.
        for index, order in enumerate(self.state.orders):
            pr, pc = order["pickup"]
            dr, dc = order["dropoff"]

            px = self.BOARD_X + pc * self.CELL + self.CELL // 2
            py = self.BOARD_Y + pr * self.CELL + self.CELL // 2

            dx = self.BOARD_X + dc * self.CELL + self.CELL // 2
            dy = self.BOARD_Y + dr * self.CELL + self.CELL // 2

            pygame.draw.circle(
                self.screen,
                (40, 170, 80),
                (px, py),
                15
            )

            self.draw_text(
                "P",
                px - 6,
                py - 11,
                self.small_font
            )

            pygame.draw.circle(
                self.screen,
                (150, 80, 180),
                (dx, dy),
                15
            )

            self.draw_text(
                "D",
                dx - 6,
                dy - 11,
                self.small_font
            )

        # Carried orders.
        for player in [0, 1]:
            order = self.state.carried_order[player]

            if order is not None:
                r, c = order["dropoff"]

                x = self.BOARD_X + c * self.CELL
                y = self.BOARD_Y + r * self.CELL

                pygame.draw.rect(
                    self.screen,
                    (255, 255, 255),
                    (
                        x + 5,
                        y + 5,
                        self.CELL - 10,
                        self.CELL - 10
                    ),
                    3
                )

    # ------------------------------------------------------------------
    # RIDERS
    # ------------------------------------------------------------------

    def draw_riders(self):
        colors = [
            (220, 50, 50),
            (50, 80, 220)
        ]

        labels = ["A", "B"]

        for player in [0, 1]:
            r, c = self.state.positions[player]

            x = (
                self.BOARD_X
                + c * self.CELL
                + self.CELL // 2
            )

            y = (
                self.BOARD_Y
                + r * self.CELL
                + self.CELL // 2
            )

            pygame.draw.circle(
                self.screen,
                colors[player],
                (x, y),
                25
            )

            self.draw_text(
                labels[player],
                x - 7,
                y - 14,
                self.font
            )

    # ------------------------------------------------------------------
    # TOP PANEL
    # ------------------------------------------------------------------

    def draw_top_panel(self):
        self.draw_text(
            "RIVAL RIDERS: DELIVERY WAR",
            40,
            25,
            self.title_font
        )

        self.draw_text(
            f"🔴 Rider A: {self.state.scores[0]}",
            390,
            25
        )

        self.draw_text(
            f"🔵 Rider B: {self.state.scores[1]}",
            530,
            25
        )

        self.draw_text(
            f"Turn: {self.state.total_turns()} / 80",
            390,
            55,
            self.small_font
        )

        # Slider.
        pygame.draw.line(
            self.screen,
            (100, 100, 100),
            (self.slider_x, self.slider_y),
            (
                self.slider_x + self.slider_w,
                self.slider_y
            ),
            5
        )

        slider_position = int(
            self.slider_x
            + (self.ai_delay / 1.0) * self.slider_w
        )

        pygame.draw.circle(
            self.screen,
            (50, 50, 50),
            (slider_position, self.slider_y),
            8
        )

        self.draw_text(
            "AI speed",
            610,
            47,
            self.small_font
        )

    # ------------------------------------------------------------------
    # RIGHT PANEL
    # ------------------------------------------------------------------

    def draw_info_panel(self):
        x = 650
        y = 110

        current = self.state.current_player

        if self.human_player == current:
            action_text = "YOUR TURN"
        else:
            action_text = "AI THINKING"

        self.draw_text(
            f"Current: Rider {'A' if current == 0 else 'B'}",
            x,
            y,
            self.title_font
        )

        self.draw_text(
            action_text,
            x,
            y + 40
        )

        self.draw_text(
            f"A roadblocks left: {self.state.roadblocks_left[0]}",
            x,
            y + 80,
            self.small_font
        )

        self.draw_text(
            f"B roadblocks left: {self.state.roadblocks_left[1]}",
            x,
            y + 105,
            self.small_font
        )

        self.draw_text(
            f"A thinking: "
            f"{self.last_thinking_time[0] * 1000:.1f} ms",
            x,
            y + 145,
            self.small_font
        )

        self.draw_text(
            f"B thinking: "
            f"{self.last_thinking_time[1] * 1000:.1f} ms",
            x,
            y + 170,
            self.small_font
        )

        self.draw_text(
            "Orders:",
            x,
            y + 210
        )

        order_y = y + 240

        for i, order in enumerate(self.state.orders):
            self.draw_text(
                f"{i + 1}. "
                f"P{order['pickup']} → D{order['dropoff']}",
                x,
                order_y,
                self.small_font
            )

            order_y += 25

        self.draw_text(
            "Action Log:",
            x,
            order_y + 20
        )

        log_y = order_y + 50

        for message in self.logs[-8:]:
            # Keep long messages inside panel.
            if len(message) > 43:
                message = message[:40] + "..."

            self.draw_text(
                message,
                x,
                log_y,
                self.small_font
            )

            log_y += 23

    # ------------------------------------------------------------------
    # BUTTONS
    # ------------------------------------------------------------------

    def draw_buttons(self):
        y = 700

        buttons = [
            ("Pause / Resume", 40, 150),
            ("Step", 210, 100)
        ]

        for text, x, w in buttons:
            pygame.draw.rect(
                self.screen,
                (210, 210, 210),
                (x, y, w, 40)
            )

            pygame.draw.rect(
                self.screen,
                (100, 100, 100),
                (x, y, w, 40),
                1
            )

            self.draw_text(
                text,
                x + 15,
                y + 9,
                self.small_font
            )

    # ------------------------------------------------------------------
    # HUMAN INPUT
    # ------------------------------------------------------------------

    def handle_human_click(self, mouse_pos):
        if self.state.current_player != self.human_player:
            return

        mx, my = mouse_pos

        # Board click.
        if (
            self.BOARD_X <= mx < self.BOARD_X + BOARD_SIZE * self.CELL
            and
            self.BOARD_Y <= my < self.BOARD_Y + BOARD_SIZE * self.CELL
        ):
            c = (mx - self.BOARD_X) // self.CELL
            r = (my - self.BOARD_Y) // self.CELL

            move = (MOVE, r, c)

            if move in self.state.get_legal_moves(
                self.human_player
            ):
                message = self.state.apply_move(move)

                self.logs.append(message)

    # ------------------------------------------------------------------
    # AI MOVE
    # ------------------------------------------------------------------

    def make_ai_move(self):
        player = self.state.current_player

        if self.human_player == player:
            return

        ai = self.ai[player]

        if ai is None:
            return

        # Avoid running AI every frame.
        now = pygame.time.get_ticks() / 1000.0

        if now - self.last_ai_time < self.ai_delay:
            return

        self.last_ai_time = now

        move = ai.choose_move(self.state)

        self.last_thinking_time[player] = (
            ai.last_thinking_time
        )

        if move is None:
            message = self.state.apply_move(None)
        else:
            message = self.state.apply_move(move)

        self.logs.append(message)

    # ------------------------------------------------------------------
    # EVENTS
    # ------------------------------------------------------------------

    def handle_events(self):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:

                mx, my = event.pos

                # Pause button.
                if 40 <= mx <= 190 and 700 <= my <= 740:
                    self.paused = not self.paused

                # Step button.
                elif 210 <= mx <= 310 and 700 <= my <= 740:
                    self.make_ai_move()

                else:
                    self.handle_human_click(
                        event.pos
                    )

            elif event.type == pygame.MOUSEMOTION:
                # Speed slider.
                mx, my = event.pos

                if pygame.mouse.get_pressed()[0]:
                    if (
                        self.slider_x <= mx
                        <= self.slider_x + self.slider_w
                        and
                        abs(my - self.slider_y) < 20
                    ):
                        ratio = (
                            mx - self.slider_x
                        ) / self.slider_w

                        ratio = max(
                            0.0,
                            min(1.0, ratio)
                        )

                        # 0.03 to 1.0 seconds.
                        self.ai_delay = (
                            0.03 + ratio * 0.97
                        )

    # ------------------------------------------------------------------
    # MAIN LOOP
    # ------------------------------------------------------------------

    def run(self):
        while self.running:

            self.handle_events()

            if not self.paused and not self.state.is_terminal():
                self.make_ai_move()

            self.screen.fill(
                (248, 248, 248)
            )

            self.draw_top_panel()
            self.draw_board()
            self.draw_riders()
            self.draw_info_panel()
            self.draw_buttons()

            if self.state.is_terminal():
                self.draw_game_over()

            pygame.display.flip()

            self.clock.tick(60)

        pygame.quit()

    # ------------------------------------------------------------------
    # GAME OVER
    # ------------------------------------------------------------------

    def draw_game_over(self):
        winner = self.state.winner()

        if winner is None:
            message = "DRAW!"
        else:
            message = (
                f"RIDER {'A' if winner == 0 else 'B'} WINS!"
            )

        overlay = pygame.Surface(
            (600, 130),
            pygame.SRCALPHA
        )

        overlay.fill(
            (255, 255, 255, 235)
        )

        self.screen.blit(
            overlay,
            (180, 320)
        )

        self.draw_text(
            message,
            310,
            350,
            self.title_font
        )

        self.draw_text(
            f"Final score: "
            f"{self.state.scores[0]} - "
            f"{self.state.scores[1]}",
            310,
            390
        )
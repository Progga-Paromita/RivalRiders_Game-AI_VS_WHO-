import sys
import time

import pygame

from game_state import GameState
from minimax_ai import MinimaxAI
from mcts_ai import MCTS_AI
from gui import GameGUI


# ================================================================
# SETTINGS
# ================================================================

DEFAULT_SEED = 42
DEFAULT_MINIMAX_DEPTH = 3
DEFAULT_MCTS_SIMULATIONS = 300
DEFAULT_ROLLOUT_DEPTH = 15


# ================================================================
# AI VS AI
# ================================================================

def run_ai_vs_ai(
    seed=DEFAULT_SEED,
    minimax_depth=DEFAULT_MINIMAX_DEPTH,
    mcts_simulations=DEFAULT_MCTS_SIMULATIONS
):
    state = GameState(seed)

    minimax = MinimaxAI(
        player=0,
        depth=minimax_depth
    )

    mcts = MCTS_AI(
        player=1,
        simulations=mcts_simulations,
        rollout_depth=DEFAULT_ROLLOUT_DEPTH,
        seed=seed + 100
    )

    gui = GameGUI(
        state,
        ai_a=minimax,
        ai_b=mcts,
        human_player=None
    )

    gui.run()


# ================================================================
# HUMAN VS AI
# ================================================================

def run_human_vs_ai(
    human_player,
    seed=DEFAULT_SEED,
    minimax_depth=DEFAULT_MINIMAX_DEPTH,
    mcts_simulations=DEFAULT_MCTS_SIMULATIONS
):
    state = GameState(seed)

    if human_player == 0:
        # Human = Rider A.
        ai_a = None
        ai_b = MCTS_AI(
            player=1,
            simulations=mcts_simulations,
            rollout_depth=DEFAULT_ROLLOUT_DEPTH,
            seed=seed + 100
        )
    else:
        # Human = Rider B.
        ai_a = MinimaxAI(
            player=0,
            depth=minimax_depth
        )

        ai_b = None

    gui = GameGUI(
        state,
        ai_a=ai_a,
        ai_b=ai_b,
        human_player=human_player
    )

    gui.run()


# ================================================================
# TOURNAMENT
# ================================================================

def run_tournament(
    games=20,
    minimax_depth=3,
    mcts_simulations=300
):
    print()
    print("=" * 60)
    print("RIVAL RIDERS AI TOURNAMENT")
    print("=" * 60)

    minimax_wins = 0
    mcts_wins = 0
    draws = 0

    minimax_total_time = 0.0
    mcts_total_time = 0.0

    minimax_moves = 0
    mcts_moves = 0

    for game_number in range(1, games + 1):

        state = GameState(
            seed=DEFAULT_SEED + game_number
        )

        minimax = MinimaxAI(
            player=0,
            depth=minimax_depth
        )

        mcts = MCTS_AI(
            player=1,
            simulations=mcts_simulations,
            rollout_depth=DEFAULT_ROLLOUT_DEPTH,
            seed=5000 + game_number
        )

        while not state.is_terminal():

            player = state.current_player

            if player == 0:
                start = time.perf_counter()

                move = minimax.choose_move(state)

                elapsed = (
                    time.perf_counter() - start
                )

                minimax_total_time += elapsed
                minimax_moves += 1

            else:
                start = time.perf_counter()

                move = mcts.choose_move(state)

                elapsed = (
                    time.perf_counter() - start
                )

                mcts_total_time += elapsed
                mcts_moves += 1

            if move is None:
                state.apply_move(None)
            else:
                state.apply_move(move)

        winner = state.winner()

        if winner == 0:
            minimax_wins += 1
            result = "Minimax win"

        elif winner == 1:
            mcts_wins += 1
            result = "MCTS win"

        else:
            draws += 1
            result = "Draw"

        print(
            f"Game {game_number:02d}: "
            f"{state.scores[0]} - {state.scores[1]} "
            f"→ {result}"
        )

    print()
    print("-" * 60)

    print(
        f"Minimax wins : {minimax_wins}"
    )

    print(
        f"MCTS wins    : {mcts_wins}"
    )

    print(
        f"Draws        : {draws}"
    )

    print()

    if minimax_moves:
        print(
            "Average Minimax thinking time: "
            f"{minimax_total_time / minimax_moves * 1000:.2f} ms"
        )

    if mcts_moves:
        print(
            "Average MCTS thinking time: "
            f"{mcts_total_time / mcts_moves * 1000:.2f} ms"
        )

    print("=" * 60)

    input("\nPress Enter to return to menu...")


# ================================================================
# MENU
# ================================================================

def draw_menu(screen, font, title_font):
    screen.fill(
        (245, 245, 245)
    )

    title = title_font.render(
        "RIVAL RIDERS: DELIVERY WAR",
        True,
        (30, 30, 30)
    )

    screen.blit(
        title,
        (150, 80)
    )

    options = [
        "1. AI vs AI  (Minimax vs MCTS)",
        "2. Human vs AI",
        "3. AI vs AI Tournament",
        "4. Exit"
    ]

    y = 200

    for option in options:
        text = font.render(
            option,
            True,
            (40, 40, 40)
        )

        screen.blit(
            text,
            (220, y)
        )

        y += 70

    info = font.render(
        "Press 1, 2, 3 or 4",
        True,
        (100, 100, 100)
    )

    screen.blit(
        info,
        (340, 500)
    )


def main_menu():
    pygame.init()

    screen = pygame.display.set_mode(
        (800, 600)
    )

    pygame.display.set_caption(
        "Rival Riders"
    )

    clock = pygame.time.Clock()

    font = pygame.font.SysFont(
        "arial",
        25
    )

    title_font = pygame.font.SysFont(
        "arial",
        32,
        bold=True
    )

    running = True

    while running:

        draw_menu(
            screen,
            font,
            title_font
        )

        pygame.display.flip()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_1:
                    pygame.quit()

                    run_ai_vs_ai()

                    pygame.init()

                    screen = pygame.display.set_mode(
                        (800, 600)
                    )

                elif event.key == pygame.K_2:
                    pygame.quit()

                    human_vs_ai_menu()

                    pygame.init()

                    screen = pygame.display.set_mode(
                        (800, 600)
                    )

                elif event.key == pygame.K_3:
                    pygame.quit()

                    run_tournament(
                        games=20
                    )

                    pygame.init()

                    screen = pygame.display.set_mode(
                        (800, 600)
                    )

                elif event.key == pygame.K_4:
                    running = False

        clock.tick(30)

    pygame.quit()


# ================================================================
# HUMAN VS AI MENU
# ================================================================

def human_vs_ai_menu():
    pygame.init()

    screen = pygame.display.set_mode(
        (800, 600)
    )

    pygame.display.set_caption(
        "Human vs AI"
    )

    font = pygame.font.SysFont(
        "arial",
        25
    )

    title_font = pygame.font.SysFont(
        "arial",
        32,
        bold=True
    )

    clock = pygame.time.Clock()

    running = True

    while running:

        screen.fill(
            (245, 245, 245)
        )

        title = title_font.render(
            "HUMAN VS AI",
            True,
            (30, 30, 30)
        )

        screen.blit(
            title,
            (300, 100)
        )

        options = [
            "1. Human Rider A vs MCTS",
            "2. Human Rider B vs Minimax",
            "3. Back"
        ]

        y = 220

        for option in options:
            text = font.render(
                option,
                True,
                (40, 40, 40)
            )

            screen.blit(
                text,
                (200, y)
            )

            y += 70

        pygame.display.flip()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_1:
                    pygame.quit()

                    run_human_vs_ai(
                        human_player=0
                    )

                    return

                elif event.key == pygame.K_2:
                    pygame.quit()

                    run_human_vs_ai(
                        human_player=1
                    )

                    return

                elif event.key == pygame.K_3:
                    running = False

        clock.tick(30)

    pygame.quit()


# ================================================================
# START PROGRAM
# ================================================================

if __name__ == "__main__":
    main_menu()
import random
from collections import deque

BOARD_SIZE = 8

ROAD = 0
BUILDING = 1
TRAFFIC = 2
ROADBLOCK = 3

EMPTY = "EMPTY"
MOVE = "MOVE"
BLOCK = "BLOCK"


class GameState:
    """
    Complete game state shared by both Minimax and MCTS.

    Both AIs use:
        get_legal_moves()
        apply_move()
        is_terminal()
        get_score()
        clone()
    """

    def __init__(self, seed=42):
        self.seed = seed
        self.rng = random.Random(seed)

        

        # Rider positions.
        self.positions = {
            0: (0, 0),                       # Rider A
            1: (BOARD_SIZE - 1, BOARD_SIZE - 1)  # Rider B
        }
        self.board = self._create_board()
        self.scores = [0, 0]

        # Number of turns/actions made by each player.
        self.player_turns = [0, 0]

        # Player 0 starts.
        self.current_player = 0

        # Maximum number of roadblocks per rider.
        self.roadblocks_left = [3, 3]

        # If a rider enters traffic, the next turn is skipped.
        self.traffic_skip = [0, 0]

        # One carried order at most.
        self.carried_order = [None, None]

        self.orders = []

        self.max_turns = 40
        self.target_score = 5

        self._spawn_orders()

    # ------------------------------------------------------------------
    # BOARD CREATION
    # ------------------------------------------------------------------

    def _create_board(self):
        """
        Create a reproducible city.

        0 = normal road
        1 = building
        2 = traffic jam
        3 = roadblock
        """

        board = [[ROAD for _ in range(BOARD_SIZE)]
                 for _ in range(BOARD_SIZE)]

        # Fixed buildings make the map easier to understand.
        buildings = {
            (0, 3), (0, 4),
            (1, 1), (1, 5),
            (2, 3),
            (3, 0), (3, 2), (3, 6),
            (4, 1), (4, 5),
            (5, 3),
            (6, 2), (6, 6),
            (7, 3), (7, 4)
        }

        for r, c in buildings:
            board[r][c] = BUILDING

        # Add reproducible traffic jams.
        possible = [
            (r, c)
            for r in range(BOARD_SIZE)
            for c in range(BOARD_SIZE)
            if board[r][c] == ROAD
            and (r, c) not in self.positions.values()
        ]

        self.rng.shuffle(possible)

        for cell in possible[:8]:
            board[cell[0]][cell[1]] = TRAFFIC

        # Make sure starting cells are roads.
        board[0][0] = ROAD
        board[7][7] = ROAD

        return board

    # ------------------------------------------------------------------
    # BASIC HELPERS
    # ------------------------------------------------------------------

    def inside(self, r, c):
        return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE

    def neighbors(self, pos):
        r, c = pos

        directions = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1)
        ]

        result = []

        for dr, dc in directions:
            nr = r + dr
            nc = c + dc

            if self.inside(nr, nc):
                result.append((nr, nc))

        return result

    def is_blocked(self, pos):
        r, c = pos
        return self.board[r][c] in (BUILDING, ROADBLOCK)

    def distance(self, start, goal):
        """
        Manhattan distance.
        """
        if goal is None:
            return 999

        return abs(start[0] - goal[0]) + abs(start[1] - goal[1])

    def bfs_distance(self, start, goal):
        """
        BFS shortest-path distance.

        Used by the Minimax heuristic.
        Roadblocks/buildings cannot be crossed.
        """

        if goal is None:
            return 999

        if start == goal:
            return 0

        queue = deque([(start, 0)])
        visited = {start}

        while queue:
            current, dist = queue.popleft()

            for nxt in self.neighbors(current):
                if nxt in visited:
                    continue

                if self.is_blocked(nxt):
                    continue

                if nxt == goal:
                    return dist + 1

                visited.add(nxt)
                queue.append((nxt, dist + 1))

        return 999

    # ------------------------------------------------------------------
    # ORDERS
    # ------------------------------------------------------------------

    def _spawn_orders(self):
        """
        Keep at most three active orders.
        """

        while len(self.orders) < 3:
            used = set()

            for order in self.orders:
                used.add(order["pickup"])
                used.add(order["dropoff"])

            used.update(self.positions.values())

            candidates = [
                (r, c)
                for r in range(BOARD_SIZE)
                for c in range(BOARD_SIZE)
                if self.board[r][c] in (ROAD, TRAFFIC)
                and (r, c) not in used
            ]

            if len(candidates) < 2:
                return

            pickup = self.rng.choice(candidates)

            remaining = [
                cell for cell in candidates
                if cell != pickup
            ]

            dropoff = self.rng.choice(remaining)

            self.orders.append({
                "pickup": pickup,
                "dropoff": dropoff
            })

    def _pickup_order(self, player):
        """
        Pick up an order when the rider reaches its pickup cell.
        """

        if self.carried_order[player] is not None:
            return None

        position = self.positions[player]

        for index, order in enumerate(self.orders):
            if order["pickup"] == position:
                self.carried_order[player] = {
                    "pickup": order["pickup"],
                    "dropoff": order["dropoff"]
                }

                self.orders.pop(index)

                return self.carried_order[player]

        return None

    def _deliver_order(self, player):
        """
        Deliver the currently carried order.
        """

        order = self.carried_order[player]

        if order is None:
            return False

        if self.positions[player] != order["dropoff"]:
            return False

        self.scores[player] += 1
        self.carried_order[player] = None

        self._spawn_orders()

        return True

    # ------------------------------------------------------------------
    # GAME ACTIONS
    # ------------------------------------------------------------------

    def get_legal_moves(self, player=None):
        """
        Return legal actions.

        Move:
            ("MOVE", row, col)

        Roadblock:
            ("BLOCK", row, col)

        If there are no possible actions, return [].
        """

        if player is None:
            player = self.current_player

        # Traffic jam causes one skipped turn.
        if self.traffic_skip[player] > 0:
            return []

        position = self.positions[player]

        moves = []

        # Normal movement.
        for nxt in self.neighbors(position):
            if self.is_blocked(nxt):
                continue

            # A rider cannot move into the other rider.
            other = 1 - player

            if nxt == self.positions[other]:
                continue

            moves.append((MOVE, nxt[0], nxt[1]))

        # Roadblock placement.
        if self.roadblocks_left[player] > 0:
            for nxt in self.neighbors(position):
                r, c = nxt

                # Only an empty normal road can become a roadblock.
                if self.board[r][c] != ROAD:
                    continue

                if nxt == self.positions[0] or nxt == self.positions[1]:
                    continue

                moves.append((BLOCK, r, c))

        return moves

    def apply_move(self, move):
        """
        Apply one action and switch to the other player.

        Returns a description of what happened.
        """

        player = self.current_player
        other = 1 - player

        # If traffic caused a skipped turn.
        if self.traffic_skip[player] > 0:
            self.traffic_skip[player] -= 1
            self.player_turns[player] += 1
            self.current_player = other

            return f"Rider {'A' if player == 0 else 'B'} skipped a turn because of traffic."

        legal = self.get_legal_moves(player)

        # No legal action means automatic skip.
        if not legal:
            self.player_turns[player] += 1
            self.current_player = other

            return f"Rider {'A' if player == 0 else 'B'} has no legal action and skips."

        if move not in legal:
            raise ValueError(f"Illegal move: {move}")

        action, r, c = move

        if action == MOVE:
            self.positions[player] = (r, c)

            message = (
                f"Rider {'A' if player == 0 else 'B'} "
                f"moved to ({r}, {c})."
            )

            # Traffic jam costs two moves:
            # current move + one skipped future turn.
            if self.board[r][c] == TRAFFIC:
                self.traffic_skip[player] = 1
                message += " Traffic jam! Next turn is skipped."

            picked = self._pickup_order(player)

            if picked is not None:
                message += (
                    f" Picked up order → dropoff {picked['dropoff']}."
                )

            delivered = self._deliver_order(player)

            if delivered:
                message += " Delivered! +1 point."

        elif action == BLOCK:
            self.board[r][c] = ROADBLOCK
            self.roadblocks_left[player] -= 1

            message = (
                f"Rider {'A' if player == 0 else 'B'} "
                f"placed a roadblock at ({r}, {c})."
            )

        self.player_turns[player] += 1

        self.current_player = other

        return message

    # ------------------------------------------------------------------
    # TERMINAL STATE
    # ------------------------------------------------------------------

    def is_terminal(self):
        if self.scores[0] >= self.target_score:
            return True

        if self.scores[1] >= self.target_score:
            return True

        if (
            self.player_turns[0] >= self.max_turns
            and self.player_turns[1] >= self.max_turns
        ):
            return True

        return False

    # ------------------------------------------------------------------
    # SCORE
    # ------------------------------------------------------------------

    def get_score(self, player):
        return self.scores[player]

    # ------------------------------------------------------------------
    # CLONE
    # ------------------------------------------------------------------

    def clone(self):
        """
        Create a completely independent copy.

        This is essential for Minimax and MCTS.
        """

        new_state = GameState.__new__(GameState)

        new_state.seed = self.seed
        new_state.rng = random.Random()

        # Copy RNG state.
        new_state.rng.setstate(self.rng.getstate())

        new_state.board = [row[:] for row in self.board]

        new_state.positions = self.positions.copy()
        new_state.scores = self.scores[:]
        new_state.player_turns = self.player_turns[:]
        new_state.current_player = self.current_player
        new_state.roadblocks_left = self.roadblocks_left[:]
        new_state.traffic_skip = self.traffic_skip[:]

        new_state.carried_order = [
            None if order is None else order.copy()
            for order in self.carried_order
        ]

        new_state.orders = [
            {
                "pickup": order["pickup"],
                "dropoff": order["dropoff"]
            }
            for order in self.orders
        ]

        new_state.max_turns = self.max_turns
        new_state.target_score = self.target_score

        return new_state

    # ------------------------------------------------------------------
    # DISPLAY HELPERS
    # ------------------------------------------------------------------

    def target_for(self, player):
        """
        Return the current target for a rider.

        If carrying an order:
            target = dropoff

        Otherwise:
            target = closest pickup.
        """

        if self.carried_order[player] is not None:
            return self.carried_order[player]["dropoff"]

        if not self.orders:
            return None

        position = self.positions[player]

        return min(
            self.orders,
            key=lambda order: self.bfs_distance(
                position,
                order["pickup"]
            )
        )["pickup"]

    def winner(self):
        if self.scores[0] > self.scores[1]:
            return 0

        if self.scores[1] > self.scores[0]:
            return 1

        return None

    def total_turns(self):
        return self.player_turns[0] + self.player_turns[1]
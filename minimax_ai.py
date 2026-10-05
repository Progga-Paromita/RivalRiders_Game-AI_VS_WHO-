import math


class MinimaxAI:
    """
    Depth-limited Minimax with Alpha-Beta pruning.
    """

    def __init__(self, player, depth=3):
        self.player = player
        self.depth = depth

        self.nodes_searched = 0
        self.last_thinking_time = 0.0

    def choose_move(self, state):
        import time

        start = time.perf_counter()

        self.nodes_searched = 0

        legal_moves = state.get_legal_moves(self.player)

        if not legal_moves:
            self.last_thinking_time = time.perf_counter() - start
            return None

        best_move = legal_moves[0]
        best_value = -math.inf

        alpha = -math.inf
        beta = math.inf

        for move in legal_moves:
            child = state.clone()
            child.current_player = self.player
            child.apply_move(move)

            value = self._minimax(
                child,
                self.depth - 1,
                alpha,
                beta,
                False
            )

            if value > best_value:
                best_value = value
                best_move = move

            alpha = max(alpha, best_value)

        self.last_thinking_time = time.perf_counter() - start

        return best_move

    def _minimax(self, state, depth, alpha, beta, maximizing):
        self.nodes_searched += 1

        if state.is_terminal() or depth <= 0:
            return self.evaluate(state)

        player = self.player
        opponent = 1 - player

        current = player if maximizing else opponent

        legal_moves = state.get_legal_moves(current)

        if not legal_moves:
            child = state.clone()
            child.current_player = current
            child.apply_move(None)

            return self._minimax(
                child,
                depth - 1,
                alpha,
                beta,
                not maximizing
            )

        if maximizing:
            value = -math.inf

            for move in legal_moves:
                child = state.clone()
                child.current_player = current
                child.apply_move(move)

                value = max(
                    value,
                    self._minimax(
                        child,
                        depth - 1,
                        alpha,
                        beta,
                        False
                    )
                )

                alpha = max(alpha, value)

                if alpha >= beta:
                    break

            return value

        else:
            value = math.inf

            for move in legal_moves:
                child = state.clone()
                child.current_player = current
                child.apply_move(move)

                value = min(
                    value,
                    self._minimax(
                        child,
                        depth - 1,
                        alpha,
                        beta,
                        True
                    )
                )

                beta = min(beta, value)

                if alpha >= beta:
                    break

            return value

    # ------------------------------------------------------------------
    # HEURISTIC
    # ------------------------------------------------------------------

    def evaluate(self, state):
        """
        Heuristic:

        score difference
        + bonus for being close to my target
        - penalty if opponent is closer to the same target
        """

        me = self.player
        opponent = 1 - me

        value = (
            state.get_score(me)
            - state.get_score(opponent)
        )

        my_target = state.target_for(me)

        if my_target is not None:
            my_distance = state.bfs_distance(
                state.positions[me],
                my_target
            )

            if my_distance < 999:
                value += 0.08 / (my_distance + 1)

        # Competition for the same target.
        if my_target is not None:
            opponent_distance = state.bfs_distance(
                state.positions[opponent],
                my_target
            )

            if opponent_distance < 999:
                value -= 0.05 / (opponent_distance + 1)

        # Slight advantage for having an order in hand.
        if state.carried_order[me] is not None:
            value += 0.12

        if state.carried_order[opponent] is not None:
            value -= 0.12

        return value
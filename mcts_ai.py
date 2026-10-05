import math
import random
import time


class MCTSNode:
    """
    One node of the Monte Carlo Search Tree.
    """

    def __init__(self, state, parent=None, move=None, root_player=0):
        self.state = state
        self.parent = parent
        self.move = move
        self.root_player = root_player

        self.children = []

        self.untried_moves = state.get_legal_moves(
            state.current_player
        )[:]

        self.visits = 0
        self.value = 0.0

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def best_child(self, exploration=math.sqrt(2)):
        """
        UCB1:

        exploitation + exploration

        value/visits
        +
        C * sqrt(ln(parent_visits) / visits)
        """

        best = None
        best_score = -math.inf

        for child in self.children:
            if child.visits == 0:
                score = math.inf
            else:
                exploitation = child.value / child.visits

                exploration_term = (
                    exploration
                    * math.sqrt(
                        math.log(self.visits)
                        / child.visits
                    )
                )

                score = exploitation + exploration_term

            if score > best_score:
                best_score = score
                best = child

        return best


class MCTS_AI:
    """
    Monte Carlo Tree Search AI.

    Default:
        300 simulations per move
    """

    def __init__(
        self,
        player,
        simulations=300,
        rollout_depth=15,
        seed=42
    ):
        self.player = player
        self.simulations = simulations
        self.rollout_depth = rollout_depth

        self.rng = random.Random(seed)

        self.last_thinking_time = 0.0

    def choose_move(self, state):
        start = time.perf_counter()

        legal_moves = state.get_legal_moves(self.player)

        if not legal_moves:
            self.last_thinking_time = time.perf_counter() - start
            return None

        root_state = state.clone()
        root_state.current_player = self.player

        root = MCTSNode(
            root_state,
            root_player=self.player
        )

        for _ in range(self.simulations):
            # ----------------------------------------------------------
            # 1. SELECTION
            # ----------------------------------------------------------

            node = root

            while (
                not node.state.is_terminal()
                and node.is_fully_expanded()
                and node.children
            ):
                node = node.best_child()

            # ----------------------------------------------------------
            # 2. EXPANSION
            # ----------------------------------------------------------

            if (
                not node.state.is_terminal()
                and node.untried_moves
            ):
                move_index = self.rng.randrange(
                    len(node.untried_moves)
                )

                move = node.untried_moves.pop(move_index)

                child_state = node.state.clone()

                child_state.current_player = (
                    node.state.current_player
                )

                child_state.apply_move(move)

                child = MCTSNode(
                    child_state,
                    parent=node,
                    move=move,
                    root_player=self.player
                )

                node.children.append(child)
                node = child

            # ----------------------------------------------------------
            # 3. SIMULATION / ROLLOUT
            # ----------------------------------------------------------

            result = self._rollout(node.state)

            # ----------------------------------------------------------
            # 4. BACKPROPAGATION
            # ----------------------------------------------------------

            while node is not None:
                node.visits += 1
                node.value += result
                node = node.parent

        # Choose the most visited action.
        if not root.children:
            best_move = legal_moves[0]
        else:
            best_child = max(
                root.children,
                key=lambda child: child.visits
            )

            best_move = best_child.move

        self.last_thinking_time = time.perf_counter() - start

        return best_move

    def _rollout(self, state):
        """
        Randomly play from the current state.

        Limited by rollout_depth so MCTS cannot run forever.
        """

        simulation = state.clone()

        for _ in range(self.rollout_depth):
            if simulation.is_terminal():
                break

            player = simulation.current_player

            legal_moves = simulation.get_legal_moves(player)

            if not legal_moves:
                simulation.player_turns[player] += 1
                simulation.current_player = 1 - player
                continue

            move = self.rng.choice(legal_moves)

            simulation.apply_move(move)

        my_score = simulation.get_score(self.player)
        opponent_score = simulation.get_score(1 - self.player)

        if my_score > opponent_score:
            return 1.0

        if my_score < opponent_score:
            return -1.0

        # Small score difference signal.
        return 0.1 * (my_score - opponent_score)
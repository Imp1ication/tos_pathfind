import random
import copy
from basic import Move
from board_optimize import TosBoard
import config as cfg


class TosPath:
    def __init__(self, steps=0, start_pos=(0, 0), path=[]):
        self.steps = steps
        self.start_pos = start_pos
        self.path = path

    def init_from_random(self, steps, start_pos=None):
        self.steps = steps

        if start_pos is not None:
            self.start_pos = start_pos
        else:
            self.start_pos = (
                random.randint(0, cfg.BOARD_PARAMS.rows - 1),
                random.randint(0, cfg.BOARD_PARAMS.cols - 1),
            )

        # Generate path (Gamestates)
        self.path = [random.randint(0, len(Move) - 1 - 1) for _ in range(steps)]
        return

    def run_path(self, tos_board):
        board = copy.deepcopy(tos_board)
        move_steps = []

        current_pos = self.start_pos
        prev_pos = self.start_pos

        for i in range(self.steps):
            successor_list = board.get_successor_list(current_pos, prev_pos)
            state = self.path[i] % len(successor_list)
            move = successor_list[state]
            move_steps.append(move)

            board.move_stone(current_pos, move)
            prev_pos = current_pos
            current_pos = tuple(sum(x) for x in zip(current_pos, move.value))

        return board, move_steps


if __name__ == "__main__":
    board = TosBoard()
    board.init_from_file(cfg.INPUT_FILE_NAME)

    path = TosPath()
    path.init_from_random(15, (0, 0))
    print(path.path)

    print(board)
    new_board, move_steps = path.run_path(board)
    print(new_board)

import random
import copy
from basic import Move
from board_optimize import TosBoard
import config as cfg


class TosPath:
    def __init__(self, steps=cfg.PATH_PARAMS.max_steps, start_pos=(0, 0), path=[]):
        self.steps = steps
        self.start_pos = start_pos
        self.path = path

    def init_from_random(self, steps=None, start_pos=None):
        if steps is None:
            self.steps = random.randint(
                cfg.PATH_PARAMS.max_steps // 2, cfg.PATH_PARAMS.max_steps
            )
        else:
            self.steps = steps

        if start_pos is None:
            self.start_pos = (
                random.randint(0, cfg.BOARD_PARAMS.rows - 1),
                random.randint(0, cfg.BOARD_PARAMS.cols - 1),
            )
        else:
            self.start_pos = start_pos

        # Generate path (Gamestates)
        # self.path = [random.randint(0, len(Move) - 1 - 1) for _ in range(self.steps)]
        self.path = [random.uniform(0, 1) for _ in range(self.steps)]
        return

    def extract_sub_path(self, left, right):
        if not (0 <= left <= right < self.steps):
            print("Error(extract_sub_path): Invalid range.")
            return None

        return self.path[left : (right + 1)]

    def run_path(self, tos_board):
        board = copy.deepcopy(tos_board)
        move_steps = []

        current_pos = self.start_pos
        prev_pos = self.start_pos

        for i in range(self.steps):
            successor_list = board.get_successor_list(current_pos, prev_pos)
            num_successors = len(successor_list)
            state = int(self.path[i] * num_successors) % num_successors

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

import random
import copy
from sre_constants import JUMP
from basic import Move, StoneType, Runestone
from board_optimize import TosBoard


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
                random.randint(0, TosBoard.BOARD_ROWS - 1),
                random.randint(0, TosBoard.BOARD_COLS - 1),
            )

        # Generate path (Gamestates)
        self.path = [random.randint(0, len(Move) - 1 - 1) for _ in range(steps)]
        return

    def run_path(self, tos_board):
        board = copy.deepcopy(tos_board)

        current_pos = self.start_pos
        prev_pos = self.start_pos

        for i in range(self.steps):
            successor_list = board.get_successor_list(current_pos, prev_pos)
            state = self.path[i] % len(successor_list)
            move = successor_list[state]

            board.move_stone(current_pos, move)
            prev_pos = current_pos
            current_pos = (
                prev_pos[0] + move.value[0],
                prev_pos[1] + move.value[1],
            )

        return board


if __name__ == "__main__":
    board = TosBoard()
    board.init_from_file("input.txt")

    path = TosPath()
    path.init_from_random(5, (0, 0))
    print(path.path)

    path.run_path(board)

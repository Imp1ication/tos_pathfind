import random
from basic import Move, StoneType, Runestone
from board_optimize import TosBoard


class Path:
    def __init__(self, steps=0, start_pos=(0, 0), path=[]):
        self.steps = steps
        self.start_pos = start_pos
        self.path = path

    def init_from_random(self, steps):
        self.steps = steps
        self.start_pos = (
            random.randint(0, TosBoard.BOARD_ROWS - 1),
            random.randint(0, TosBoard.BOARD_COLS - 1),
        )

        return


if __name__ == "__main__":
    print("hi")

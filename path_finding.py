from tos_board import TosBoard
from tos_path import TosPath
import config as cfg


def ga_find_path(_initBoard, steps):
    # -- Initialize population -- #
    population = []
    fitness = []

    for _ in range(cfg.PATH_PARAMS.population_size):
        path = TosPath()
        path.init_from_random(steps)
        population.append(path)

    # -- Evaluate population -- #

    return


if __name__ == "__main__":
    init_board = TosBoard()
    target_board = TosBoard()

    init_board.init_from_file(cfg.INPUT_FILE_NAME)
    target_board.init_from_file("input2.txt")

    print("Init Board:")
    print(init_board)
    print()
    print("Target Board:")
    print(target_board)

    ga_find_path(init_board, 5)

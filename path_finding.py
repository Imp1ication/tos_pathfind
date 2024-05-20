import multiprocessing
from functools import partial

from tos_board import TosBoard
from tos_path import TosPath
import config as cfg


def parallel_eval_fitness(path, init_board, target_board):
    final_board, _ = path.run_path(init_board)

    diff_score = final_board.calc_board_diff(target_board)
    diff_score = diff_score / (cfg.BOARD_PARAMS.rows * cfg.BOARD_PARAMS.cols)

    step_score = path.steps / cfg.PATH_PARAMS.max_steps

    fitness = cfg.PATH_PARAMS.diff_weight + cfg.PATH_PARAMS.step_weight
    fitness -= (
        diff_score * cfg.PATH_PARAMS.diff_weight
        + step_score * cfg.PATH_PARAMS.step_weight
    )

    return fitness


def parallel_eval_pop_fitness(population, init_board, target_board):
    with multiprocessing.Pool() as pool:
        fitness_scores = pool.map(
            partial(
                parallel_eval_fitness, init_board=init_board, target_board=target_board
            ),
            population,
        )
    return fitness_scores


def ga_find_path(init_board, target_board):
    # -- Initialize population -- #
    population = []
    fitness = []

    for _ in range(cfg.PATH_PARAMS.population_size):
        path = TosPath()
        path.init_from_random()
        population.append(path)

    # -- Evaluate population -- #
    fitness = parallel_eval_pop_fitness(population, init_board, target_board)

    return


if __name__ == "__main__":
    init_board = TosBoard()
    target_board = TosBoard()

    # init_board.init_from_file(cfg.INPUT_FILE_NAME)
    init_board.init_from_file(cfg.INPUT_FILE_NAME)
    target_board.init_from_file("input2.txt")

    print("Init Board:")
    print(init_board)
    print()
    print("Target Board:")
    print(target_board)
    print()

    path = TosPath(steps=2, path=[0, 1])

    final, _ = path.run_path(init_board)
    print("Final Board:")
    print(final)

    score = parallel_eval_fitness(path, init_board, target_board)
    print("Score: ", score)

    # ga_find_path(init_board, 5)

import copy
import time
import random
import multiprocessing
from functools import partial
from statistics import mean, stdev

from basic import Move
from tos_board import TosBoard
from tos_path import TosPath
import config as cfg

import board_optimize as bo


def two_tournament_selection(population, fitness):
    p1, p2 = random.sample(range(len(population)), 2)

    return (
        copy.deepcopy(population[p1])
        if fitness[p1] > fitness[p2]
        else copy.deepcopy(population[p2])
    )


def cut_splice_crossover(parent1, parent2, cross_point):
    child1_path = parent1.extract_sub_path(0, cross_point - 1)
    child1_path += parent2.extract_sub_path(cross_point, parent2.steps - 1)

    child2_path = parent2.extract_sub_path(0, cross_point - 1)
    child2_path += parent1.extract_sub_path(cross_point, parent1.steps - 1)

    child1 = TosPath(
        steps=len(child1_path), start_pos=parent1.start_pos, path=child1_path
    )
    child2 = TosPath(
        steps=len(child2_path), start_pos=parent2.start_pos, path=child2_path
    )
    return child1, child2


def single_point_mutation(path, mutate_point):
    for p in range(mutate_point, path.steps - 1):
        path.path[p] = random.uniform(0, 1)
    return path


def parallel_eval_fitness(path, init_board, target_board):
    final_board, _ = path.run_path(init_board)

    # diff = target_board.calc_board_diff(final_board) / 30
    # rm_stones, combo, final_state = final_board.eliminate_stones()
    # score = final_board.calc_score(rm_stones, combo) - final_state.calc_stone_density()
    # return score

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


def parallel_mutate_children(path, mutate_rate):
    if random.random() < mutate_rate:
        mutate_point = random.randint(0, path.steps - 1)
        path = single_point_mutation(path, mutate_point)

    return path


def parallel_mutate_child(child, mutate_rate):
    with multiprocessing.Pool() as pool:
        mutated_child = pool.map(
            partial(parallel_mutate_children, mutate_rate=mutate_rate), child
        )
    return mutated_child


def ga_find_path(init_board, target_board):
    # -- Initialize population -- #
    population = []
    fitness = []

    for row in range(0, cfg.BOARD_PARAMS.rows):
        for col in range(0, cfg.BOARD_PARAMS.cols):
            for _ in range(cfg.PATH_PARAMS.population_size):
                path = TosPath()
                path.init_from_random(start_pos=(row, col))
                population.append(path)

    # for _ in range(cfg.PATH_PARAMS.population_size):
    #     path = TosPath()
    #     path.init_from_random()
    #     population.append(path)

    # -- Evaluate population -- #
    fitness = parallel_eval_pop_fitness(population, init_board, target_board)

    # -- Evolution -- #
    stagnation_count = 0
    prev_max_fitness = 0

    for gen in range(cfg.PATH_PARAMS.max_generation):
        # print("Generation: ", gen)
        child = []
        child_fitness = []

        for _ in range(int(cfg.PATH_PARAMS.population_size / 2)):
            # -- Matting Selection -- #
            parent1 = two_tournament_selection(population, fitness)
            parent2 = two_tournament_selection(population, fitness)

            # -- Crossover -- #
            cross_point = random.randint(1, min(parent1.steps, parent2.steps) - 1)
            child1, child2 = cut_splice_crossover(parent1, parent2, cross_point)

            child.append(child1)
            child.append(child2)

        # -- Mutation -- #
        child = parallel_mutate_child(child, cfg.PATH_PARAMS.mutation_rate)

        # -- Evaluate child -- #
        child_fitness = parallel_eval_pop_fitness(child, init_board, target_board)

        # -- Selection -- #
        combined = list(zip(population + child, fitness + child_fitness))
        sorted_combined = sorted(combined, key=lambda x: x[1], reverse=True)

        population = [x[0] for x in sorted_combined[: cfg.PATH_PARAMS.population_size]]
        fitness = [x[1] for x in sorted_combined[: cfg.PATH_PARAMS.population_size]]

        max_fitness = round(max(fitness), 3)
        min_fitness = round(min(fitness), 3)
        mean_fitness = round(mean(fitness), 3)
        std_dev_fitness = round(stdev(fitness), 3)
        print(
            gen,
            ": ",
            max_fitness,
            "/",
            mean_fitness,
            "/",
            min_fitness,
            "/",
            std_dev_fitness,
        )

        # if std_dev_fitness <= cfg.PATH_PARAMS.stop_threshold:
        #     print("Stopping early: Converged due to low diversity.")
        #     break

        # if max_fitness == prev_max_fitness:
        #     stagnation_count += 1
        #     if stagnation_count >= cfg.PATH_PARAMS.max_stagnation:
        #         print("Stopping early: Converged due to stagnation.")
        #         break
        # else:
        #     stagnation_count = 0
        #     prev_max_fitness = max_fitness

    return population[0], fitness[0]


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

    start_time = time.time()
    best_indv, best_fit = ga_find_path(init_board, target_board)
    elapsed_time = time.time() - start_time

    final_board, best_path = best_indv.run_path(init_board)

    print("Final Board:")
    print(final_board)

    print("Best Path: ", best_fit)
    print("Start Position: ", best_indv.start_pos)
    print("Best Path steps: ", best_indv.steps)
    # for move in best_path:
    # print(move)

    print("Runtime: ", elapsed_time)

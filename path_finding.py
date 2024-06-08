import os
import copy
import time
import random
import multiprocessing
from functools import partial
from statistics import mean, stdev

from tos_board import TosBoard
from tos_path import TosPath

import config as cfg
from config import PATH_PARAMS as PP


def two_tournament_selection(population, fitness):
    p1, p2 = random.sample(range(len(population)), 2)

    return (
        copy.deepcopy(population[p1])
        if fitness[p1] < fitness[p2]
        else copy.deepcopy(population[p2])
    )


def cut_splice_crossover(parent1, parent2, cross_point1, cross_point2):
    child1_path = parent1.extract_sub_path(0, cross_point1 - 1)
    child1_path += parent2.extract_sub_path(cross_point2, parent2.steps - 1)
    if len(child1_path) > PP.max_steps:
        child1_path = child1_path[: PP.max_steps]

    child2_path = parent2.extract_sub_path(0, cross_point2 - 1)
    child2_path += parent1.extract_sub_path(cross_point1, parent1.steps - 1)
    if len(child2_path) > PP.max_steps:
        child2_path = child2_path[: PP.max_steps]

    child1 = TosPath(
        steps=len(child1_path), start_pos=parent1.start_pos, path=child1_path
    )
    child2 = TosPath(
        steps=len(child2_path), start_pos=parent2.start_pos, path=child2_path
    )
    return child1, child2


def segment_mutation(path, mutate_point):
    for i in range(mutate_point, path.steps):
        path.path[i] = random.uniform(0, 1)
    return path


def reset_population(population, fitness):
    combined = list(zip(population, fitness))
    combined = sorted(combined, key=lambda x: x[1], reverse=True)
    population = [x[0] for x in combined]

    index = 0
    for row in range(0, cfg.BOARD_PARAMS.rows):
        for col in range(0, cfg.BOARD_PARAMS.cols):
            for _ in range(int(PP.pos_size / 2)):
                population[index].init_from_random(start_pos=(row, col))
                index += 1

    return population


def parallel_eval_fitness(path, init_board, target_board):
    final_board, _ = path.run_path(init_board)

    dist_score = final_board.calc_board_dist(target_board)
    step_score = path.steps / PP.max_steps

    fitness = dist_score * PP.dist_weight + step_score * PP.step_weight

    return fitness


def parallel_eval_pop_fitness(population, init_board, target_board):
    with multiprocessing.Pool(processes=cfg.GA_CORES) as pool:
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
        path = segment_mutation(path, mutate_point)
        # path = single_point_mutation(path, mutate_point)

    return path


def parallel_mutate_child(child, mutate_rate):
    with multiprocessing.Pool(processes=cfg.GA_CORES) as pool:
        mutated_child = pool.map(
            partial(parallel_mutate_children, mutate_rate=mutate_rate), child
        )
    return mutated_child


def ga_find_path(init_board, target_board, log_file_name):
    # -- Initialize population -- #
    population = []
    fitness = []

    for row in range(0, cfg.BOARD_PARAMS.rows):
        for col in range(0, cfg.BOARD_PARAMS.cols):
            for _ in range(PP.pos_size):
                path = TosPath()
                path.init_from_random(start_pos=(row, col))
                population.append(path)

    # -- Evaluate population -- #
    fitness = parallel_eval_pop_fitness(population, init_board, target_board)

    # -- Evolution -- #
    stagnation_count = 0
    prev_min_fitness = 0
    prev_max_fitness = 1

    log_file = open(log_file_name, "w")
    final_log_string = ""

    for gen in range(PP.max_generation):
        # print("Generation: ", gen)
        child = []
        child_fitness = []

        for _ in range(int(PP.population_size / 2)):
            # -- Matting Selection -- #
            parent1 = two_tournament_selection(population, fitness)
            parent2 = two_tournament_selection(population, fitness)

            # -- Crossover -- #
            cross_point1 = random.randint(1, parent1.steps - 1)
            cross_point2 = random.randint(1, parent2.steps - 1)
            child1, child2 = cut_splice_crossover(
                parent1, parent2, cross_point1, cross_point2
            )

            child.append(child1)
            child.append(child2)

        # -- Mutation -- #
        child = parallel_mutate_child(child, PP.mutation_rate)

        # -- Evaluate child -- #
        child_fitness = parallel_eval_pop_fitness(child, init_board, target_board)

        # -- Selection -- #
        combined = list(zip(population + child, fitness + child_fitness))
        sorted_combined = sorted(combined, key=lambda x: x[1], reverse=False)

        population = [x[0] for x in sorted_combined[: PP.population_size]]
        fitness = [x[1] for x in sorted_combined[: PP.population_size]]

        max_fitness = max(fitness)
        min_fitness = min(fitness)
        mean_fitness = mean(fitness)
        std_dev_fitness = stdev(fitness)
        if gen % 100 == 0:
            print(
                gen,
                ": ",
                round(max_fitness, 3),
                "/",
                round(mean_fitness, 3),
                "/",
                round(min_fitness, 3),
                "/",
                std_dev_fitness,
            )

        log_file.write(
            f"{max_fitness} {mean_fitness} {min_fitness} {std_dev_fitness}\n"
        )
        final_log_string = (
            f"{max_fitness} {mean_fitness} {min_fitness} {std_dev_fitness} "
        )

        if round(min_fitness, 3) == round(prev_min_fitness, 3) and round(
            max_fitness, 3
        ) == round(prev_max_fitness, 3):
            stagnation_count += 1
            if stagnation_count >= PP.max_stagnation:
                if min_fitness == 0:
                    print("Stopping early: Find Path.")
                    break

                print("Reset population: Converged due to stagnation.")
                population = reset_population(population, fitness)
                fitness = parallel_eval_pop_fitness(
                    population, init_board, target_board
                )
                stagnation_count = 0
        else:
            stagnation_count = 0
            prev_min_fitness = min_fitness
            prev_max_fitness = max_fitness

        if std_dev_fitness <= PP.stop_threshold:
            print("Stopping early: Converged due to low diversity.")
            break

    log_file.close()
    return population[0], fitness[0], final_log_string


def mutate_exper():
    LOG_DIR = "./pf_log/"
    LOG_RESULT = "./pf_log/result/"
    input_files = os.listdir(cfg.INPUT_FILE_DIR)

    for i in range(1, 10, 2):
        PP.mutation_rate = round(i * 0.1, 1)
        for file in input_files:
            if not file.endswith(".txt"):
                continue

            for _ in range(20):
                log_file_name = f"{file.split('.')[0]}_{PP.mutation_rate}.txt"
                log_file_name = os.path.join(LOG_DIR, log_file_name)

                result_file_name = f"{file.split('.')[0]}_{PP.mutation_rate}.txt"
                result_file_name = os.path.join(LOG_RESULT, result_file_name)

                initBoard = TosBoard()
                initBoard.init_from_file(cfg.INPUT_FILE_DIR + file)

                targetBoard = TosBoard()
                targetBoard.init_from_file("input2.txt")

                start_time = time.time()
                _, best_fit, result_log_string = ga_find_path(
                    initBoard, targetBoard, log_file_name
                )
                elapsed_time = time.time() - start_time

                result_log_string += f"{elapsed_time}\n"

                log_file_name = f"{file.split('.')[0]}_{PP.mutation_rate}.txt"
                log_file_name = os.path.join(LOG_DIR, log_file_name)

                result_file_name = f"{file.split('.')[0]}_{PP.mutation_rate}.txt"
                result_file_name = os.path.join(LOG_RESULT, result_file_name)

                with open(log_file_name, "a") as log_file:
                    log_file.write(f"{elapsed_time}\n{best_fit}\n\n")

                with open(result_file_name, "a") as log_file:
                    log_file.write(result_log_string)

    return


if __name__ == "__main__":
    mutate_exper()
    # init_board = TosBoard()
    # target_board = TosBoard()

    # # init_board.init_from_file(cfg.INPUT_FILE_NAME)
    # init_board.init_from_file(cfg.INPUT_FILE_NAME)
    # target_board.init_from_file("input2.txt")

    # print("Init Board:")
    # print(init_board)
    # print()
    # print("Target Board:")
    # print(target_board)
    # print()

    # start_time = time.time()
    # best_indv, best_fit, _ = ga_find_path(init_board, target_board, "test.txt")
    # elapsed_time = time.time() - start_time

    # final_board, best_path = best_indv.run_path(init_board)

    # print("Final Board:")
    # print(final_board)

    # print("Best Path: ", best_fit)
    # print("Start Position: ", best_indv.start_pos)
    # print("Best Path steps: ", best_indv.steps)
    # for move in best_path:
    # print(move)

    # print("Runtime: ", elapsed_time)

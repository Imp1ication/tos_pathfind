import copy
import time
import random
import multiprocessing
from functools import partial
from statistics import mean, stdev

from tos_board import TosBoard
from basic import StoneType, Runestone
import config as cfg


def random_select_rects(rows, cols):
    cp1_x, cp1_y = (random.randint(0, rows - 1), random.randint(0, cols - 1))
    cp2_x, cp2_y = (random.randint(0, rows - 1), random.randint(0, cols - 1))

    cross_point1 = (min(cp1_x, cp2_x), min(cp1_y, cp2_y))
    cross_point2 = (max(cp1_x, cp2_x), max(cp1_y, cp2_y))

    return cross_point1, cross_point2


def two_tournament_selection(population, fitness):
    p1, p2 = random.sample(range(len(population)), 2)

    return (
        copy.deepcopy(population[p1])
        if fitness[p1] > fitness[p2]
        else copy.deepcopy(population[p2])
    )


def linear_order_crossover(parent1, parent2, cross_point1, cross_point2):
    child1 = TosBoard()
    child2 = TosBoard()

    sub_board1 = parent1.extract_sub_board(cross_point1, cross_point2)
    sub_board2 = parent2.extract_sub_board(cross_point1, cross_point2)

    sb1_stone_counts = sub_board1.count_stones_types()
    sb2_stone_counts = sub_board2.count_stones_types()

    fill_stones1 = []
    fill_stones2 = []
    for row in range(parent1.numOfRows):
        for col in range(parent1.numOfCols):
            stone_type = parent1.runestones[row][col].type
            if sb2_stone_counts.get(stone_type, 0) > 0:
                sb2_stone_counts[stone_type] -= 1
            else:
                fill_stones1.append(Runestone(stone_type))

            stone_type = parent2.runestones[row][col].type
            if sb1_stone_counts.get(stone_type, 0) > 0:
                sb1_stone_counts[stone_type] -= 1
            else:
                fill_stones2.append(Runestone(stone_type))

    # fill sub board
    for row in range(cross_point1[0], cross_point2[0] + 1):
        for col in range(cross_point1[1], cross_point2[1] + 1):
            child1.runestones[row][col] = parent2.runestones[row][col]
            child2.runestones[row][col] = parent1.runestones[row][col]

    # fill the rest of the board
    for row in range(child1.numOfRows):
        for col in range(child1.numOfCols):
            if child1.runestones[row][col].type is StoneType.NONE:
                child1.runestones[row][col] = fill_stones1.pop(0)

            if child2.runestones[row][col].type is StoneType.NONE:
                child2.runestones[row][col] = fill_stones2.pop(0)

    return child1, child2


def mutate_board(board, mutate_point1, mutate_point2, right_shift, down_shift):
    new_board = copy.deepcopy(board)
    sub_board = board.extract_sub_board(mutate_point1, mutate_point2)

    # right shift sub board
    for row in range(mutate_point1[0], mutate_point2[0] + 1):
        new_row = [Runestone() for _ in range(new_board.numOfCols)]
        rest_row = [
            new_board.runestones[row][col]
            for col in range(new_board.numOfCols)
            if not (mutate_point1[1] <= col <= mutate_point2[1])
        ]

        # fill the sub board
        for col in range(sub_board.numOfCols):
            new_row[
                (mutate_point1[1] + col + right_shift) % board.numOfCols
            ] = sub_board.runestones[row - mutate_point1[0]][col]

        # fill the rest of the board
        for col in range(new_board.numOfCols):
            if new_row[col].type is StoneType.NONE:
                new_row[col] = rest_row.pop(0)

        new_board.runestones[row] = new_row

    # down shift
    shift_col1 = mutate_point1[1] + right_shift
    shift_col2 = mutate_point2[1] + right_shift

    for col in range(shift_col1, shift_col2 + 1):
        s_col = col % new_board.numOfCols
        new_col = [Runestone() for _ in range(new_board.numOfRows)]
        sub_col = []
        rest_col = []

        for row in range(new_board.numOfRows):
            if mutate_point1[0] <= row <= mutate_point2[0]:
                sub_col.append(new_board.runestones[row][s_col])
            else:
                rest_col.append(new_board.runestones[row][s_col])

        # fill the sub board
        for row in range(sub_board.numOfRows):
            new_col[
                (mutate_point1[0] + row + down_shift) % board.numOfRows
            ] = sub_col.pop(0)

        # fill the rest of the board
        for row in range(new_board.numOfRows):
            if new_col[row].type is StoneType.NONE:
                new_col[row] = rest_col.pop(0)

        # fill the new board
        for row in range(new_board.numOfRows):
            new_board.runestones[row][s_col] = new_col[row]

    return new_board


def parallel_eval_fitness(board, _initBoard):
    diff = board.calc_board_diff(_initBoard)
    rm_stones, combo, final_state = board.eliminate_stones()

    score = board.calc_score(rm_stones, combo) - final_state.calc_stone_density() - diff
    return score


def parallel_eval_pop_fitness(population, _initBoard):
    with multiprocessing.Pool() as pool:
        fitness_scores = pool.map(
            partial(parallel_eval_fitness, _initBoard=_initBoard), population
        )
    return fitness_scores


def parallel_mutate_children(board, mutate_rate):
    if random.random() < mutate_rate:
        mutate_point1, mutate_point2 = random_select_rects(
            board.numOfRows, board.numOfCols
        )
        right_shift = random.randint(0, board.numOfCols - 1)
        down_shift = random.randint((0 if right_shift > 0 else 1), board.numOfRows - 1)
        board = mutate_board(
            board, mutate_point1, mutate_point2, right_shift, down_shift
        )
    return board


def parallel_mutate_child(child, mutate_rate):
    with multiprocessing.Pool() as pool:
        mutated_child = pool.map(
            partial(parallel_mutate_children, mutate_rate=mutate_rate), child
        )
    return mutated_child


def ga_optimize_board(_initBoard):
    # -- Initialize population -- #
    population = []
    fitness = []

    population.append(copy.deepcopy(_initBoard))
    for _ in range(cfg.BOARD_PARAMS.population_size - 1):
        population.append(_initBoard.shuffle_stones())

    # -- Evaluate population -- #
    fitness = parallel_eval_pop_fitness(population, _initBoard)

    # -- Evolution -- #
    stagnation_count = 0
    prev_max_fitness = 0

    for gen in range(cfg.BOARD_PARAMS.max_generation):
        # print("Generation: ", gen)
        child = []
        child_fitness = []

        for _ in range(int(cfg.BOARD_PARAMS.population_size / 2)):
            # -- Matting Selection -- #
            parent1 = two_tournament_selection(population, fitness)
            parent2 = two_tournament_selection(population, fitness)

            # -- Crossover -- #
            cross_point1, cross_point2 = random_select_rects(
                parent1.numOfRows, parent1.numOfCols
            )

            child1, child2 = linear_order_crossover(
                parent1, parent2, cross_point1, cross_point2
            )

            child.append(child1)
            child.append(child2)

        # -- Mutation -- #
        child = parallel_mutate_child(child, cfg.BOARD_PARAMS.mutation_rate)

        # -- Evaluate child -- #
        child_fitness = parallel_eval_pop_fitness(child, _initBoard)

        # -- Selection -- #
        combined = list(zip(population + child, fitness + child_fitness))
        sorted_combined = sorted(combined, key=lambda x: x[1], reverse=True)

        population = [x[0] for x in sorted_combined[: cfg.BOARD_PARAMS.population_size]]
        fitness = [x[1] for x in sorted_combined[: cfg.BOARD_PARAMS.population_size]]

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

        if std_dev_fitness <= cfg.BOARD_PARAMS.stop_threshold:
            print("Stopping early: Converged due to low diversity.")
            break

        if max_fitness == prev_max_fitness:
            stagnation_count += 1
            if stagnation_count >= cfg.BOARD_PARAMS.max_stagnation:
                print("Stopping early: Converged due to stagnation.")
                break
        else:
            stagnation_count = 0
            prev_max_fitness = max_fitness

    return population[0], fitness[0]


if __name__ == "__main__":
    initBoard = TosBoard()
    initBoard.init_from_file(cfg.INPUT_FILE_NAME)
    # initBoard.init_from_random()

    rm_stones, combo, final_state = initBoard.eliminate_stones()
    score = initBoard.calc_score(rm_stones, combo) - final_state.calc_stone_density()

    print("Init Board: ", score)
    print(initBoard)

    start_time = time.time()
    best_indv, best_fit = ga_optimize_board(initBoard)
    elapsed_time = time.time() - start_time

    print("Best Board: ", best_fit)
    print(best_indv)

    print("Runtime: ", elapsed_time)

    # search_board(initBoard)

from board import TosBoard


def search_board(_initBoard):
    # Constants
    POPULATION_SIZE = 5

    # Initialize population
    population = []

    for i in range(POPULATION_SIZE):
        population.append(_initBoard.shuffle_stones())

    # Evaluate population
    fitness = []

    for i in range(POPULATION_SIZE):
        rm_stones, combo, final_state = population[i].eliminate_stones()

        score = (
            population[i].calc_score(rm_stones, combo)
            + final_state.calc_stone_density()
        )
        fitness.append(score)

    # Selection

    # for i in range(POPULATION_SIZE):
    #     print("Population: ", i)
    #     print(population[i])
    #     print(fitness[i])


if __name__ == "__main__":
    # Initialize board
    initBoard = TosBoard()
    initBoard.init_from_file("input.txt")

    search_board(initBoard)

from types import SimpleNamespace


# random initizlized if inputFileName = None
INPUT_FILE_NAME = "./input.txt"

BOARD_PARAMS = SimpleNamespace(
    # -- Board -- #
    rows=5,
    cols=6,
    # -- Genetic Algorithm -- #
    max_generation=200,
    population_size=500,
    mutation_rate=0.6,
    max_stagnation=65,
    stop_threshold=0.1,
)

PATH_PARAMS = SimpleNamespace(
    # -- Path -- #
    max_steps=5,
    # -- Genetic Algorithm -- #
    max_generation=1,
    pupulation_size=5,
)

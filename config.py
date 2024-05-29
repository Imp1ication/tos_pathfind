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
    max_steps=500,
    diff_weight=10.0,
    step_weight=1.0,
    # -- Genetic Algorithm -- #
    max_generation=500,
    population_size=500,
    mutation_rate=0.9,
    max_stagnation=65,
    stop_threshold=0.1,
)

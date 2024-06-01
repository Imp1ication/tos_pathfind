from types import SimpleNamespace


# random initizlized if inputFileName = None
INPUT_FILE_DIR = "./input/"
INPUT_FILE_NAME = INPUT_FILE_DIR + "board15.txt"

BOARD_PARAMS = SimpleNamespace(
    # -- Board -- #
    rows=5,
    cols=6,
    # -- Genetic Algorithm -- #
    max_generation=200,
    population_size=500,
    mutation_rate=0.6,
    max_stagnation=60,
    stop_threshold=0.0001,
    # -- Fitness weight -- #
    score_weight=1.0,
    dist_weight=0.2,
    density_weight=0.2,
)

PATH_PARAMS = SimpleNamespace(
    # -- Path -- #
    max_steps=500,
    # -- Genetic Algorithm -- #
    max_generation=200,
    pos_size=100,
    population_size=3000,  # pos_size * 30
    mutation_rate=0.7,
    max_stagnation=65,
    stop_threshold=0.001,
    # -- Fitness weight -- #
    dist_weight=0.9,
    step_weight=0,
)

from types import SimpleNamespace

# file paths
INPUT_FILE_DIR = "./input/"
INPUT_FILE_NAME = INPUT_FILE_DIR + "board15.txt"

LOG_FILE_DIR = "./log/"

BO_LOG_DIR = LOG_FILE_DIR + "bo/"
BO_RESULT_DIR = BO_LOG_DIR + "result/"

PF_LOG_DIR = LOG_FILE_DIR + "pf/"
PF_RESULT_DIR = PF_LOG_DIR + "result/"


# parallel parameters
GA_CORES = 20


GA_FULL_RUNS = 10

BOARD_PARAMS = SimpleNamespace(
    # -- Board -- #
    rows=5,
    cols=6,
    # -- Genetic Algorithm -- #
    max_generation=200,
    population_size=500,
    mutation_rate=0.5,
    max_stagnation=60,
    stop_threshold=0.0001,
    # -- Fitness weight -- #
    score_weight=1.0,
    dist_weight=0.2,
    density_weight=0.2,
)

PATH_PARAMS = SimpleNamespace(
    # -- Path -- #
    max_steps=250,
    # -- Genetic Algorithm -- #
    max_generation=1000,
    pos_size=100,
    population_size=3000,  # pos_size * 30
    mutation_rate=0.3,
    max_stagnation=50,
    stop_threshold=0.0001,
    # -- Fitness weight -- #
    dist_weight=1,
    step_weight=0,
)

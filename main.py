import os
import time
from colorama import Fore, Style, init

import config as cfg
from tos_board import TosBoard

import board_optimize as BO
import path_finding as PF

init(autoreset=True)


def ga_tos(filename):
    for run in range(cfg.GA_FULL_RUNS):
        print(
            f"{Fore.GREEN}{Style.BRIGHT}Starting{Style.RESET_ALL} {filename} run {run+1}...\n"
        )

        start_time = time.time()

        # -- Board Optimization -- #
        bo_log_file = os.path.join(
            cfg.BO_LOG_DIR, f"{filename.split('.')[0]}_{run + 1:02}.txt"
        )
        bo_result_file = os.path.join(
            cfg.BO_RESULT_DIR, f"{filename.split('.')[0]}.txt"
        )

        init_board = TosBoard()
        init_board.init_from_file(os.path.join(cfg.INPUT_FILE_DIR, filename))

        best_board, best_fit, result_log_string = BO.ga_optimize_board(
            init_board, bo_log_file
        )

        bo_time = time.time() - start_time
        result_log_string += f"{bo_time}\n"
        print(
            f"{Fore.YELLOW}{Style.BRIGHT}{filename}{Style.RESET_ALL} run {run+1} "
            f"{Fore.CYAN}{Style.BRIGHT}board optimization{Style.RESET_ALL} result:"
        )
        print("  ", result_log_string)

        # write result log
        with open(bo_log_file, "a") as log_file:
            log_file.write("\n")
            log_file.write(f"Run Time: {bo_time}\n")
            log_file.write(f"Best Fitness: {best_fit}\n\n")
            log_file.write(str(best_board))

        with open(bo_result_file, "a") as result_file:
            result_file.write(result_log_string)

        # -- Path Finding -- #
        pf_log_file = os.path.join(
            cfg.PF_LOG_DIR, f"{filename.split('.')[0]}_{run + 1:02}.txt"
        )
        pf_result_file = os.path.join(
            cfg.PF_RESULT_DIR, f"{filename.split('.')[0]}.txt"
        )

        best_path, best_fit, result_log_string = PF.ga_find_path(
            init_board, best_board, pf_log_file
        )

        pf_time = time.time() - start_time - bo_time
        result_log_string += f"{pf_time}\n"
        print(
            f"{Fore.YELLOW}{Style.BRIGHT}{filename}{Style.RESET_ALL} run {run+1} "
            f"{Fore.MAGENTA}{Style.BRIGHT}path finding{Style.RESET_ALL} result:"
        )
        print("  ", result_log_string)

        achieve_board, achieve_path = best_path.run_path(init_board)

        # write result log
        with open(pf_log_file, "a") as log_file:
            log_file.write("\n")
            log_file.write(f"Run Time: {pf_time}\n")
            log_file.write(f"Best Fitness: {best_fit}\n\n")
            log_file.write(str(achieve_board))
            log_file.write("\n\n")
            log_file.write(str(achieve_path))
            log_file.write("\n\n")
            log_file.write(str(best_path.path))

        with open(pf_result_file, "a") as log_file:
            log_file.write(result_log_string)

        print(
            f"{Fore.RED}{Style.BRIGHT}Finished{Style.RESET_ALL} {filename} run {run+1} in {round(time.time() - start_time, 2)} seconds.\n"
        )


if __name__ == "__main__":
    input_files = [f for f in os.listdir(cfg.INPUT_FILE_DIR) if f.endswith(".txt")]
    input_files.sort()

    for file in input_files:
        ga_tos(file)

    print("Done.")

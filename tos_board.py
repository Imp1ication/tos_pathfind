import random
import copy
import queue
import itertools
from collections import defaultdict
from basic import Move, StoneType, Runestone
import config as cfg


class TosBoard:
    MAX_SCORE = (30 + 10) * 0.25 * 100
    MAX_DENSITY = 6 * 9
    MAX_DIFF = 30
    MAX_DIST = 30 * 4.5

    def __init__(self):
        self.numOfRows = cfg.BOARD_PARAMS.rows
        self.numOfCols = cfg.BOARD_PARAMS.cols
        self.runestones = [
            [Runestone()] * self.numOfCols for _ in range(self.numOfRows)
        ]
        # self.currentPosition = [0, 0]
        # self.previousPosition = self.currentPosition

    def __repr__(self):
        string = ""
        for row in range(self.numOfRows):
            for col in range(self.numOfCols):
                stone = self.runestones[row][col]
                string = string + str(stone)
            string = string + "\n"
        return string

    def __str__(self):
        result = []
        for row in range(self.numOfRows):
            row_str = []
            for col in range(self.numOfCols):
                stone = self.runestones[row][col]
                if stone.type == StoneType.DARK:
                    row_str.append("D ")
                elif stone.type == StoneType.LIGHT:
                    row_str.append("L ")
                elif stone.type == StoneType.WATER:
                    row_str.append("W ")
                elif stone.type == StoneType.FIRE:
                    row_str.append("F ")
                elif stone.type == StoneType.EARTH:
                    row_str.append("E ")
                elif stone.type == StoneType.HEALTH:
                    row_str.append("H ")
                else:
                    row_str.append("N ")
            result.append("".join(row_str).strip())
        return "\n".join(result)

    def init_from_random(self):
        for rowIdx, colIdx in itertools.product(
            range(self.numOfRows), range(self.numOfCols)
        ):
            stone_type = list(StoneType)
            stone_type.remove(StoneType.NONE)

            stone = Runestone(random.choice(stone_type))
            self.runestones[rowIdx][colIdx] = stone
        self.currentPosition = [
            random.randrange(self.numOfRows),
            random.randrange(self.numOfCols),
        ]
        self.previousPosition = self.currentPosition
        self.runestones[self.currentPosition[0]][self.currentPosition[1]].status = "*"

    def init_from_file(self, _filePath):
        with open(_filePath, "r") as fin:
            for lineIdx, line in enumerate(fin):
                tokenList = line.strip().split()
                if len(tokenList) != self.numOfCols:
                    continue
                for tokenIdx, token in enumerate(tokenList):
                    stone = Runestone()
                    if token == "D":
                        stone = Runestone(StoneType.DARK)
                    if token == "L":
                        stone = Runestone(StoneType.LIGHT)
                    if token == "W":
                        stone = Runestone(StoneType.WATER)
                    if token == "F":
                        stone = Runestone(StoneType.FIRE)
                    if token == "E":
                        stone = Runestone(StoneType.EARTH)
                    if token == "H":
                        stone = Runestone(StoneType.HEALTH)
                    self.runestones[lineIdx][tokenIdx] = stone

    def save_to_file(self, file_path):
        with open(file_path, "w") as fout:
            for row in range(self.numOfRows):
                for col in range(self.numOfCols):
                    stone = self.runestones[row][col]
                    if stone.type == StoneType.DARK:
                        fout.write("D ")
                    elif stone.type == StoneType.LIGHT:
                        fout.write("L ")
                    elif stone.type == StoneType.WATER:
                        fout.write("W ")
                    elif stone.type == StoneType.FIRE:
                        fout.write("F ")
                    elif stone.type == StoneType.EARTH:
                        fout.write("E ")
                    elif stone.type == StoneType.HEALTH:
                        fout.write("H ")
                    else:
                        fout.write("N ")
                fout.write("\n")

    # -- Functional Methods --#
    def count_stones_types(self):
        stone_counts = defaultdict(int)
        for row in range(self.numOfRows):
            for col in range(self.numOfCols):
                stone_type = self.runestones[row][col].type
                if stone_type != StoneType.NONE:
                    stone_counts[stone_type] += 1
        return stone_counts

    def shuffle_stones(self):
        stones = [
            stone.type
            for row in self.runestones
            for stone in row
            if stone.type != StoneType.NONE
        ]
        random.shuffle(stones)

        new_board = copy.deepcopy(self)
        idx = 0
        for row in range(new_board.numOfRows):
            for col in range(new_board.numOfCols):
                if new_board.runestones[row][col].type != StoneType.NONE:
                    new_board.runestones[row][col] = Runestone(stones[idx])
                    idx += 1

        return new_board

    def extract_sub_board(self, top_left, bottom_right):
        top_row, left_col = top_left
        bottom_row, right_col = bottom_right

        sub_board = TosBoard()
        sub_board.numOfRows = bottom_row - top_row + 1
        sub_board.numOfCols = right_col - left_col + 1
        sub_board.runestones = [
            self.runestones[row][left_col : right_col + 1]
            for row in range(top_row, bottom_row + 1)
        ]

        return sub_board

    def drop_stones(self):
        stones = self.runestones

        # check if stone dropped
        for colIdx in range(self.numOfCols):
            for rowIdx in range(self.numOfRows - 1, 0, -1):
                if stones[rowIdx][colIdx].type == StoneType.NONE:
                    for r in range(rowIdx - 1, -1, -1):
                        if stones[r][colIdx].type != StoneType.NONE:
                            stones[rowIdx][colIdx] = stones[r][colIdx]
                            stones[r][colIdx] = Runestone()
                            break

    def move_stone(self, start_pos, move):
        # check if input is valid
        if not (
            0 <= start_pos[0] < self.numOfRows and 0 <= start_pos[1] < self.numOfCols
        ):
            # print("Error(move_stone): Invalid start position ", start_pos, ".")
            return False

        new_pos = (
            start_pos[0] + move.value[0],
            start_pos[1] + move.value[1],
        )
        if not (0 <= new_pos[0] < self.numOfRows and 0 <= new_pos[1] < self.numOfCols):
            # print("Error(move_stone): Invalid adjacent stone position ", new_pos, ".")
            return False

        # swap the stones
        temp = self.runestones[start_pos[0]][start_pos[1]]
        self.runestones[start_pos[0]][start_pos[1]] = self.runestones[new_pos[0]][
            new_pos[1]
        ]
        self.runestones[new_pos[0]][new_pos[1]] = temp
        self.runestones[new_pos[0]][new_pos[1]].status = "*"

        return True

    def get_successor_list(self, start_pos, prev_pos):
        successor_list = []

        if not (
            0 <= start_pos[0] < self.numOfRows and 0 <= start_pos[1] < self.numOfCols
        ):
            return []

        for move in Move:
            new_pos = (
                start_pos[0] + move.value[0],
                start_pos[1] + move.value[1],
            )

            if (
                (0 <= new_pos[0] < self.numOfRows)
                and (0 <= new_pos[1] < self.numOfCols)
                and (new_pos != prev_pos)
            ):
                successor_list.append(move)

        return successor_list

    # -- Method to evaluate the board --#
    def eliminate_stones(self):
        # determine if the stone would be removed
        tos_state = copy.deepcopy(self)
        stones = tos_state.runestones
        rm_stones = [[StoneType.NONE] * self.numOfCols for _ in range(self.numOfRows)]
        total_rm_count = 0
        total_combo = 0

        while True:
            rm_count = 0
            combo = 0

            # determine if the stone would be removed
            for rowIdx, colIdx in itertools.product(
                range(self.numOfRows), range(self.numOfCols - 2)
            ):
                if stones[rowIdx][colIdx].type == StoneType.NONE:
                    continue
                stone1 = stones[rowIdx][colIdx]
                stone2 = stones[rowIdx][colIdx + 1]
                stone3 = stones[rowIdx][colIdx + 2]
                if stone1.type == stone2.type == stone3.type:
                    for delta in range(3):
                        rm_stones[rowIdx][colIdx + delta] = stone1.type

            for colIdx, rowIdx in itertools.product(
                range(self.numOfCols), range(self.numOfRows - 2)
            ):
                if stones[rowIdx][colIdx].type == StoneType.NONE:
                    continue
                stone1 = stones[rowIdx][colIdx]
                stone2 = stones[rowIdx + 1][colIdx]
                stone3 = stones[rowIdx + 2][colIdx]
                if stone1.type == stone2.type == stone3.type:
                    for delta in range(3):
                        rm_stones[rowIdx + delta][colIdx] = stone1.type

            # calculate the number of stones removed and update the board
            for rowIdx, colIdx in itertools.product(
                range(self.numOfRows), range(self.numOfCols)
            ):
                if rm_stones[rowIdx][colIdx] != StoneType.NONE:
                    rm_count += 1
                    stones[rowIdx][colIdx] = Runestone()

            if rm_count == 0:
                break

            # calculate the combo, clear removed stones
            for rowIdx, colIdx in itertools.product(
                range(self.numOfRows), range(self.numOfCols)
            ):
                if rm_stones[rowIdx][colIdx] != StoneType.NONE:
                    combo = combo + 1
                    t = rm_stones[rowIdx][colIdx]
                    q = queue.Queue()
                    q.put((rowIdx, colIdx))
                    while not q.empty():
                        (r, c) = q.get()
                        rm_stones[r][c] = StoneType.NONE
                        if r + 1 < self.numOfRows and rm_stones[r + 1][c] == t:
                            q.put((r + 1, c))
                        if c + 1 < self.numOfCols and rm_stones[r][c + 1] == t:
                            q.put((r, c + 1))
                        if r - 1 >= 0 and rm_stones[r - 1][c] == t:
                            q.put((r - 1, c))
                        if c - 1 >= 0 and rm_stones[r][c - 1] == t:
                            q.put((r, c - 1))

            total_rm_count += rm_count
            total_combo += combo

            # check if stone dropped
            tos_state.drop_stones()

            # print(tos_state)
        # print("Total Removed: ", total_rm_count)
        # print("Total Combo: ", total_combo)
        return total_rm_count, total_combo, tos_state

    def calc_score(self, stones, combo):
        return 100 * ((stones + combo) * 0.25) / self.MAX_SCORE

    def calc_stone_density(self):
        stone_positions = defaultdict(list)

        # get all stone positions
        for row in range(self.numOfRows):
            for col in range(self.numOfCols):
                stone = self.runestones[row][col]
                if stone.type is not StoneType.NONE:
                    stone_positions[stone.type].append((row, col))

        # calculate average manhattan distance between stones
        avg_distances = {}

        for stone_type, positions in stone_positions.items():
            total_distance = 0
            num_pairs = 0
            for i in range(len(positions)):
                for j in range(i + 1, len(positions)):
                    x1, y1 = positions[i]
                    x2, y2 = positions[j]
                    distance = abs(x1 - x2) + abs(y1 - y2)
                    total_distance += distance
                    num_pairs += 1
            avg_distance = total_distance / num_pairs if num_pairs > 0 else 1
            avg_distances[stone_type] = avg_distance

        # print average distances
        # for stone_type, avg_distance in avg_distances.items():
        #     print(f"Average distance for {stone_type}: {avg_distance}")

        # add up all average distances
        return sum(avg_distances.values()) / self.MAX_DENSITY

    def calc_board_diff(self, target_board):
        diff = 0
        for row in range(self.numOfRows):
            for col in range(self.numOfCols):
                if (
                    self.runestones[row][col].type
                    != target_board.runestones[row][col].type
                ):
                    diff += 1
        return diff / self.MAX_DIFF

    def calc_board_dist(self, target_board):
        total_dist = 0
        temp_board = copy.deepcopy(target_board.runestones)

        for row, col in itertools.product(range(self.numOfRows), range(self.numOfCols)):
            stone_type = self.runestones[row][col].type

            if stone_type == StoneType.NONE:
                continue

            min_dist = float("inf")
            min_pos = None

            for row2, col2 in itertools.product(
                range(self.numOfRows), range(self.numOfCols)
            ):
                if temp_board[row2][col2].type == stone_type:
                    dist = abs(row - row2) + abs(col - col2)
                    if dist < min_dist:
                        min_dist = dist
                        min_pos = (row2, col2)

            if min_pos is not None:
                total_dist += min_dist
                temp_board[min_pos[0]][min_pos[1]] = Runestone()

        return total_dist / self.MAX_DIST


if __name__ == "__main__":
    board = TosBoard()
    board.init_from_file(cfg.INPUT_FILE_NAME)
    print(board)
